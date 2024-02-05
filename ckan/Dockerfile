FROM ckan/ckan-base:2.9.10

LABEL maintainer='federico.oldani@linksfoundation.com'

# Set timezone
ARG TZ
RUN echo $TZ > /etc/timezone
RUN cp /usr/share/zoneinfo/$TZ /etc/localtime


RUN apk update && apk add postgresql-client geos-dev python3 python3-dev py3-pip proj proj-dev proj-util 
RUN apk add postgresql-client postgis postgresql

RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
RUN python3 get-pip.py --force-reinstall
#         libxslt-dev \
#         libgeos-dev

# # install gdal
# Install GDAL dependencies
# RUN echo "@edge http://dl-cdn.alpinelinux.org/alpine/edge/main" >> /etc/apk/repositories
# RUN echo "@edge-testing http://dl-cdn.alpinelinux.org/alpine/edge/testing" >> /etc/apk/repositories

# RUN apk update && \
#   apk --no-cache --update upgrade musl && \
#   apk add --upgrade --force-overwrite apk-tools@edge && \
#   apk add --update --force-overwrite "proj-dev@edge-testing" "geos-dev@edge-testing" "gdal-dev@edge-testing" && \
#   rm -rf /var/cache/apk/*

# RUN apk info proj-dev geos-dev gdal-dev
# RUN pip3 install GDAL==$(gdal-config --version) --global-option=build_ext --global-option="-I/usr/include/gdal"

# RUN pip3 install setuptools
# RUN pip3 install wheel
# RUN pip3 install pyproj==2.6.1

# Install ckanext-spatial
RUN apk add --no-cache gdal
RUN apk add geos-dev
RUN apk add proj-dev
RUN apk add proj-util
RUN mkdir "${APP_DIR}/src/ckanext-spatial/"
ADD ./ckanext-spatial/ ${APP_DIR}/src/ckanext-spatial/
RUN pip3 install -e "${APP_DIR}/src/ckanext-spatial/"
RUN pip3 install cython==0.29.36
RUN pip3 install --no-use-pep517 pyproj==2.6.1
RUN pip3 install -r "${APP_DIR}/src/ckanext-spatial/pip3-requirements.txt"
# WORKDIR "${APP_DIR}/src"
# RUN pip3 install -U pip setuptools

# RUN pip3 install -e "git+https://github.com/smellman/ckanext-spatial.git@dev-py3#egg=ckanext-spatial"
# RUN pip3 install -r "${APP_DIR}/src/ckanext-spatial/pip3-requirements.txt"

# Install hidegroups
RUN mkdir "${APP_DIR}/src/ckanext-hidegroups/"
ADD ./ckanext-hidegroups/ ${APP_DIR}/src/ckanext-hidegroups/
RUN pip3 install -e "${APP_DIR}/src/ckanext-hidegroups/"

# Install theme
RUN mkdir "${APP_DIR}/src/ckanext-theme/"
ADD ./ckanext-theme/ ${APP_DIR}/src/ckanext-theme/
RUN pip3 install -e "${APP_DIR}/src/ckanext-theme/"

# Install ckanext-geoview
RUN mkdir "${APP_DIR}/src/ckanext-geoview/"
ADD ./ckanext-geoview/ ${APP_DIR}/src/ckanext-geoview/
RUN pip3 install -e "${APP_DIR}/src/ckanext-geoview/"
RUN pip3 install -r "${APP_DIR}/src/ckanext-geoview/pip-requirements.txt"

# Install ckanext-datesearch
RUN mkdir "${APP_DIR}/src/ckanext-datesearch/"
ADD ./ckanext-datesearch/ ${APP_DIR}/src/ckanext-datesearch/
RUN pip3 install -e "${APP_DIR}/src/ckanext-datesearch/"

# Install ckanext-cloudstorage
RUN mkdir "${APP_DIR}/src/ckanext-cloudstorage/"
ADD ./ckanext-cloudstorage-py3/ ${APP_DIR}/src/ckanext-cloudstorage/
RUN pip3 install -r "${APP_DIR}/src/ckanext-cloudstorage/requirements.txt"
RUN pip3 install -e "${APP_DIR}/src/ckanext-cloudstorage/"

# Install ckanext-notify
RUN mkdir "${APP_DIR}/src/ckanext-notify/"
ADD ./ckanext-notify/ ${APP_DIR}/src/ckanext-notify/
RUN pip3 install -r "${APP_DIR}/src/ckanext-notify/requirements.txt"
RUN pip3 install -e "${APP_DIR}/src/ckanext-notify/"

# Install ckanext-authcheck
RUN mkdir "${APP_DIR}/src/ckanext-authcheck/"
ADD ./ckanext-authcheck/ ${APP_DIR}/src/ckanext-authcheck/
RUN pip3 install -e "${APP_DIR}/src/ckanext-authcheck/"

# # Install ckanext-openapi
# RUN mkdir "${APP_DIR}/src/ckanext-openapiviewer/"
# ADD ./ckanext-openapiviewer/ ${APP_DIR}/src/ckanext-openapiviewer/
# RUN pip3 install -e "${APP_DIR}/src/ckanext-openapiviewer/"

# Install ckanext-datatype
RUN mkdir "${APP_DIR}/src/ckanext-datatype/"
ADD ./ckanext-datatype/ ${APP_DIR}/src/ckanext-datatype/
RUN pip3 install -e "${APP_DIR}/src/ckanext-datatype/"

# Install ckanext-oauth2
RUN mkdir "${APP_DIR}/src/ckanext-oauth2/"
ADD ./ckanext-oauth2/ ${APP_DIR}/src/ckanext-oauth2/
RUN pip3 install -r "${APP_DIR}/src/ckanext-oauth2/requirements.txt"
RUN pip3 install -e "${APP_DIR}/src/ckanext-oauth2/"

# Install ckanext-scheming
RUN mkdir "${APP_DIR}/src/ckanext-scheming/"
ADD ./ckanext-scheming/ ${APP_DIR}/src/ckanext-scheming/
RUN pip3 install -e "${APP_DIR}/src/ckanext-scheming/"
# RUN pip3 install -r "${APP_DIR}/src/ckanext-scheming/requirements.txt"

# # Copy various data and initialization files
# RUN mkdir "${APP_DIR}/data/"
# ADD ./data ${APP_DIR}/data/

# Link to who.ini
# RUN ln -s "${APP_DIR}/src/ckan/ckan/config/who.ini" "${APP_DIR}/who.ini"

# Setup entrypoint
# COPY ./ckan-entrypoint.sh /
# RUN chmod +x /ckan-entrypoint.sh
# ENTRYPOINT ["/ckan-entrypoint.sh"]

# # Set default user and work directory
# # USER ckan

# EXPOSE 5000

COPY docker-entrypoint.d/* /docker-entrypoint.d/
COPY start_ckan.sh ${APP_DIR}
COPY uwsgi.ini ${APP_DIR}
RUN chmod +x ${APP_DIR}/start_ckan.sh
