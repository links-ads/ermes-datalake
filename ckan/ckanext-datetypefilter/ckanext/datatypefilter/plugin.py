import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
import logging

log = logging.getLogger(__name__)


class DateSearchPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IPackageController, inherit=True)

    def update_config(self, config):
        toolkit.add_template_directory(config, "templates")

        log.info("datesearch ADDING ASSETS")
        toolkit.add_public_directory(config, "fanstatic")
        toolkit.add_resource("fanstatic", "datesearch_wg")

    def before_search(self, search_params):

        log.info("datesearch " + str(search_params))

        extras = search_params.get("extras")
        if not extras:
            log.info("datesearch: There are no extras in the search params, so do nothing")
            # There are no extras in the search params, so do nothing.
            # return search_params
        start_date = extras.get("ext_startdate")
        end_date = extras.get("ext_enddate")
        if not start_date or not end_date:
            log.info("datesearch: The user didn't select a start and end date, so do nothing")
            # The user didn't select a start and end date, so do nothing.
            return search_params

        # Add a date-range query with the selected start and end dates into the
        # Solr facet queries.
        fq = search_params.get("fq", None)

        # begin > start_date & begin < end_date
        # OR
        # end > start_date & end < end_date
        # OR
        # begin < start_date & end > end_date
        date_plus_inf = "3000-12-31T00:00:00Z"
        date_minus_inf = "2000-12-31T00:00:00Z"

        query1 = "data_temporal_extent_begin_date:[{start_date} TO {end_date}]".format(
            start_date=start_date, end_date=end_date
        )
        query2 = "data_temporal_extent_end_date:[{start_date} TO {end_date}]".format(
            start_date=start_date, end_date=end_date
        )
        query3 = "(data_temporal_extent_begin_date:[{date_minus_inf} TO {start_date}] AND data_temporal_extent_end_date:[{end_date} TO {date_plus_inf}])".format(
            start_date=start_date, end_date=end_date, date_minus_inf=date_minus_inf, date_plus_inf=date_plus_inf
        )

        if fq:
            fq = "{fq} AND (({query1}) OR ({query2}) OR ({query3}))".format(
                fq=fq, query1=query1, query2=query2, query3=query3
            )
        else:
            fq = "(({query1}) OR ({query2}) OR ({query3}))".format(query1=query1, query2=query2, query3=query3)

        log.info("Query: " + fq)
        search_params["fq"] = fq
        return search_params

    def before_index(self, pkg_dict):
        t_ext_inst = pkg_dict.get("extras_" + "temporal-extent-instant")
        if t_ext_inst:
            log.info("...Creating index for temporal field: %s ", "temporal-extent-instant")
            pkg_dict["extras_" + "temporal_extent_instant"] = t_ext_inst

        t_ext_begin = pkg_dict.get("data_temporal_extent_begin_date")
        if t_ext_begin:
            log.info("...Creating index for temporal field: %s", "data_temporal_extent_begin_date")
            pkg_dict["data_temporal_extent_begin_date"] = t_ext_begin

        t_ext_end = pkg_dict.get("data_temporal_extent_end_date")
        if t_ext_end:
            log.info("...Creating index for temporal field: %s", "data_temporal_extent_end_date")
            pkg_dict["data_temporal_extent_end_date"] = t_ext_end

        return pkg_dict
