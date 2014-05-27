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

base = Namespace("http://book.landportal.org/")
base_obs = Namespace("http://book.landportal.org/observation/")
base_ind = Namespace("http://book.landportal.org/indicator/")
base_slice = Namespace("http://book.landportal.org/slice/")
base_dsource = Namespace("http://book.landportal.org/datasource/")
base_topic = Namespace("http://book.landportal.org/topic/")
base_upload = Namespace("http://book.landportal.org/upload/")


def bind_namespaces(graph):
    """
    Binds Landportal uris with their corresponding prefixes
    """
    n_space = {"cex": cex, "dcterms": dcterms, "foaf": foaf,
               "lb": lb, "org": org, "qb": qb,
               "sdmx-concept": sdmx_concept, "time": time,
               "sdmx-code": sdmx_code, "": base,
               "base-obs": base_obs, "base-ind": base_ind, "base-slice": base_slice,
               "base-data-source": base_dsource, "base-topic": base_topic,
               "base-upload": base_upload}

    for prefix, uri in n_space.items():
        graph.namespace_manager.bind(prefix, URIRef(Namespace(uri)))
