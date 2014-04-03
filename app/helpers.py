import parser


class IndicatorSQLService(object):
    def __init__(self, content):
        self._parser = parser.Parser(content)

    #TODO: create two methods: get_all_indicators and get_new_indicators \
    # get_new_indicators will return only the indicators to persist in the
    # database. get_all_indicators will return the 

    def get_indicators(self):
        indicators = self._parser.get_indicators()
        # Filter indicators that already exist
        return [ind for ind in indicators if not self._fake_api_query(ind)]

    @staticmethod
    def _fake_api_query(indicator):
        """Simulates a query to the API to check if the indicator already exists
        """
        return indicator.id == 'INDIPFRI3'


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
        #TODO: check if the datasource already exists in the database
        return self._parser.get_datasource()

    def get_dataset(self):
        return self._parser.get_dataset()


class SliceSQLService(object):
    def __init__(self, content):
        self._parser = parser.Parser(content)

    def get_slices(self):
        return self._parser.get_slices()
