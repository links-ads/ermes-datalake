#!/bin/env bash

set -e

config="${APP_DIR}/ckan.ini"

# Set up the Secret key used by Beaker and Flask
# This can be overriden using a CKAN___BEAKER__SESSION__SECRET env var
if grep -E "beaker.session.secret ?= ?$" ckan.ini
then
    echo "Setting beaker.session.secret in ini file"
    ckan config-tool ${config} "beaker.session.secret=$(python3 -c 'import secrets; print(secrets.token_urlsafe())')"
    ckan config-tool ${config} "WTF_CSRF_SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_urlsafe())')"
    JWT_SECRET=$(python3 -c 'import secrets; print("string:" + secrets.token_urlsafe())')
    ckan config-tool ${config} "api_token.jwt.encode.secret=$JWT_SECRET"
    ckan config-tool ${config} "api_token.jwt.decode.secret=$JWT_SECRET"
fi

ckan --config ${config} db init

ckan config-tool ${config} -s "app:main" \
        "ckan.site_title = ${PROJECT_NAME} Data Lake" \
        "ckan.site_description = Data lake tool for ${PROJECT_NAME} project." \
        "ckan.site_logo = /ckan-logo.png" \
        "ckan.favicon = /ckan.ico" \
        "ckan.site_intro_text = ### $PROJECT_NAME data repository" \
        "ckan.site_about = This is a datalake catalog deployed by LINKS Foundation to support ${PROJECT_NAME} data." \
        "sqlalchemy.url = ${CKAN_SQLALCHEMY_URL}" \
        "ckan.site_url = ${CKAN_SITE_URL}" \
        "ckan.auth.user_create_organizations = true" \
        "solr_url=${CKAN_SOLR_URL}" \
        "ckan.redis.url = ${CKAN_REDIS_URL}" \
        "ckan.cors.origin_allow_all = true" \
        "ckan.plugins = oauth2 notify theme datesearch datatype authcheck stats text_view image_view recline_view spatial_metadata spatial_query resource_proxy geo_view geojson_view shp_view scheming_datasets cloudstorage"  \
        "scheming.presets = ckanext.scheming:presets.json" \
        "scheming.ontology_schema = ckanext.scheming:${SCHEMING_ONTOLOGY_FILE}" \
        "scheming.dataset_schemas = ckanext.scheming:ckan_dataset_INSPIRE.json" \
        "scheming.dataset_fallback = false" \
        "ckan.locale_default = en" \
        "ckan.views.default_views = image_view text_view recline_view geo_view geojson_view shp_view" \
        "ckan.max_resource_size = 100" \
        "ckan.spatial.srid = 4326" \
        "ckanext.spatial.search_backend = solr-spatial-field" \
        "ckan.spatial.validator.profiles = iso19193eden" \
        "ckanext.cloudstorage.driver =AZURE_BLOBS" \
        "ckanext.cloudstorage.container_name = ${AZURE_BLOB_CONTAINER_NAME}" \
        "ckanext.cloudstorage.driver_options = {'key': '${AZURE_BLOB_ACCOUNT_NAME}', 'secret': '${AZURE_BLOB_SECRET}', 'secure':True}" \
        "ckanext.cloudstorage.use_secure_urls = True" \
        "ckan.oauth2.register_url = https://${OAUTH_SERVICE}/oauth2/register" \
        "ckan.oauth2.reset_url = https://${OAUTH_SERVICE}/users/password/new" \
        "ckan.oauth2.edit_url = https://${OAUTH_SERVICE}/settings" \
        "ckan.oauth2.authorization_endpoint = https://${OAUTH_SERVICE}/oauth2/authorize" \
        "ckan.oauth2.token_endpoint = https://${OAUTH_SERVICE}/oauth2/token" \
        "ckan.oauth2.profile_api_url = https://${OAUTH_SERVICE}/oauth2/userinfo" \
        "ckan.oauth2.logout_url = ${CKAN_SITE_URL}" \
        "ckan.oauth2.logout_next_name = user" \
        "ckan.oauth2.client_id = ${OAUTH_CLIENT_ID}" \
        "ckan.oauth2.client_secret = ${OAUTH_CLIENT_SECRET}" \
        "ckan.oauth2.scope = openid offline_access" \
        "ckan.oauth2.profile_api_user_field = preferred_username" \
        "ckan.oauth2.profile_api_mail_field = preferred_username" \
        "ckan.oauth2.authorization_header = Authorization" \
        "ckan.notify.mq.port = ${RABBIT_NOTIFY_PORT}" \
        "ckan.notify.mq.userid = ${RABBIT_NOTIFY_USERID}" \
        "ckan.notify.mq.password = ${RABBIT_NOTIFY_PASSWORD}" \
        "ckan.notify.mq.hostname = ${RABBIT_NOTIFY_HOSTNAME}" \
        "ckan.notify.mq.vhost = ${RABBIT_VHOST}" \
        "ckan.notify.mq.exchange_name = ${RABBIT_EXCHANGE}" \
        "ckan.notify.mq.queue_name = ${RABBIT_QUEUE}" \
        "ckan.notify.mq.app_id = ${RABBIT_NOTIFY_APPID}" \
        "ckan.notify.mq.rk_prefix = ${RABBIT_NOTIFY_ROUTINGKEY_PREFIX}"


# Initializes the database
ckan --config ${config} spatial initdb

exec "$@"
