__author__ = 'guillermo'

from parser import Parser
from rdf_utils.namespaces_handler import *
from rdflib import Literal, XSD
from rdflib.namespace import RDF, RDFS, FOAF


class ReceiverRDFService(object):
    def __init__(self, content):
        self.parser = Parser(content)

    def add_observations_triples(self, graph):
        for obs in self.parser.get_observations():
            graph.add((prefix_.term(obs.id), RDF.type,
                       qb.term("Observation")))

            graph.add((prefix_.term(obs.id), cex.term("ref-time"),
                       prefix_.term(obs.ref_time)))

            graph.add((prefix_.term(obs.id), cex.term("ref-area"),
                       prefix_.term(obs.region_id)))

            graph.add((prefix_.term(obs.id), cex.term("ref-indicator"),
                       prefix_.term(str(obs.indicator))))

            graph.add((prefix_.term(obs.id), cex.term("value"),
                       Literal(obs.value_id, datatype=XSD.double)))

            graph.add((prefix_.term(obs.id), cex.term("computation"),
                       cex.term(str(obs.computation.id))))

            graph.add((prefix_.term(obs.id), dcterms.term("issued"),
                       Literal(obs.issued, datatype=XSD.dateTime)))

            graph.add((prefix_.term(obs.id), qb.term("dataSet"),
                       prefix_.term(str(obs.dataset))))

            graph.add((prefix_.term(obs.id), qb.term("slice"),
                       prefix_.term(str(obs.slice_id))))

            # graph.add((prefix_.term(obs.id), RDFS.label,
            #        Literal(obs.description, lang='en')))

            # graph.add((prefix_.term(obs.id),
            #        sdmx_concept.term("obsStatus"), sdmx_code.term(obs.status)))

            # graph.add((prefix_.term(obs.id),
            #        lb.term("source"), prefix_.term(obs.source)))

            graph.add((prefix_.term(obs.region_id), RDF.type,
                       cex.term("Area")))
        return graph


    def add_indicators_triples(self, graph):
        for ind in self.parser.get_simple_indicators():
            graph.add((prefix_.term(ind.id), RDF.type,
                   cex.term("Indicator")))

            graph.add((prefix_.term(ind.id), lb.term("preferable_tendency"),
                   cex.term(ind.preferable_tendency)))

            graph.add((prefix_.term(ind.id), lb.term("measurement"),
                   cex.term(ind.measurement_unit)))

            graph.add((prefix_.term(ind.id), lb.term("last_update"),
                   Literal(ind.last_update, datatype=XSD.dateTime)))

            graph.add((prefix_.term(ind.id), lb.term("starred"),
                   Literal(ind.starred, datatype=XSD.Boolean)))

            graph.add((prefix_.term(ind.id), lb.term("topic"),
                   cex.term(ind.topic_id)))

            graph.add((prefix_.term(ind.id), lb.term("indicatorType"),
                   cex.term(ind.type)))

            graph.add((prefix_.term(ind.id), RDFS.label,
                   Literal(ind.translations[0].description, lang='en')))

            graph.add((prefix_.term(ind.id), RDFS.comment,
                       Literal("Longer description of " +
                               ind.translations[0].description, lang='en')))

        return graph

    def add_slices_triples(self, graph):
        for slc in self.parser.get_slices():
            graph.add((prefix_.term(slc.id), RDF.type,
                   qb.term("Slice")))

            graph.add((prefix_.term(slc.id), cex.term("indicator"),
                   prefix_.term(str(slc.indicator))))

            graph.add((prefix_.term(slc.id), qb.term("observation"),
                   prefix_.term("Obs")))

            graph.add((prefix_.term(slc.id), lb.term("dimension"),
                   prefix_.term(slc.dimension)))

            graph.add((prefix_.term(slc.id), qb.term("dataSet"),
                   prefix_.term(str(slc.dataset))))

        return graph

    # def add_users_triples(self, graph):
    #     for usr in self.parser.get_user():
    #         graph.add((prefix_.term(usr.user_id), RDF.type,
    #                FOAF.Person))
    #         graph.add((prefix_.term(usr.user_id), RDFS.label,
    #                Literal(usr.user_id, lang='en')))
    #         graph.add((prefix_.term(usr.user_id), FOAF.name,
    #                Literal(usr.user_id)))
    #         graph.add((prefix_.term(usr.user_id), FOAF.account,
    #                Literal(usr.user_id)))
    #         graph.add((prefix_.term(usr.user_id), org.term("memberOf"),
    #                prefix_.term(str(usr.organization))))
    #
    #     return graph

    # def add_topics_triples(self, graph):
    #     for topic in self.parser.get:
    #         g.add((prefix_.term(topic.topic), RDF.type,
    #                lb.term("Topic")))
    #         g.add((prefix_.term(topic.topic), RDFS.label,
    #                Literal(topic.topic, lang='en')))

    def serialize_rdf_xml(self, graph):
        serialized = graph.serialize(format='application/rdf+xml')
        with open('../datasets/dataset.rdf', 'w') as dataset:
            dataset.write(serialized)


    def serialize_turtle(self, graph):
        serialized = graph.serialize(format='turtle')
        with open('../datasets/dataset.ttl', 'w') as dataset:
            dataset.write(serialized)


