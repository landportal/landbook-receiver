__author__ = 'guillermo'

from parser import Parser
from rdf_utils.namespaces_handler import *
from rdflib import Literal, XSD, URIRef
from rdflib.namespace import RDF, RDFS, FOAF
import datetime


class ReceiverRDFService(object):
    def __init__(self, content):
        self.parser = Parser(content)
        self.time = datetime.datetime.now()

    def add_observations_triples(self, graph):
        for obs in self.parser.get_observations():
            graph.add((prefix_.term(obs.id), RDF.type,
                       qb.term("Observation")))

            graph.add((prefix_.term(obs.id), cex.term("ref-time"),
                       prefix_.term(obs.ref_time.value)))

            graph.add((prefix_.term(obs.id), cex.term("ref-area"),
                       prefix_.term(obs.region_code)))

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
                       prefix_.term(obs.slice_id)))

            graph.add((prefix_.term(obs.id), RDFS.label,
                   Literal("Observation of region " + str(obs.region_code) + " in "
                           + str(obs.ref_time.value) + " for indicator "
                           + str(obs.indicator_id), lang='en')))

            graph.add((prefix_.term(obs.id),
                       sdmx_concept.term("obsStatus"),
                       sdmx_code.term(obs.value.obs_status)))

            # graph.add((prefix_.term(obs.id),
            #        lb.term("source"), prefix_.term(obs.source)))

            # graph.add((prefix_.term(obs.region_code), RDF.type,
            #            cex.term("Area")))
        return graph

    def add_indicators_triples(self, graph):
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

    def add_slices_triples(self, graph):
        for slc in self.parser.get_slices():
            graph.add((prefix_.term(slc.id), RDF.type,
                   qb.term("Slice")))

            graph.add((prefix_.term(slc.id), cex.term("indicator"),
                   prefix_.term(str(slc.indicator_id))))

            graph.add((prefix_.term(slc.id), qb.term("observation"),
                   prefix_.term(slc.observation_ids[0])))

            if slc.region_code is not None:
                dimension = slc.region_code
            elif slc.country_code is not None:
                dimension = slc.country_code
            else:
                dimension = slc.dimension.value

            graph.add((prefix_.term(slc.id), lb.term("dimension"),
                   prefix_.term(dimension)))

            graph.add((prefix_.term(slc.id), qb.term("dataSet"),
                   prefix_.term(str(slc.dataset))))

        return graph

    def add_users_triples(self, graph):
        usr = self.parser.get_user()
        graph.add((prefix_.term(usr.id), RDF.type,
               FOAF.Person))
        graph.add((prefix_.term(usr.id), RDFS.label,
               Literal(usr.id, lang='en')))
        graph.add((prefix_.term(usr.id), FOAF.name,
               Literal(usr.id)))
        graph.add((prefix_.term(usr.id), FOAF.account,
               Literal(usr.id)))
        graph.add((prefix_.term(usr.id), org.term("memberOf"),
               prefix_.term(str(usr.organization_id))))

        return graph

    def add_organizations_triples(self, graph):
        organization = self.parser.get_organization()
        graph.add((URIRef(organization.id), RDF.type,
               org.term("Organization")))
        graph.add((URIRef(organization.id), RDFS.label,
               Literal(organization.name, lang='en')))
        graph.add((URIRef(organization.id), FOAF.homepage,
               Literal(organization.url)))
        return graph

    def add_topics_triples(self, graph):
        for ind in self.parser.get_simple_indicators():
            graph.add((prefix_.term(ind.topic_id), RDF.type,
                   lb.term("Topic")))
            graph.add((prefix_.term(ind.topic_id), RDFS.label,
                   Literal(ind.topic_id, lang='en')))
        return graph

    def add_regions_triples(self, graph):
        for obs in self.parser.get_observations():
            region = None
            if obs.country_code is not None:
                region = obs.country_code
            elif obs.region_code is not None:
                region = obs.region_code

            graph.add((prefix_.term(region), RDF.type,
                          cex.term("Area")))

            # graph.add((prefix_.term(obs.region_code), lb.term("UNCode"),
            #        Literal("EU")))
        return graph

    def add_country_triples(self, graph):
        for obs in self.parser.get_observations():
            if obs.country_code is not None:
                country = obs.country_code

                graph.add((prefix_.term(country), RDF.type,
                          cex.term("Area")))

                graph.add((prefix_.term(country), RDFS.label,
                  Literal(country, lang='en')))
            #
            # graph.add((prefix_.term(obs.region_code), lb.term("UNCode"),
            #        Literal("EU")))
        return graph

    def add_licenses_triples(self, graph):
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



    def serialize_rdf_xml(self, graph):
        serialized = graph.serialize(format='application/rdf+xml')
        with open('../datasets/dataset.rdf', 'w') as dataset:
            dataset.write(serialized)

    def serialize_turtle(self, graph):
        serialized = graph.serialize(format='turtle')
        with open('../datasets/dataset.ttl', 'w') as dataset:
            dataset.write(serialized)