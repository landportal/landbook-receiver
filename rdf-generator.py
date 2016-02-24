import logging
import sys, getopt, traceback

import config

from app.rdf_service import ReceiverRDFService
from rdflib import Graph

def main(argv):
   inputfile = ''
   outputfile = ''
   try:
      opts, args = getopt.getopt(argv,"hi:o:",["ifile=","ofile="])
   except getopt.GetoptError:
      print 'test.py -i <inputfile> -o <outputfile>'
      sys.exit(2)
   for opt, arg in opts:
      if opt == '-h':
         print 'test.py -i <inputfile> -o <outputfile>'
         sys.exit()
      elif opt in ("-i", "--input"):
         inputfile = arg
      elif opt in ("-o", "--output"):
         outputfile = arg
   run(inputfile, outputfile)

def run(inputfile_path, outputfile_path):
    configure_log()
    log = logging.getLogger("rdf-generator")

    try:
    	#read the file
	inputfile = open(inputfile_path, 'r')

    	#generate the RDF
        host = config.TRIPLE_STORE_HOST
        triple_api = config.TRIPLE_STORE_API
        graph_uri = config.GRAPH_URI
	user_ip = "127.0.0.1"
        graph = Graph()
	# obtain the xml in a string
	xml = inputfile.read()

	#invoke the RDF Service (passing the output filepath)
        ReceiverRDFService(xml).\
            run_service(host=host, 
			api=triple_api, 
			graph_uri=graph_uri, 
			user_ip=user_ip, 
			graph=graph, 
			outputfile=outputfile_path)

    	#TODO send the RDF
	# Nowadays, the RDFService.run() send the data to the triplestore

    except Exception as detail:
        log.error("OOPS! Something went wrong %s" %detail)
	e = sys.exc_info()[0]
        print "Error: %s" %e
	traceback.print_exc(file=sys.stdout)

def configure_log():
    FORMAT = "%(asctime)s - %(name)s - %(levelname)s [%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s"
    logging.basicConfig(filename='rdf-generator.log', level=logging.INFO,
                        format=FORMAT)

if __name__ == '__main__':
   main(sys.argv[1:])
