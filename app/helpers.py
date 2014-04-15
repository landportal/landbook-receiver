import parser
import requests
import model.models as model

class IndicatorSQLService(object):
    def __init__(self, content):
        self._parser = parser.Parser(content)

    def get_simple_indicators(self):
        return self._parser.get_simple_indicators()

    def get_compound_indicators(self):
        return self._parser.get_compound_indicators()

    def get_indicator_groups(self):
        return self._parser.get_indicator_groups()


class ObservationSQLService(object):
    def __init__(self, content):
        self._parser = parser.Parser(content)

    def get_observations(self):
        return self._parser.get_observations()


class MetadataSQLService(object):
    """Provides access to the dataset metadata
    """
    def __init__(self, content):
        self._parser = parser.Parser(content)

    def get_user(self, ip):
        """Return the User object representing the dataset user"""
        #TODO: check if the user already exists in the database
        user = self._parser.get_user()
        user.ip = ip
        return user

    def get_organization(self):
        #TODO: check if the organization already exists in the database
        return self._parser.get_organization()

    def get_datasource(self):
        datasource = self._parser.get_datasource()
        # Check if the datasource already exists in the database
        other = APIHelper().check_datasource(datasource.name)
        return other if other is not None else datasource

    def get_dataset(self):
        return self._parser.get_dataset()


class SliceSQLService(object):
    def __init__(self, content):
        self._parser = parser.Parser(content)

    def get_slices(self):
        return self._parser.get_slices()


class APIHelper(object):
    """ Comunicate with the API to check existing data in the database
    """
    def check_datasource(self, datasource_name):
        r = requests.get('http://localhost:80/api/datasources')
        # The data comes in JSON format
        datasources = r.json()
        # Find the JSON object with the required name
        datasource = next((dat for dat in datasources if str(dat['name']) == datasource_name), None)
        # Return the JSON object as a Datasource object
        if datasource is None:
            return None
        else:
            return self._make_datasource(datasource)

    def _make_datasource(self, datasource_data):
        datasource = model.DataSource()
        datasource.name = str(datasource_data['name'])
        datasource.id = int(datasource_data['id'])
        datasource.organization_id = str(datasource_data['organization_id'])
        return datasource
