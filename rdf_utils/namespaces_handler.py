__author__ = 'guillermo'

from rdflib import Namespace, URIRef

# Namespaces
cex = Namespace("http://purl.org/weso/ontology/computex#")
dc = Namespace("http://purl.org/dc/elements/1.1/")
dct = Namespace("http://purl.org/dc/terms/")
dctype = Namespace("http://purl.org/dc/dcmitype/")
foaf = Namespace("http://xmlns.com/foaf/0.1/")
lb = Namespace("http://purl.org/weso/landbook/ontology#")
org = Namespace("http://www.w3.org/ns/org#")
qb = Namespace("http://purl.org/linked-data/cube#")
sdmx_concept = Namespace("http://purl.org/linked-data/sdmx/2009/concept#")
time = Namespace("http://www.w3.org/2006/time#")
sdmx_code = Namespace("http://purl.org/linked-data/sdmx/2009/code#")
dcat = Namespace("http://www.w3.org/ns/dcat#")


base_url = "http://book.landportal.org/"
base = Namespace(base_url)
base_time = Namespace(base_url + "time/")
base_obs = Namespace(base_url + "observation/")
base_ind = Namespace(base_url + "indicator/")
base_slice = Namespace(base_url + "slice/")
base_dsource = Namespace(base_url + "datasource/")
base_topic = Namespace(base_url + "topic/")
base_upload = Namespace(base_url + "upload/")
base_org = Namespace(base_url + "organization/")
base_user = Namespace(base_url + "user/")
base_dataset = Namespace(base_url + "dataset/")


def bind_namespaces(graph):
    """
    Binds Landportal uris with their corresponding prefixes
    """
    n_space = {	"cex": cex,
		"dc": dc, 
		"dct": dct, 
		"dctype": dctype, 
		"foaf": foaf,
		"lb": lb,
		"org": org,
		"qb": qb,
		"sdmx-concept": sdmx_concept,
		"time": time,
		"sdmx-code": sdmx_code, 
		"": base, 
		"base-obs": base_obs,
		"base-ind": base_ind, 
		"base-slice": base_slice,
		"base-data-source": base_dsource, 
		"base-topic": base_topic,
		"base-upload": base_upload, 
		"base-org": base_org, 
		"base-time": base_time,
		"base-user": base_user,
		"dcat": dcat}

    for prefix, uri in n_space.items():
        graph.namespace_manager.bind(prefix, URIRef(Namespace(uri)))
