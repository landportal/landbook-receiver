__author__ = 'guillermo'

from parser import Parser
from rdf_utils.namespaces_handler import *
from rdflib import Literal, XSD, URIRef
from rdflib.namespace import RDF, RDFS, FOAF
from countries.country_reader import CountryReader
import datetime as dt
import sh
import os
import config


class ReceiverRDFService(object):
    """
    Service that gets the _xml input from the html request, generates RDF triples and store
    them in Virtuoso triple store
    """
    def __init__(self, content):
        self.parser = Parser(content)
        self.time = dt.datetime.now()

    def run_service(self, graph, host, api, graph_uri, user_ip):
        """Run the ReceiverRDFService

        :param graph: RDF graph.
        :param graph_uri: RDF graph URI to be stored in the triple store.
        :param host: Triple store host.
        :param api: Triple store authentication api.
        :param user_ip: IP from the invoker client.
        :returns: RDF graph.
        """
        bind_namespaces(graph)
        self._add_observations_triples(graph)
        self._add_indicators_triples(graph)
        self._add_area_triples_from_observations(graph)
        self._add_area_triples_from_slices(graph)
        self._add_computation_triples(graph)
        self._add_data_source_triples(graph)
        self._add_dataset_triples(graph)
        self._add_licenses_triples(graph)
        self._add_organizations_triples(graph)
        self._add_region_triples(graph)
        self._add_slices_triples(graph)
        self._add_upload_triples(graph, user_ip)
        self._add_users_triples(graph)
        self._add_topics_triples(graph)
        self._serialize_rdf_xml(graph)
        self._serialize_turtle(graph)
        #self._load_data_set(graph_uri=graph_uri, host=host, api=api)
        #self._remove_data_sets()
        return graph

    def _add_observations_triples(self, graph):
        """

        """
        for obs in self.parser.get_observations():
            region = self._get_area_code(obs)
            graph.add((base_obs.term(obs.id), RDF.type,
                       qb.term("Observation")))
            graph.add((base_obs.term(obs.id), cex.term("ref-time"),
                       base.term(obs.ref_time.value)))
            graph.add((base_obs.term(obs.id), cex.term("ref-area"),
                       base.term(region)))
            graph.add((base_obs.term(obs.id), cex.term("ref-indicator"),
                       base_ind.term(obs.indicator_id)))
            graph.add((base_obs.term(obs.id), cex.term("value"),
                       Literal(str(obs.value.value), datatype=XSD.double)))
            graph.add((base_obs.term(obs.id), cex.term("computation"),
                       cex.term(str(obs.computation.uri))))
            graph.add((base_obs.term(obs.id), dcterms.term("issued"),
                       Literal(obs.issued.timestamp.strftime("%Y-%m-%d"),
                               datatype=XSD.date)))
            graph.add((base_obs.term(obs.id), qb.term("dataSet"),
                       base.term(obs.dataset_id)))
            graph.add((base_obs.term(obs.id), qb.term("slice"),
                       base.term(str(obs.slice_id))))
            graph.add((base_obs.term(obs.id), RDFS.label,
                       Literal("Observation of " + str(region) +
                               " within the period of " + str(obs.ref_time.value) +
                               " for indicator " + str(obs.indicator_id), lang='en')))
            graph.add((base_obs.term(obs.id),
                       sdmx_concept.term("obsStatus"),
                       sdmx_code.term(obs.value.obs_status)))
        return graph

    def _add_indicators_triples(self, graph):
        for ind in self.parser.get_simple_indicators():
            graph.add((base_ind.term(ind.id), RDF.type,
                       cex.term("Indicator")))
            graph.add((base_ind.term(ind.id), lb.term("preferable_tendency"),
                       cex.term(ind.preferable_tendency)))
            graph.add((base_ind.term(ind.id), lb.term("measurement"),
                       cex.term(ind.measurement_unit.name)))
            graph.add((base_ind.term(ind.id), lb.term("last_update"),
                       Literal(self.time.strftime("%Y-%m-%d"), datatype=XSD.date)))
            graph.add((base_ind.term(ind.id), lb.term("starred"),
                       Literal(ind.starred, datatype=XSD.Boolean)))
            graph.add((base_ind.term(ind.id), lb.term("topic"),
                       cex.term(ind.topic_id)))
            graph.add((base_ind.term(ind.id), lb.term("indicatorType"),
                       cex.term(ind.type)))
            graph.add((base_ind.term(ind.id), RDFS.label,
                       Literal(ind.translations[0].name, lang='en')))
            graph.add((base_ind.term(ind.id), RDFS.comment,
                       Literal(ind.translations[0].description, lang='en')))
        return graph

    def _add_slices_triples(self, graph):
        for slc in self.parser.get_slices():
            graph.add((base_slice.term(slc.id), RDF.type,
                       qb.term("Slice")))
            graph.add((base_slice.term(slc.id), cex.term("indicator"),
                       base.term(str(slc.indicator_id))))
            for obs in self.parser.get_observations():
                if obs.slice_id == slc.id:
                    graph.add((base_slice.term(slc.id), qb.term("observation"),
                               base.term(str(obs.id))))
            if slc.region_code is not None:
                dimension = slc.region_code
            elif slc.country_code is not None:
                dimension = slc.country_code
            else:
                dimension = slc.dimension.value
            graph.add((base_slice.term(slc.id), lb.term("dimension"),
                       lb.term(dimension)))
            graph.add((base_slice.term(slc.id), qb.term("dataSet"),
                       base.term(slc.dataset_id)))
        return graph

    def _add_users_triples(self, graph):
        usr = self.parser.get_user()
        organization = self.parser.get_organization()
        graph.add((base.term(usr.id), RDF.type,
                   FOAF.Person))
        graph.add((base.term(usr.id), RDFS.label,
                   Literal(usr.id, lang='en')))
        graph.add((base.term(usr.id), FOAF.name,
                   Literal(usr.id)))
        graph.add((base.term(usr.id), FOAF.account,
                   Literal(usr.id)))
        graph.add((base.term(usr.id), org.term("memberOf"),
                   URIRef(str(organization.id))))
        return graph

    def _add_organizations_triples(self, graph):
        organization = self.parser.get_organization()
        graph.add((URIRef(organization.id), RDF.type,
                   org.term("Organization")))
        graph.add((URIRef(organization.id), RDFS.label,
                   Literal(organization.name, lang='en')))
        graph.add((URIRef(organization.id), FOAF.homepage,
                   Literal(organization.url)))
        return graph

    def _add_topics_triples(self, graph):
        for ind in self.parser.get_simple_indicators():
            self._add_topic(graph, ind)
        return graph

    @staticmethod
    def _add_topic(graph, indicator):
        from create_db import MetadataPopulator

        topic_id = indicator.topic_id
        topic_label = ""
        for tp in MetadataPopulator.get_topics():
            if topic_id == tp.id:
                topic_label = tp.translations[0].name
        graph.add((base.term(topic_id), RDF.type,
                   lb.term("Topic")))
        graph.add((base.term(topic_id), RDFS.label,
                   Literal(topic_label, lang='en')))
        return topic_id

    def _add_area_triples_from_slices(self, graph):
        slices = self.parser.get_slices()
        for slc in slices:
            if slc.country_code:
                self._add_country(graph, slc)
            elif slc.region_code:
                self._add_region(graph, slc)
        return graph

    def _add_area_triples_from_observations(self, graph):
        observations = self.parser.get_observations()
        for obs in observations:
            if obs.country_code:
                self._add_country(graph, obs)
            elif obs.region_code:
                self._add_region(graph, obs)
        return graph

    @staticmethod
    def _add_country(graph, arg):
        code = arg.country_code
        country_list_file = config.COUNTRY_LIST_FILE
        country_id = ""
        country_name = ""
        iso2 = ""
        fao_uri = ""
        region = ""
        for country in CountryReader().get_countries(country_list_file):
            if code == country.iso3:
                country_id = country.iso3
                country_name = country.translations[0].name
                iso2 = country.iso2
                fao_uri = country.faoURI
                region = country.is_part_of_id
        graph.add((base.term(country_id), RDF.type,
                   cex.term("Area")))
        graph.add((base.term(country_id), RDFS.label,
                   Literal(country_name, lang="en")))
        graph.add((base.term(country_id), lb.term("iso3"),
                   Literal(code)))
        graph.add((base.term(country_id), lb.term("iso2"),
                   Literal(iso2)))
        graph.add((base.term(country_id), lb.term("faoURI"),
                   URIRef(fao_uri)))
        graph.add((base.term(country_id), lb.term("is_part_of"),
                   Literal(region)))
        return code

    def _add_region_triples(self, graph):
        self._add_region(graph, None)

    @staticmethod
    def _add_region(graph, arg):
        country_list_file = config.COUNTRY_LIST_FILE
        for region in CountryReader().get_countries(country_list_file):
            region_id = region.is_part_of_id
            graph.add((base.term(region_id), RDF.type,
                       cex.term("Area")))
            graph.add((base.term(region_id), RDFS.label,
                       Literal(region_id, lang="en")))
            un_code = None
            if region_id == "Americas":
                un_code = 19
            elif region_id == "Europe":
                un_code = 150
            elif region_id == "Oceania":
                un_code = 9
            elif region_id == "Africa":
                un_code = 2
            elif region_id == "Asia":
                un_code = 142
            graph.add((base.term(region.is_part_of_id), lb.term("UNCode"),
                       Literal(un_code)))

    @staticmethod
    def _get_area_code(arg):
        area = None
        if arg.country_code:
            area = arg.country_code
        elif arg.region_code:
            area = arg.region_code
        return area

    def _add_licenses_triples(self, graph):
        lic = self.parser.get_license()
        graph.add((URIRef(lic.url), RDF.type,
                   lb.term("License")))
        graph.add((URIRef(lic.url), lb.term("name"),
                   Literal(lic.name)))
        graph.add((URIRef(lic.url), lb.term("description"),
                   Literal(lic.description)))
        graph.add((URIRef(lic.url), lb.term("url"),
                   Literal(lic.url)))
        graph.add((URIRef(lic.url), lb.term("republish"),
                   Literal(lic.republish, datatype=XSD.Boolean)))
        return graph

    def _add_computation_triples(self, graph):
        for obs in self.parser.get_observations():
            graph.add((cex.term(obs.computation.uri), RDF.type,
                       cex.term(Literal("Computation"))))
            graph.add((cex.term(obs.computation.uri), RDFS.label,
                       Literal(obs.computation.description, lang='en')))
        return graph

    def _add_dataset_triples(self, graph):
        dataset = self.parser.get_dataset()
        lic = self.parser.get_license()
        dsource = self.parser.get_datasource()
        graph.add((base.term(dataset.id), RDF.type,
                   qb.term(Literal("DataSet"))))
        graph.add((base.term(dataset.id), sdmx_concept.term("freq"),
                   sdmx_code.term(dataset.sdmx_frequency)))
        graph.add((base.term(dataset.id), lb.term("license"),
                   URIRef(lic.url)))
        graph.add((base.term(dataset.id), lb.term("dataSource"),
                   Literal(dsource.dsource_id)))
        return graph

    def _add_data_source_triples(self, graph):
        data_source = self.parser.get_datasource()
        organization = self.parser.get_organization()
        user = self.parser.get_user()
        graph.add((base_dsource.term(data_source.dsource_id), RDF.type,
                   lb.term(Literal("DataSource"))))
        graph.add((base_dsource.term(data_source.dsource_id), RDFS.label,
                   Literal(data_source.name, lang='en')))
        graph.add((base_dsource.term(data_source.dsource_id), lb.term("organization"),
                   URIRef(organization.url)))
        graph.add((base_dsource.term(data_source.dsource_id), dcterms.term("creator"),
                   Literal(user.id)))
        return graph

    def _add_upload_triples(self, graph, ip):
        upload = "upload" + str(self.time.
                                strftime("%y%m%d%H%M"))
        user = self.parser.get_user()
        dsource = self.parser.get_datasource()
        observations = self.parser.get_observations()
        graph.add((base_upload.term(upload), RDF.type,
                   lb.term(Literal("Upload"))))
        graph.add((base_upload.term(upload), lb.term("user"),
                   lb.term(user.id)))
        graph.add((base_upload.term(upload), lb.term("timestamp"),
                   Literal(self.time.strftime("%Y-%m-%d"),
                           datatype=XSD.date)))
        graph.add((base_upload.term(upload), lb.term("ip"),
                   Literal(ip)))
        for obs in observations:
            graph.add((base_upload.term(upload), lb.term("observation"),
                       base.term(obs.id)))
        graph.add((base_upload.term(upload), lb.term("dataSource"),
                   lb.term(dsource.dsource_id)))

        return graph

    @staticmethod
    def _serialize_rdf_xml(graph):
        serialized = graph.serialize(format='application/rdf+xml')
        with open(config.RDF_DATA_SET, 'w') as dataset:
            dataset.write(serialized)

    @staticmethod
    def _serialize_turtle(graph):
        serialized = graph.serialize(format='turtle')
        with open(config.TURTLE_DATA_SET, 'w') as dataset:
            dataset.write(serialized)

    @staticmethod
    def _load_data_set(host, api, graph_uri):
        sh.curl(host + api + graph_uri,
                digest=True, u=config.DBA_USER + ":" + config.DBA_PASSWORD,
                verbose=True, X="POST", T=config.RDF_DATA_SET)

    @staticmethod
    def _remove_data_sets():
        os.remove(config.RDF_DATA_SET)
        os.remove(config.TURTLE_DATA_SET)
