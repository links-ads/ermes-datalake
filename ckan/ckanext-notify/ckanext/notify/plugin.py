import os
import logging
import ssl
import pika
from ckan.plugins import implements, SingletonPlugin
from ckan.plugins import IResourceController, IPackageController
from ckan.lib.base import config
from ckan.logic.action.get import package_show
import ckan.plugins as p
from json import JSONEncoder
import datetime
import json
import validators
from enum import Enum


log = logging.getLogger(__name__)


class DeliveryMode(Enum):
    TRANSIENT = 1
    PERSISTENT = 2


# subclass JSONEncoder
class DateTimeEncoder(JSONEncoder):
    # Override the default method
    def default(self, obj):
        if isinstance(obj, (datetime.date, datetime.datetime)):
            return obj.isoformat()


class notifyPlugin(SingletonPlugin):
    """
    This plugin is used to send a notification on a rabbit bus queue for each resource modified.
    In general is sufficient trigger after_update, after_create and before_delete for resources.
    BUT in case one deletes the whole package, then i need to iterate over the resources contained
    in that package and send a notification for each package
    """

    implements(IResourceController, inherit=True)
    implements(IPackageController, inherit=True)

    def __init__(self, name=None):
        self.port = int(config.get("ckan.notify.mq.port"))
        self.userid = config.get("ckan.notify.mq.userid")
        self.password = config.get("ckan.notify.mq.password")
        self.hostname = config.get("ckan.notify.mq.hostname")
        self.vhost = config.get("ckan.notify.mq.vhost")
        self.exchange_name = config.get("ckan.notify.mq.exchange_name")
        self.queue_name = config.get("ckan.notify.mq.queue_name")
        self.datacatalog_host = config.get("ckan.site_url")
        self.app_id = config.get("ckan.notify.mq.app_id")
        self.rk_prefix = config.get("ckan.notify.mq.rk_prefix")
        self.content_type = "application/json"
        self.encoding = "utf-8"
        self.credentials = pika.PlainCredentials(self.userid, self.password)
        self.ssl_options = pika.SSLOptions(ssl.create_default_context(), self.hostname)
        self.parameters = pika.ConnectionParameters(
            host=self.hostname,
            virtual_host=self.vhost,
            credentials=self.credentials,
            port=self.port,
            ssl_options=self.ssl_options,
        )
        log.debug("pika connection using %s" % self.parameters)

    def send_notification(self, data_id, output, req_code=None):
        connection = pika.BlockingConnection(self.parameters)
        channel = connection.channel()
        channel.queue_bind(exchange=self.exchange_name, queue=self.queue_name, routing_key=f"{self.rk_prefix}.#")
        properties = pika.BasicProperties(
            content_type="application/json", content_encoding="utf-8", **self.get_properties()
        )

        routing_key = f"{self.rk_prefix}.{data_id}"
        if req_code:
            routing_key = f"{routing_key}.{req_code}"

        channel.basic_publish(exchange=self.exchange_name, routing_key=routing_key, body=output, properties=properties)
        channel.close()
        connection.close()

    def get_req_code(self, dataset_dict):
        req_code = None
        if dataset_dict.get("external_attributes"):
            ext_attr = dataset_dict.get("external_attributes")
            req_code = ext_attr.get("request_code", None)
        return req_code

    def build_dict(self, pkg_dict, ix, action, dataset_dict):
        # retrieve
        if dataset_dict.get("spatial", "None"):
            geometry = json.loads(dataset_dict.get("spatial", "None"))
        else:
            geometry = ""

        req_code = self.get_req_code(dataset_dict)
        if not req_code:
            req_code = ""

        url = pkg_dict.get("url")
        if not validators.url(url):
            url = f"{self.datacatalog_host}/dataset/{dataset_dict.get('id','None')}/resource/{pkg_dict.get('id', 'None')}/download/{url}"

        output_dict = {
            "metadata_id": dataset_dict.get("id", "None"),
            "id": pkg_dict.get("id", "None"),
            "datatype_id": ix,
            "type": action,
            "creation_date": dataset_dict.get("temporalReference_dateOfCreation", "None"),
            "start_date": pkg_dict.get("file_date_start", "None"),
            "end_date": pkg_dict.get("file_date_end", "None"),
            "geometry": geometry,
            "request_code": req_code,
            "url": url,
        }
        return json.dumps(output_dict, cls=DateTimeEncoder)

    def get_properties(self):
        return {"delivery_mode": DeliveryMode.PERSISTENT.value, "app_id": self.app_id, "user_id": self.userid}

    def after_update(self, context, pkg_dict):
        # check if it is triggered by resource or by package,
        # we use only resource trigger and in resource the pkg_dict contains a list
        log.debug("Updated! Full pack: %r", pkg_dict)
        datatype_id = pkg_dict.get("datatype_resource", None)
        if datatype_id:
            dataset_dict = package_show(context, {"id": pkg_dict["package_id"]})
            output = self.build_dict(pkg_dict, datatype_id, "update", dataset_dict)
            req_code = self.get_req_code(dataset_dict)
            self.send_notification(datatype_id, output, req_code)

    def after_create(self, context, pkg_dict):
        # check if it is triggered by resource or by package,
        # we use only resource trigger and in resource the pkg_dict contains a list
        datatype_id = pkg_dict.get("datatype_resource", None)
        # log.debug("Created! Full pack: %r", pkg_dict)
        if datatype_id:
            dataset_dict = package_show(context, {"id": pkg_dict["package_id"]})
            output = self.build_dict(pkg_dict, datatype_id, "create", dataset_dict)
            req_code = self.get_req_code(dataset_dict)
            self.send_notification(datatype_id, output, req_code)

    def before_delete(self, context, res, pkg_dict):
        # check if it is triggered by resource or by package,
        # we use only resource trigger and in resource the pkg_dict contains a list
        # log.debug("Deleting Full pack: %r", pkg_dict)
        if isinstance(pkg_dict, list):
            # if deleting the resource, send the notification
            for res_dict in pkg_dict:
                if res_dict["id"] == res["id"]:
                    pkg = res_dict

            # log.debug("Deleting resources: %r", pkg)
            dataset_dict = package_show(context, {"id": pkg["package_id"]})

            datatype_id = pkg.get("datatype_resource", None)
            if datatype_id:
                output = self.build_dict(pkg, datatype_id, "delete", dataset_dict)
                req_code = self.get_req_code(dataset_dict)
                self.send_notification(datatype_id, output, req_code)

    def after_delete(self, context, pkg_dict):
        # check if it is triggered by resource or by package,
        # we use only package trigger and in package the pkg_dict
        # does not contain a list
        if not isinstance(pkg_dict, list):
            log.debug("Deleting ad Full pack: %r", pkg_dict)
            if pkg_dict.get("id", None):
                dataset_dict = package_show(context, {"id": pkg_dict["id"]})
                # if deleting a package, send a notification for each resource contained
                log.debug("Deleting ad Full pack dataset del: %r", dataset_dict)
                for res in dataset_dict.get("resources"):
                    datatype_id = res["datatype_resource"]
                    output = self.build_dict(res, datatype_id, "delete", dataset_dict)
                    req_code = self.get_req_code(dataset_dict)
                    self.send_notification(datatype_id, output, req_code)
