__author__ = 'guillermo'

from parser import Parser
from rdf_utils.namespaces_handler import *
from rdflib import Literal, XSD, URIRef
from rdflib.namespace import RDF, RDFS, FOAF
import datetime
from countries.country_reader import CountryReader
import datetime as dt
import sh
import config


class ReceiverRDFService(object):
    def __init__(self, content):
        self.parser = Parser(content)
        self.time = datetime.datetime.now()

    def run_service(self, graph, host, api, graph_uri):
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
        self._add_upload_triples(graph)
        self._add_users_triples(graph)
        self._add_topics_triples(graph)
        self._serialize_rdf_xml(graph)
        self._serialize_turtle(graph)
        self._load_data_set(graph, host, api, graph_uri)
        return graph

    def _add_observations_triples(self, graph):
        for obs in self.parser.get_observations():
            region = self._get_area_code(obs)
            graph.add((prefix_.term(obs.id), RDF.type,
                       qb.term("Observation")))
            graph.add((prefix_.term(obs.id), cex.term("ref-time"),
                       prefix_.term(obs.ref_time.value)))
            graph.add((prefix_.term(obs.id), cex.term("ref-area"),
                       prefix_.term(region)))
            graph.add((prefix_.term(obs.id), cex.term("ref-indicator"),
                       prefix_.term(obs.indicator_id)))
            graph.add((prefix_.term(obs.id), cex.term("value"),
                       Literal(str(obs.value.value), datatype=XSD.double)))
            graph.add((prefix_.term(obs.id), cex.term("computation"),
                       cex.term(obs.computation.uri)))
            graph.add((prefix_.term(obs.id), dcterms.term("issued"),
                       Literal(obs.issued.timestamp, datatype=XSD.dateTime)))
            graph.add((prefix_.term(obs.id), qb.term("dataSet"),
                       prefix_.term(obs.dataset_id)))
            graph.add((prefix_.term(obs.id), qb.term("slice"),
                       prefix_.term(str(obs.slice_id))))
            graph.add((prefix_.term(obs.id), RDFS.label,
                       Literal("Observation of " + str(region) +
                               " within the period of " + str(obs.ref_time.value) +
                               " for indicator " + str(obs.indicator_id), lang='en')))
            graph.add((prefix_.term(obs.id),
                       sdmx_concept.term("obsStatus"),
                       sdmx_code.term(obs.value.obs_status)))
            # graph.add((prefix_.term(obs.id),
            #        lb.term("source"), prefix_.term(obs.source)))
        return graph

    def _add_indicators_triples(self, graph):
        for ind in self.parser.get_simple_indicators():
            graph.add((prefix_.term(ind.id), RDF.type,
                       cex.term("Indicator")))
            graph.add((prefix_.term(ind.id), lb.term("preferable_tendency"),
                       cex.term(ind.preferable_tendency)))
            graph.add((prefix_.term(ind.id), lb.term("measurement"),
                       cex.term(ind.measurement_unit.name)))
            graph.add((prefix_.term(ind.id), lb.term("last_update"),
                       Literal(self.time, datatype=XSD.dateTime)))
            graph.add((prefix_.term(ind.id), lb.term("starred"),
                       Literal(ind.starred, datatype=XSD.Boolean)))
            graph.add((prefix_.term(ind.id), lb.term("topic"),
                       cex.term(ind.topic_id)))
            graph.add((prefix_.term(ind.id), lb.term("indicatorType"),
                       cex.term(ind.type)))
            graph.add((prefix_.term(ind.id), RDFS.label,
                       Literal(ind.translations[0].name, lang='en')))
            graph.add((prefix_.term(ind.id), RDFS.comment,
                       Literal(ind.translations[0].description, lang='en')))
        return graph

    def _add_slices_triples(self, graph):
        for slc in self.parser.get_slices():
            graph.add((prefix_.term(slc.id), RDF.type,
                       qb.term("Slice")))
            graph.add((prefix_.term(slc.id), cex.term("indicator"),
                       prefix_.term(str(slc.indicator_id))))
            for obs in self.parser.get_observations():
                if obs.slice_id == slc.id:
                    graph.add((prefix_.term(slc.id), qb.term("observation"),
                               prefix_.term(str(obs.id))))
            if slc.region_code is not None:
                dimension = slc.region_code
            elif slc.country_code is not None:
                dimension = slc.country_code
            else:
                dimension = slc.dimension.value
            graph.add((prefix_.term(slc.id), lb.term("dimension"),
                       lb.term(dimension)))
            graph.add((prefix_.term(slc.id), qb.term("dataSet"),
                       prefix_.term(slc.dataset_id)))
        return graph

    def _add_users_triples(self, graph):
        usr = self.parser.get_user()
        organization = self.parser.get_organization()
        graph.add((prefix_.term(usr.id), RDF.type,
                   FOAF.Person))
        graph.add((prefix_.term(usr.id), RDFS.label,
                   Literal(usr.id, lang='en')))
        graph.add((prefix_.term(usr.id), FOAF.name,
                   Literal(usr.id)))
        graph.add((prefix_.term(usr.id), FOAF.account,
                   Literal(usr.id)))
        graph.add((prefix_.term(usr.id), org.term("memberOf"),
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
        graph.add((prefix_.term(topic_id), RDF.type,
                   lb.term("Topic")))
        graph.add((prefix_.term(topic_id), RDFS.label,
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
        country_list_file = '../countries/country_list.xlsx'
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
        graph.add((prefix_.term(country_id), RDF.type,
                   cex.term("Area")))
        graph.add((prefix_.term(country_id), RDFS.label,
                   Literal(country_name, lang="en")))
        graph.add((prefix_.term(country_id), lb.term("iso3"),
                   Literal(code)))
        graph.add((prefix_.term(country_id), lb.term("iso2"),
                   Literal(iso2)))
        graph.add((prefix_.term(country_id), lb.term("faoURI"),
                   URIRef(fao_uri)))
        graph.add((prefix_.term(country_id), lb.term("is_part_of"),
                   Literal(region)))
        return code

    def _add_region_triples(self, graph):
        self._add_region(graph, None)

    @staticmethod
    def _add_region(graph, arg):
        country_list_file = '../countries/country_list.xlsx'
        for region in CountryReader().get_countries(country_list_file):
            region_id = region.is_part_of_id
            graph.add((prefix_.term(region_id), RDF.type,
                       cex.term("Area")))
            graph.add((prefix_.term(region_id), RDFS.label,
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
            graph.add((prefix_.term(region.is_part_of_id), lb.term("UNCode"),
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
        graph.add((prefix_.term(dataset.id), RDF.type,
                   qb.term(Literal("DataSet"))))
        graph.add((prefix_.term(dataset.id), sdmx_concept.term("freq"),
                   sdmx_code.term(dataset.sdmx_frequency)))
        graph.add((prefix_.term(dataset.id), lb.term("license"),
                   URIRef(lic.url)))
        graph.add((prefix_.term(dataset.id), lb.term("dataSource"),
                   Literal(dsource.dsource_id)))
        return graph

    def _add_data_source_triples(self, graph):
        data_source = self.parser.get_datasource()
        organization = self.parser.get_organization()
        user = self.parser.get_user()
        graph.add((prefix_.term(data_source.dsource_id), RDF.type,
                   lb.term(Literal("DataSource"))))
        graph.add((prefix_.term(data_source.dsource_id), RDFS.label,
                   Literal(data_source.name, lang='en')))
        graph.add((prefix_.term(data_source.dsource_id), lb.term("organization"),
                   URIRef(organization.url)))
        graph.add((prefix_.term(data_source.dsource_id), dcterms.term("creator"),
                   Literal(user.id)))
        return graph

    def _add_upload_triples(self, graph):
        upload = "upload" + str(dt.datetime.now().
                                strftime("%y%m%d%H%M"))
        user = self.parser.get_user()
        dsource = self.parser.get_datasource()
        observations = self.parser.get_observations()
        graph.add((prefix_.term(upload), RDF.type,
                   lb.term(Literal("Upload"))))
        graph.add((prefix_.term(upload), lb.term("user"),
                   lb.term(user.id)))
        graph.add((prefix_.term(upload), lb.term("timestamp"),
                   Literal(dt.datetime.now(), datatype=XSD.dateTime)))
        #TODO get ip from the http request
        graph.add((prefix_.term(upload), lb.term("ip"),
                   Literal("156.35.82.103")))
        for obs in observations:
            graph.add((prefix_.term(upload), lb.term("observation"),
                       prefix_.term(obs.id)))
        graph.add((prefix_.term(upload), lb.term("dataSource"),
                   lb.term(dsource.dsource_id)))

        return graph

    @staticmethod
    def _serialize_rdf_xml(graph):
        serialized = graph.serialize(format='application/rdf+xml')
        with open('../datasets/dataset.rdf', 'w') as dataset:
            dataset.write(serialized)

    @staticmethod
    def _serialize_turtle(graph):
        serialized = graph.serialize(format='turtle')
        with open('../datasets/dataset.ttl', 'w') as dataset:
            dataset.write(serialized)

    @staticmethod
    def _load_data_set(host, api, graph_uri):
        sh.curl(host + api + graph_uri,
                digest=True, u=config.DBA_USER + ":" + config.DBA_PASSWORD,
                verbose=True, X="POST", T="../datasets/dataset.ttl")