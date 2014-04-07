import model.models as model
import xml.etree.ElementTree as Et
import datetime


class Parser(object):
    def __init__(self, content):
        self._content = content
        self._root = Et.fromstring(content)

    def get_simple_indicators(self):
        """Return a list of indicators
        """
        indicators = self._root.find('indicators').findall('indicator')
        simple_indicators = [self._get_simple_indicator(item) for item
                             in indicators]
        return simple_indicators

    def get_compound_indicators(self):
        indicators = self._root.find('indicators').findall('compound_indicator')
        compound_indicators = [self._get_compound_indicator(item) for item
                               in indicators]
        return compound_indicators

    def get_indicator_groups(self):
        groups_element = self._root.find('indicator_groups')\
            .findall('indicator_group')
        return [self._get_indicator_group(ind) for ind in groups_element]

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

    def _get_simple_indicator(self, ind):
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
        # The indicator may be related with others
        # The attribute related_id WILL NOT be persisted to the database and
        # it is only used to create the relationships objects in the services
        indicator.related_id = []
        if ind.find('relatedWith') is not None:
            for rel in ind.find('relatedWith').findall('indicator-ref'):
                indicator.related_id.append(rel.get('id'))
        return indicator

    def _get_compound_indicator(self, ind):
        indicator = model.CompoundIndicator(id=ind.get('id'),
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
        # The indicator may be related with others
        # The attribute related_id WILL NOT be persisted to the database and
        # it is only used to create the relationships objects in the services
        indicator.related_id = []
        for rel in ind.findall('indicator-ref'):
            indicator.related_id.append(rel.get('id'))
        return indicator

    def _get_indicator_group(self, group):
        indicator = model.IndicatorGroup()
        indicator.id = group.get('id')
        #The indicator group is linked to a CompoundIndicator. The attribute
        #indicator-ref will be used in the services layer to link the
        #IndicatorGroup and the CompoundIndicator, and it will not be
        #persisted to the database
        indicator.indicator_ref = group.get('indicator-ref')
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
        observation.indicator_group_id = obs.get('group')
        # This field will not be persisted to the database, instead it will
        # be used to link the observation with is referred region in the
        # services layer
        observation.region_code = obs.find('region').text
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
        # An observation may refer to an arbitrary interval of time...
        if node.get('unit') == 'years':
            if node.find('interval') is not None:
                interval = node.find('interval')
                start_year = int(interval.find('beginning').text)
                end_year = int(interval.find('end').text)

                beginning = datetime.date(year=start_year, month=1, day=1)
                end = datetime.date(year=end_year, month=1, day=1)
                return model.Interval(start_time=beginning, end_time=end)
            # ... It may also refer to a concrete year ...
            else:
                return model.YearInterval(year=node.text)
        # ... Or a concrete month of a year
        elif node.get('unit') == 'months':
            # The information comes in the format MM/YYYY
            month = int(node.text.split('/')[0])
            year = int(node.text.split('/')[1])
            beginning = datetime.date(year=year, month=month, day=1)
            if month == 12:
                end = datetime.date(year=year+1, month=1, day=1)
            else:
                end = datetime.date(year=year, month=month+1, day=1)
            return model.Interval(start_time=beginning, end_time=end)


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
