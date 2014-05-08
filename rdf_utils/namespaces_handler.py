__author__ = 'guillermo'

from rdflib import Namespace, URIRef

# Namespaces
cex = Namespace("http://purl.org/weso/computex/ontology#")
dcterms = Namespace("http://purl.org/dc/terms/")
foaf = Namespace("http://xmlns.com/foaf/0.1/")
lb = Namespace("http://purl.org/weso/landbook/ontology#")
org = Namespace("http://www.w3.org/ns/org#")
qb = Namespace("http://purl.org/linked-data/cube#")
sdmx_concept = Namespace("http://purl.org/linked-data/sdmx/2009/concept#")
time = Namespace("http://www.w3.org/2006/time#")
sdmx_code = Namespace("http://purl.org/linked-data/sdmx/2009/code#")
prefix_ = Namespace("http://example.org/")


def bind_namespaces(graph):
    """
    Binds Landportal uris with their corresponding prefixes
    """
    graph.namespace_manager.bind("cex", URIRef(cex))
    graph.namespace_manager.bind("dcterms", URIRef(dcterms))
    graph.namespace_manager.bind("foaf", URIRef(foaf))
    graph.namespace_manager.bind("lb", URIRef(lb))
    graph.namespace_manager.bind("org", URIRef(org))
    graph.namespace_manager.bind("qb", URIRef(qb))
    graph.namespace_manager.bind("sdmx-concept", URIRef(sdmx_concept))
    graph.namespace_manager.bind("time", URIRef(time))
    graph.namespace_manager.bind("sdmx-code", URIRef(sdmx_code))
    graph.namespace_manager.bind("", URIRef(prefix_))
