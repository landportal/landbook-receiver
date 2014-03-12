
from flask_restful import Resource, Api
from app import app, db
from app.services import ParserService

api = Api(app)
service = ParserService()


class CountryListAPI(Resource):

    def get(self):
        nodes = service.parse_nodes_content()
        session = db.session
        session.add(nodes)
        session.commit()

api.add_resource(CountryListAPI, '/receiver')
