import model.models as model
import xml.etree.ElementTree as Et
import datetime


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
        dsource_name = self._root.find('import_process').find('datasource').text
        return model.DataSource(name=dsource_name)

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
        indicator.preferable_tendency = ind.find('preferable_tendency').text
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
        slice = model.Slice(id=sli.get('id'))
        slice.indicator_id = sli.find('sli_metadata')\
            .find('indicator-ref').get('id')
        # This field will not be persisted to the database, instead it will
        # be used to link the slice with its regions from the services layer
        slice.region_code = None
        # The slice observation may be an Region or a Time. If it is a Time we
        # can create it here and link it with the slice. If it is a Region we
        # must query the database to get the corresponding object, that's why
        # we must link it from the services layer
        time_element = sli.find('sli_metadata').find('time')
        if time_element is not None:
            slice.dimension = self._parse_time(sli.find('sli_metadata')
                                               .find('time'))
        else:
            slice.region_code = int(sli.find('sli_metadata').find('region').text)
        # This list of Observation IDs will not be persisted to the database,
        # instead it will be used by the services layer to link the slice with
        # its observations, and it will find them using these IDs
        slice.observation_ids = []
        for obs in sli.find('referred').findall('observation-ref'):
            slice.observation_ids.append(obs.get('id'))
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
