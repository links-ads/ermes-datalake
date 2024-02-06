# example of context:
# context =  {
# 'auth_user_obj': <
#     User id=9acbc718-1e2d-4053-a145-18ea4233ff16
#     name=admin-dev
#     openid=None
#     password=None
#     fullname=None
#     email=admin@shelter-project-dev.cloud
#     apikey=apikey
#     created=2020-11-10 15:25:41.681855
#     reset_key=None
#     about=None
#     activity_streams_email_notifications=False
#     sysadmin=True
#     state=active>,
# '__auth_user_obj_checked': True,
# 'session': <sqlalchemy.orm.scoping.scoped_session object at 0x7ff3bece9750>,
# 'user': u'admin-dev',
# '__auth_audit': [],
# 'model': <module 'ckan.model' from '/usr/lib/ckan/default/src/ckan/ckan/model/__init__.pyc'>,
# 'api_version': 3}


# -------------------------------------------------------------------------------------------------------

import ckan.plugins as plugins
import ckan.logic as logic
import ckan.lib.base as base
import ckan.plugins.toolkit as toolkit
import ckan.lib.helpers as h
import logging
from ckan.common import _, g
from ckan.logic.action.get import package_show, resource_show
from ckan.logic.action.update import package_update
import ckan.logic.auth.update as auth_update
import ckan.logic.auth.delete as auth_delete

log = logging.getLogger(__name__)

from flask import render_template as flask_render_template, abort as flask_abort

abort = flask_abort
NotFound = logic.NotFound
NotAuthorized = logic.NotAuthorized


def additional_check(context, data_dict, metadata=False):
    # save context information (current user data)
    user_dict = context.get("auth_user_obj").__dict__
    log.info("USER_OBJ: %r", user_dict)
    user_email = user_dict["email"]
    is_sysadmin = user_dict["sysadmin"]

    # get the metadata to retrieve author_email
    # two cases:
    # - the data_dict refers to a resource
    # - the data_dict refers to a metadata
    id_data = {"id": data_dict["id"]}
    if not metadata:
        try:
            # first case: id_data is the resource id. then get the package id
            log.info("querying for resource with id: %r", id_data)
            pkg_dict = resource_show(context, id_data)
            id_data["id"] = pkg_dict["package_id"]
        except NotAuthorized:
            # raise NotAuthorized(('User %r not authorized to view %s') % (g.user, id))
            # abort(403)
            # base.abort(403, ('User %r not authorized to view %s') % (g.user, id))
            # toolkit.abort(403, ('User %r not authorized to view %s') % (g.user, id))
            return (False, ("User %r not authorized to view %s") % (g.user, id))
        except NotFound:
            log.debug("Not Found")
            return (False, ("no resource found with id %r, try to get the metadata") % (id_data))
    else:
        try:
            # second case: id_data is the metadata id
            log.info("querying for metadata id: %r", id_data)
            pkg_dict = package_show(context, id_data)
            author_email = pkg_dict["author_email"]
            log.info("Package author: %r", author_email)
            author_email = pkg_dict["author_email"]
        except NotFound:
            # raise NotFound('Dataset not found')
            # abort(404)
            # base.abort(404, ('Dataset not found'))
            # toolkit.abort(404, 'Dataset not found')
            return (False, "Dataset not found")
        except NotAuthorized:
            # raise NotAuthorized(('User %r not authorized to view %s') % (g.user, id))
            # abort(403)
            # toolkit.abort(403, ('User %r not authorized to view %s') % (g.user, id))
            # base.abort(403, ('User %r not authorized to view %s') % (g.user, id))
            return (False, ("User %r not authorized to view %s") % (g.user, id))

        # compare metadata author to the current user
        is_author = user_email == author_email
        is_author_null = author_email is None

        try:
            # additional checks (at least one must be true):
            # - the author is the same person who uploaded the metadata
            # - the current user is sysadmin
            # - the metadata author is null (then everyone can edit it)
            log.info("Check permission 2/2...")
            log.info("is_sysadmin:%r", is_sysadmin)
            log.info("is_author:%r", is_author)
            log.info("is_author_null:%r", is_author_null)
            if is_sysadmin or is_author or is_author_null:
                log.debug("Permission granted")
            else:
                return (False, "Not Authorized")
        except NotFound:
            return (False, "Dataset not found")
        except NotAuthorized:
            # raise NotAuthorized(('User %r not authorized to edit metedata with id:%s') % (g.user, id_data['id']))
            # abort(403)
            return (False, ("User %r not authorized to edit metedata with id:%s") % (g.user, id_data["id"]))
            # base.abort(403, ('User %r not authorized to edit metedata with id:%s') % (g.user, id_data['id']))
    return (True, "")


def package_update(context, data_dict):
    log.info("UPDATING METADATA: %r", data_dict)

    # original check
    log.info("Check permission 1/2...")
    authorization = auth_update.package_update(context, data_dict)
    success = authorization["success"]
    msg = ""

    # additional checks
    if success and data_dict is not None:
        log.info("Check permission 2/2...")
        (success, msg) = additional_check(context, data_dict, metadata=True)
    log.debug(f"success:{success} --> {type(success)}--- {not success}")
    if not success:
        return {"success": False, "msg": msg}
    else:
        return {"success": True}


def package_delete(context, data_dict):
    log.info("DELETING METADATA: %r", data_dict)

    # original check
    log.info("Check permission 1/2...")
    authorization = auth_delete.package_delete(context, data_dict)
    success = authorization["success"]
    msg = ""

    # additional checks
    if success and data_dict is not None:
        (success, msg) = additional_check(context, data_dict, metadata=True)
    log.debug(f"success:{success} --> {type(success)}--- {not success}")
    if not success:
        return {"success": False, "msg": msg}
    else:
        return {"success": True}


def resource_delete(context, data_dict):
    log.info("DELETING Resource: %r", data_dict)

    # original check
    log.info("Check permission 1/2...")
    authorization = auth_delete.resource_delete(context, data_dict)
    success = authorization["success"]
    msg = ""

    # additional checks
    if success and data_dict is not None:
        (success, msg) = additional_check(context, data_dict, metadata=False)
    log.debug(f"success:{success} --> {type(success)} --- {not success}")

    if not success:
        return {"success": False, "msg": msg}
    else:
        return {"success": True}


def resource_update(context, data_dict):
    log.info("UPDATING Resource: %r", data_dict)

    # original check
    log.info("Check permission 1/2...")
    authorization = auth_update.resource_update(context, data_dict)
    success = authorization["success"]
    msg = ""

    # additional checks
    if success and data_dict is not None:
        (success, msg) = additional_check(context, data_dict, metadata=False)

    log.debug(f"success:{success} --> {type(success)} --- {not success}")
    if not success:
        return {"success": False, "msg": msg}
    else:
        return {"success": True}


class authcheckPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IAuthFunctions, inherit=True)

    # IAuthFunctions
    def get_auth_functions(self):
        return {
            "package_delete": package_delete,
            "package_update": package_update,
            "resource_delete": resource_delete,
            "resource_update": resource_update,
        }
