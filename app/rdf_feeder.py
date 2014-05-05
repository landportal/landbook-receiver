__author__ = 'guillermo'

import codecs
from app.rdf_service import ReceiverRDFService
from rdflib import Graph
import logging
from rdf_utils.namespaces_handler import bind_namespaces

with codecs.open('../xml/test_file.xml', encoding='utf-8') as xml:
        content = xml.read()

graph = Graph()
logging.basicConfig()


def feed_rdf():
    rdf_service = ReceiverRDFService(content)
    rdf_service.add_observations_triples(graph)
    rdf_service.add_indicators_triples(graph)
    rdf_service.add_slices_triples(graph)
    bind_namespaces(graph)
    rdf_service.serialize_turtle(graph)
    rdf_service.serialize_rdf_xml(graph)

if __name__ == "__main__":
    feed_rdf()