import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
import logging
import json
from ckan.logic.action.get import package_show
from ckan.logic.action.patch import package_patch
from itertools import count


log = logging.getLogger(__name__)


class DatatypePlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IPackageController, inherit=True)
    plugins.implements(plugins.IResourceController, inherit=True)

    def update_config(self, config):
        toolkit.add_template_directory(config, "templates")
        toolkit.add_resource("fanstatic", "ckanext-datetype")

    # def before_index(self, pkg_dict):
    #     dt = pkg_dict['datatype_id']
    #     if isinstance(dt, str):
    #         tags = [tag.strip() \
    #                 for tag in dt.split(',') \
    #                 if tag.strip()]
    #     else:
    #         tags = dt

    #     # dt_list = []
    #     # for tag in tags:
    #     #     dt_list.append(tag)

    #     pkg_dict['datatype_id'] = tags
    #     # log.debug('DATATYPE data after: {0}'.format(pkg_dict))
    #     return pkg_dict

    # Resource Controller:
    # genereta a new datatype_id list every time a new resource is uploaded or updated or deleted
    def regenerate_datatype_id(self, context, resource):
        log.debug(f"regenerating datatype_ids...")
        if resource.get("datatype_resource", None) is not None:
            # log.debug(f'resource: {resource}')
            pkg_dict = package_show(context, {"id": resource["package_id"]})
            # log.debug(f'pkg: {pkg_dict}')
            dt_list = []
            for res in pkg_dict.get("resources"):
                datatype_resource = res["datatype_resource"]
                if isinstance(datatype_resource, str):
                    datatype_resource = [tag.strip() for tag in datatype_resource.split(",") if tag.strip()]
                    dt_list = dt_list + datatype_resource

            dt_set = set(dt_list)  # remove duplicates
            dt_list = ", ".join(list(dt_set))

            data_dict = {"id": resource["package_id"], "datatype_id": dt_list}
            # log.debug(f'data dict: {data_dict}')
            package_patch(context, data_dict)

    # After create a new resource the list of the datatypeid is regenerated
    def after_create(self, context, resource):
        self.regenerate_datatype_id(context, resource)

    # After update a new resource the list of the datatypeid is regenerated
    def after_update(self, context, resource):
        self.regenerate_datatype_id(context, resource)

    # After delete a new resource the list of the datatypeid is regenerated
    def after_delete(self, context, resource):
        # In after delete action, resource is a list of resources
        if type(resource) is list:
            for res in resource:
                self.regenerate_datatype_id(context, res)
