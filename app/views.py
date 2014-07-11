import flask_restful
import app
from app.sql_service import ReceiverSQLService
from app.rdf_service import ReceiverRDFService
from app.ckan_service import ReceiverCKANService
import config
from rdflib import Graph
from flask import request
import os


class Receiver(flask_restful.Resource):

    @staticmethod
    def post():
        """ Parse an XML and store the model mapping into the database.

        Receives an _xml=... with the XML content to parse
        Returns a 200 response if everything went right or 400 if there
        is not any content to parse.
        """
        host = config.TRIPLE_STORE_HOST
        triple_api = config.TRIPLE_STORE_API
        graph_uri = config.GRAPH_URI
        graph = Graph()
        ckan_instance = config.CKAN_INSTANCE

        user_ip = flask_restful.request.remote_addr
        if not _check_allowed_ip(user_ip):
            flask_restful.abort(403)

        if 'xml' in flask_restful.request.form and \
           'file' in flask_restful.request.files:
            xml_content = flask_restful.request.form['xml']
            ckan_api_key = flask_restful.request.form['api_key']
            file_ = request.files['file']
            path = os.path.join(config.DATA_SETS_DIR, "raw_file")
            file_.save(path)
            #ReceiverSQLService(xml_content.encode('utf-8')).run_service(user_ip)
            ReceiverRDFService(xml_content.encode('utf-8')).\
               run_service(host=host, api=triple_api, graph_uri=graph_uri,
                           user_ip=user_ip, graph=graph)
           # ReceiverCKANService(content=xml_content, api_key=ckan_api_key).\
           #     run_service(ckan_instance=ckan_instance, file_=file_)
            _remove_data_sets()
        else:
            flask_restful.abort(400)


def _remove_data_sets():
    os.remove(config.RDF_DATA_SET)
    os.remove(config.TURTLE_DATA_SET)
    os.remove(config.RAW_FILE)


def _check_allowed_ip(ip):
    """ Checks if an IP is allowed to send requests."""
    if len(config.ALLOWED_IPS) == 0:
        return True
    else:
        return ip in config.ALLOWED_IPS


api = flask_restful.Api(app.app)
api.add_resource(Receiver, '/')
