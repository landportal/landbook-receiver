__author__ = 'guillermo'

import codecs
from app.rdf_service import ReceiverRDFService
from rdflib import Graph
import logging
from rdf_utils.namespaces_handler import bind_namespaces
import datetime as dt

# test data
with codecs.open(unicode('../xml/DATIPFRI_0_1_0_no_urls.xml', encoding='utf-8')) as xml:
    content = xml.read()

graph = Graph()
logging.basicConfig()
host = "http://localhost:1300/"
api = "sparql-graph-crud-auth?"
graph_uri = "graph-uri=http://www.landportal.info"


def feed_rdf():
    rdf_service = ReceiverRDFService(content)
    bind_namespaces(graph)
    #rdf_service.run_service(graph, host, api, graph_uri)
    rdf_service._load_data_set(host=host, api=api, graph_uri=graph_uri)

if __name__ == "__main__":
    start = dt.datetime.now()
    feed_rdf()
    end = dt.datetime.now()
    print end - start