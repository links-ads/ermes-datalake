TEMPORAL FIELDS INDEXING
------------------------

In order to be able to index temporal fields into Solr the XML schema must be modified:

1. Add the following dynamicField into the schema.xml file used by CKAN:

	<dynamicField name="extras_temporal_extent*" type="date" indexed="true" stored="true" multiValued="false"/>
		
3. Restart SOLR:

	/etc/init.d/solr restart

4. Restart CKAN:

	service supervisord restart
	
4. Reharvest data in order to apply new names for temporal fields. 

5. If you need to reindex, from the 'ckan' user run this command:

		paster --plugin=ckan search-index rebuild  -c /etc/ckan/default/production.ini