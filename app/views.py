import flask_restful
import app
from app.services import ReceiverSQLService


class Receiver(flask_restful.Resource):
    @staticmethod
    def post():
        """ Parse an XML and store the model mapping into the database.

        Receives an xml=... with the XML content to parse
        Returns a 200 response if everything went right or 400 if there
        is not any content to parse.
        """
        user_ip = flask_restful.request.remote_addr
        if 'xml' in flask_restful.request.form:
            content = flask_restful.request.form['xml']
            ReceiverSQLService(content.encode('utf-8')).store_data(user_ip)
        else:
            flask_restful.abort(400)

api = flask_restful.Api(app.app)
api.add_resource(Receiver, '/')
