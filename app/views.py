
from flask_restful import Resource, Api, request, abort
from app import app, db
from app.services import ParserService

api = Api(app)
service = ParserService()


class CountryListAPI(Resource):

    def post(self):
        """ Parse an XML and store the model mapping into the database.

        Receives an xml=... with the XML content to parse
        Returns a 200 response if everything went right or 400 if there
        is not any content to parse.
        """
        user_ip = request.remote_addr
        if 'xml' in request.form:
            nodes = service.parse_nodes_content(content=request.form['xml'], ip=user_ip)
            session = db.session
            session.merge(nodes)
            session.commit()
        else:
            abort(400)


api.add_resource(CountryListAPI, '/receiver')
