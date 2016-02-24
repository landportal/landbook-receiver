# LANDPORTAL-RECEIVER  CONFIGURATION  FILE

# Put here all the IPs which can send requests to the receiver.
# If this list is empty, ALL REQUESTS WILL BE ACCEPTED
ALLOWED_IPS = [
    # "127.0.0.1",
]

# Those are the database configuration parameters.  Change them
# according to your configuration.  You may need to restart the
# receiver
MYSQL_URL = "localhost"
MYSQL_PORT = "3306"
MYSQL_DATABASE = "landportal"
MYSQL_USER = "root"
MYSQL_PASSWORD = "root"
DBA_USER = "dba"
DBA_PASSWORD = "dba"
TRIPLE_STORE_HOST = "http://localhost:8890/"
TRIPLE_STORE_API = "sparql-graph-crud-auth?"
GRAPH_URI = "graph-uri=http://book.landportal.org"
COUNTRY_LIST_FILE = 'countries/country_list.xlsx'
RDF_DATA_SET = 'datasets/dataset.rdf'
TURTLE_DATA_SET = 'datasets/dataset.ttl'
DATA_SETS_DIR = "datasets"
RAW_FILE = 'datasets/raw_file'
CKAN_INSTANCE = 'http://localhost:2000/data/'
PORTAL_HUB = 'http://localhost:2000'
SOURCE_IMG_PATH = '/sites/all/themes/book/static/images/sources/'
SOURCE_IMG = {"ORGFAO": "fao.png",
              "ORGUNDP": "undp.png",
              "ORGOECD": "oecd.png",
              "ORGWHO": "who.png",
              "ORGFONCIER": "observatoire-foncier.png",
              "ORGWB": "worldbank.png",
              "ORGIFPRI": "ifpri.png"

}
