import model.models as model
import datetime
import xml.etree.ElementTree as Et


class IndicatorSQLService(object):
    def __init__(self, parser):
        self._parser = parser

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
    def __init__(self, parser):
        self._parser = parser

    def get_observations(self):
        return self._parser.get_observations()


class MetadataSQLService(object):
    """Provides access to the dataset metadata
    """
    def __init__(self, parser):
        self._parser = parser

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
    def __init__(self, parser):
        self._parser = parser

    def get_slices(self):
        return self._parser.get_slices()


class Parser(object):
    def __init__(self, content):
        self._content = content
        self._root = Et.fromstring(content)

    def get_indicators(self):
        """Return a list of indicators
        """
        indicators = [self._get_indicator(item) for item in self._root.find('indicators').findall('indicator')]
        return indicators

    def get_user(self):
        """Parse the user data from the XML.
        """
        username = self._root.find('import_process').find('user').text
        return model.User(id=username, timestamp=datetime.datetime.utcnow())

    def get_organization(self):
        """Parse the organization data from the XML.
        """
        org_name = self._root.find('import_process').find('organization_name').text
        org_url = self._root.find('import_process').find('organization_url').text
        organization = model.Organization(name=org_name, id=org_url)
        organization.url = org_url
        return organization

    def get_datasource(self):
        datasource = self._root.find('import_process').find('datasource').text
        return model.DataSource(id_source=datasource, name=datasource)

    def get_dataset(self):
        dataset = model.Dataset()
        dataset.license = self._get_license()
        return dataset

    def _get_license(self):
        """Parse a license node and return a License object."""
        name = self._root.find('license').find('lic_name').text
        description = self._root.find('license').find('lic_description').text
        republish = self._root.find('license').find('republish').text
        url = self._root.find('license').find('lic_url').text
        return model.License(name=name,
                                 description=description,
                                 republish=bool(republish),
                                 url=url
                                )

    def _get_indicator(self, ind):
        indicator = model.Indicator(id=ind.get('id'),
                                     name=None,
                                     description=None,
                                     )
        indicator.measurement_unit = model.MeasurementUnit(name=ind.find('measure_unit').text)
        indicator.topic_id = ind.find('topic-ref').text
        indicator.add_translation(
            model.IndicatorTranslation(lang_code='en',
                                        name=ind.find('ind_name_en').text,
                                        description=ind.find('ind_description_en').text))
        indicator.add_translation(
            model.IndicatorTranslation(lang_code='es',
                                        name=ind.find('ind_name_es').text,
                                        description=ind.find('ind_description_es').text))
        indicator.add_translation(
            model.IndicatorTranslation(lang_code='fr',
                                        name=ind.find('ind_name_fr').text,
                                        description=ind.find('ind_description_fr').text))
        return indicator

    def get_observations(self):
        observations = [self._get_observation(item) for item in self._root.find('observations').findall('observation')]
        return observations

    def get_slices(self):
        return [self._get_slice(sli) for sli in self._root.find('slices').findall('slice')]

    def _get_observation(self, obs):
        observation = model.Observation()
        observation.id = obs.get('id')
        observation.indicator_id = obs.find('indicator-ref').get('indicator')
        observation.ref_time = self._parse_time(obs.find('time'))
        observation.issued = self._parse_issued(obs.find('issued'))
        observation.value = self._parse_obs_value(obs.find('obs-status'), obs.find('value'))
        observation.computation = self._parse_computation(obs.find('computation'))
        # TODO: Regions such as America should have an ISO3 code or equivalent to link directly
        observation.region_id = 1
        return observation

    def _get_slice(self, sli):
        time = self._parse_time(sli.find('sli_metadata').find('time'))
        slice = model.Slice(id=sli.get('id'), dimension=time)
        slice.indicator_id = sli.find('sli_metadata').find('indicator-ref').get('id')
        return slice

    @staticmethod
    def _parse_time(node):
        is_interval = node.find('interval') is not None
        if is_interval:
            interval = node.find('interval')
            start_year = int(interval.find('beginning').text)
            end_year = int(interval.find('end').text)

            beginning = datetime.date(year=start_year, month=1, day=1)
            end = datetime.date(year=end_year, month=1, day=1)
            return model.Interval(start_time=beginning, end_time=end)
        else:
            return model.YearInterval(year=node.text)

    @staticmethod
    def _parse_issued(node):
        date = datetime.datetime.strptime(node.text, '%Y-%m-%dT%H:%M:%S')
        return model.Instant(instant=date)

    @staticmethod
    def _parse_obs_value(status_node, value_node):
        value = model.Value(obs_status=status_node.text)
        if value_node is not None:
            value.value = value_node.text
        return value

    @staticmethod
    def _parse_computation(node):
        computation = model.Computation(uri=node.text)
        return computation
