__author__ = 'guillermo'

import codecs
from app.rdf_service import ReceiverRDFService
from rdflib import Graph
import logging
from rdf_utils.namespaces_handler import bind_namespaces
import datetime as dt
import config

# test data
with codecs.open(unicode('../xml/test_file.xml', encoding='utf-8')) as xml:
    content = xml.read()

graph = Graph()
logging.basicConfig()
host = config.TRIPLE_STORE_HOST
api = config.TRIPLE_STORE_API
graph_uri = config.GRAPH_URI


def feed_rdf():
    rdf_service = ReceiverRDFService(content)
    bind_namespaces(graph)
    rdf_service.run_service(host=host, api=api, graph_uri=graph_uri,
                            graph=graph, user_ip="12.34.45.67")

if __name__ == "__main__":
    start = dt.datetime.now()
    feed_rdf()
    end = dt.datetime.now()
    print end - start