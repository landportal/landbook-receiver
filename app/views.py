
from flask_restful import Resource, Api, request, abort
from app import app, db
from app.services import ParserService

api = Api(app)
service = ParserService()


class Receiver(Resource):

    def post(self):
        """ Parse an XML and store the model mapping into the database.

        Receives an xml=... with the XML content to parse
        Returns a 200 response if everything went right or 400 if there
        is not any content to parse.
        """
        user_ip = request.remote_addr
        if 'xml' in request.form:
            session = db.session
            countries = self._get_countries()
            nodes = service.parse_nodes_content(content=request.form['xml'], ip=user_ip, countries=countries)
            session.merge(nodes)
            session.commit()
        else:
            abort(400)

    def _get_countries(self):
        from model import models
        session = db.session
        countries = session.query(models.Country).all()
        result = {}
        for item in countries:
            result[item.faoURI] = item
        return result


api.add_resource(Receiver, '/receiver')
