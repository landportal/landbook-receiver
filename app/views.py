import flask_restful
import app
from app.sql_service import ReceiverSQLService
from app.rdf_service import ReceiverRDFService
import config
from rdflib import Graph


class Receiver(flask_restful.Resource):

    @staticmethod
    def post():
        """ Parse an XML and store the model mapping into the database.

        Receives an xml=... with the XML content to parse
        Returns a 200 response if everything went right or 400 if there
        is not any content to parse.
        """
        host = config.TRIPLE_STORE_HOST
        triple_api = config.TRIPLE_STORE_API
        graph_uri = config.GRAPH_URI
        graph = Graph()

        user_ip = flask_restful.request.remote_addr
        if not _check_allowed_ip(user_ip):
            flask_restful.abort(403)

        if 'xml' in flask_restful.request.form:
            content = flask_restful.request.form['xml']
            ReceiverSQLService(content.encode('utf-8')).store_data(user_ip)
            #ReceiverRDFService(content.encode('utf-8')).run_service(host=host,
            #                                                        api=triple_api,
            #                                                        graph_uri=graph_uri,
            #                                                        user_ip=user_ip,
            #                                                        graph=graph)
        else:
            flask_restful.abort(400)


def _check_allowed_ip(ip):
    """ Checks if an IP is allowed to send requests."""
    if len(config.ALLOWED_IPS) == 0:
        return True
    else:
        return ip in config.ALLOWED_IPS


api = flask_restful.Api(app.app)
api.add_resource(Receiver, '/')
