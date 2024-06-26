import os
from logging import getLogger

from ckan.plugins import implements, SingletonPlugin, IConfigurer
import ckan.plugins.toolkit as toolkit

log = getLogger(__name__)


class themePlugin(SingletonPlugin):

    implements(IConfigurer)

    def update_config(self, config):

        # Add this plugin's templates dir to CKAN's extra_template_paths, so
        # that CKAN will use this plugin's custom templates.
        toolkit.add_template_directory(config, "templates")

        # Add this plugin's public dir to CKAN's extra_public_paths, so
        # that CKAN will use this plugin's custom static files.
        toolkit.add_public_directory(config, "public")
