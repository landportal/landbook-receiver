import parser


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
        #TODO: check if the datasource already exists in the database
        return self._parser.get_datasource()

    def get_dataset(self):
        return self._parser.get_dataset()


class SliceSQLService(object):
    def __init__(self, content):
        self._parser = parser.Parser(content)

    def get_slices(self):
        return self._parser.get_slices()
