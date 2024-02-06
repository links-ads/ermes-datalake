# Data Catalog - CKAN

[CKAN](https://ckan.org/) is a powerful data management system that makes data accessible – by providing tools to streamline publishing, sharing, finding and using data. This project provides everything you need to run CKAN plus a set of extensions to add functionalities.

## Tools references

The tools used in this repository are

* [Docker](https://www.docker.com/)

## Main components

* **CKAN** version 2.9 with the extensions listed at the end of this document (see [ckan](https://github.com/ckan/ckan)). This is the main framework and it is based on [Flask](https://flask.palletsprojects.com/en/1.1.x/).

* **Solr** version 6.2 packaged for CKAN and with some customizations (see [solr](https://hub.docker.com/r/ckan/solr)). Solr provides distributed indexing, replication and load-balanced querying, automated failover and recovery, centralized configuration and more.

* **PostgreSQL+PostGIS** PostgreSQL version 12 with PostGIS 3.4 (see [postgis](https://hub.docker.com/r/postgis/postgis)). PostGIS is an open source software program that adds support for geographic objects to the PostgreSQL object-relational database. This component is the db where all the information will be stored.

* **Redis** pulled in as a dependency from its [official Docker repository](https://hub.docker.com/_/redis). Redis is an open source (BSD licensed), in-memory data structure store, used as a database, cache, and message broker.

## Plugins references
The base version of Ckan has been enhanced with several extensions in order to add functionalities: 

* **[spatial](https://github.com/ckan/ckanext-spatial)** add a spatial field on the default CKAN dataset schema, it uses PostGIS as the backend and allows to perform spatial queries and to display the dataset extent on the frontend.
* **datesearch**. Forked and modified from [datesearch](https://github.com/geosolutions-it/ckanext-datesearch/tree/c007). It adds start/end validity date of metadata and it allows to search on those fields.
* **[oauth2](https://github.com/conwetlab/ckanext-oauth2)** It allows integration with FusionAuth or any other OAuth2.0 protocol
* **[geoview](https://github.com/ckan/ckanext-geoview)** It contains view plugins to display geospatial files and services in CKAN
* **[scheming](https://github.com/ckan/ckanext-scheming)** It allows to create new metadata fields and validate the entries. It currently implements [INSPIRE metadata](https://inspire.ec.europa.eu/metadata/6541).
* **[cloudstorage](https://github.com/TkTech/ckanext-cloudstorage)** It allows to use the main cloud storage services for storing data. It is currently set to use Azure Blob Storage. 
* **notify** - It allows to send a notification to a [rabbitMQ](https://www.rabbitmq.com/) queue everytime a dataset is updated/created/deleted
* **theme** - allows theme customization
* **hidegroups** - hides 'group' from the front end (because useless for this purpose)
* **authcheck** - Check if the user has the permission to modify / delete a certain dataset (Only the creator can modify/delete its own dataset)
* **notify** - Listen for modification on resources and send notification to a rabbit queue
* **datatype** - Collect datatype ids from resources and put the list in the metadata description


Each plugin can be modified and adapted to new scopes, and new plugins can be develop to add other functionalities! In [this repository](https://extensions.ckan.org/) a plenty of plugins are published.

## How to run

In this repository, CKAN and its related tools are redistributed as a set of Docker containers interacting with one each other.

The `docker-compose.yml` file are in the root of this repository, in each component's folder the `Dockerfile` describe how to build the container.

Set the environment variables through .env file (follow the configuration in .env.example file). If you are not using all the plugins described above, you may not need all the variables.

Accordingly to the Dockerfile, after the installation of CKAN and the plugins, the scripts in folder `ckan/docker-entrypoint.d` will be run. File `ckan-entrypoint.sh` contains all the modification needed to enable and configure the plugins.

To run the containers:

1. Clone this repository
2. `cd datacatalog`
3. `make up TARGET=dev|prod ARGS=--build` [dev enables CKAN `DEBUG` logs and automatic reload of CKAN instance upon any code change]

## Credentials
After a while you can open the CKAN home [http://localhost:5001](http://localhost:5001) and login with the credentials set in the `env/.env` file. If you are using the plugin oauth2 the login page will be the one speciefied in the env file.

### OAUTH2 plugin
The plugin allows to use oauth2 server to authenticate users. The CKAN istance will create in any case a internal table with its users, and it is filled at the first login via web interface by the user. For this reason, once you created the user in the oauth2 portal, you need to login via web interface before using the API. Otherwise it will not work.

To test this plugin in local we advice to use [ngrok](https://ngrok.com/) to simulate SSL on localhost.


### Make a user sysadmin
1. Enter in the ckan container shell with the command `docker exec -it [container_id] sh`
2. run the command `ckan -c /srv/app/ckan.ini sysadmin add [username]`

## Customize the metadata
To customize the metadata (currently compliant to INSPIRE Metadata directive) define your own schema as described in the [official plugin's guide](https://github.com/ckan/ckanext-scheming), save the file in `ckan/ckanext-scheming/ckanext/scheming/` and specify the filename in the field "scheming.dataset_schemas" in the file `ckan/docker-entrypoint.d/ckan-entrypoint.sh`

## Add a controlled vocabulary (ONTOLOGY) for tags or keywords
Currently the ontology used for tags is the one you find at `ckan/ckanext-scheming/ckanext/scheming/ontology.json`. If you want to add your own ontology you need to modify the file respecting the format:
- change "ontology" with a new name (example 'ontology_v2')
- change the tags list
To make your ontology effective, you need to change the metadata schema: in the field `keyword_KeywordValue` change the validator `convert_strings_to_tags(ontology)` into `convert_strings_to_tags([name of your ontology])`. 

More information [here](https://github.com/smallmedia/iod-ckan/issues/20).

## Database Backup
1. Discover the container id of the db with `docker ps` 
2. Backup db with the following command `docker exec -t [container_id] pg_dumpall -U ckan -c > dump.sql`

## Database Restore
0. Clean the existing db. Enter in the ckan container shell and run `ckan -c ckan.ini db clean`
1. Restore db with the following command  `cat dump.sql | docker exec -i [container_id] psql -U ckan`
2. Finally, you need to rebuild the solr index. Enter in the ckan container shell and run `ckan search-index rebuild`

## TROUBLESHOOTING
### API don't work
- check the if the access token got through oauth2 authentication is valid
- if API fails with 409 error, it is possibly a validation error in the request, ckan should return the field for which the error occurred
- if no results are shown, it is probably becasue the authentication is wrong (indeed, private datasets are shown only to authenticated users)

### Map preview doesn't work
Yes, this is a known issue. The plugin has been updated with a different type of map but the latest version of it is not compatible with this dockerized version of ckan. Waiting for the fix.
[Here](https://github.com/ckan/ckanext-spatial/issues/317) more info for the solution.
