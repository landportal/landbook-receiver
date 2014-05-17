import model.models as model
import datetime
try:
    import xml.etree.cElementTree as Et
except ImportError:
    import xml.etree.ElementTree as Et


class Parser(object):
    def __init__(self, content):
        self._content = content
        self._root = Et.fromstring(content)
        self._observations_slices = self._get_observations_slices()

    def _get_observations_slices(self):
        """Creates an inverse index of observations and slices.

        :returns: map in which the key is the observation ID and the
        value is its corresponding slice ID.
        """
        obs_map = {}
        slices = self._root.findall(".//slice")
        for sli in slices:
            observations = sli.findall("./referred/observation-ref")
            for obs in observations:
                obs_map[obs.get("id")] = sli.get("id")
        return obs_map

    def get_simple_indicators(self):
        """
        :returns: list of simple indicators found in the XML file.
        """
        ind_root = self._root.find("indicators")
        return (self._get_simple_indicator(ind) for ind
                in ind_root.findall("indicator"))

    def get_compound_indicators(self):
        """
        :returns: list of compound indicators found in the XML file.
        """
        ind_root = self._root.find("indicators")
        return (self._get_compound_indicator(ind) for ind
                in ind_root.findall("compound_indicator"))

    def get_indicator_groups(self):
        """
        :returns: list of indicator groups found in the XML file.
        """
        groups_element = self._root.find('indicator_groups')\
            .findall('indicator_group')
        return [self._get_indicator_group(ind) for ind in groups_element]

    def get_user(self):
        """
        :returns: user data found in the XML file (whithout user_ip)
        """
        username = self._root.find('import_process').find('user').text
        return model.User(id=username, timestamp=datetime.datetime.utcnow())

    def get_organization(self):
        """
        :returns: organization data found in the XML file.  The organization ID
            is constructed with the domain name in the organization_url, for
            example www.observatoire-foncier.com will result in the ID
            'observatoire-foncier'.
        """
        org_name = self._root.find('import_process').find('organization_name').text
        org_url = self._root.find('import_process').find('organization_url').text
        org_id = org_url.split(".")[1]
        organization = model.Organization(name=org_name, id=org_id)
        organization.url = org_url
        return organization

    def get_datasource(self):
        """
        :returns: datasource data found in the XML file.
        """
        dsource = self._root.find('import_process').find('datasource')
        dsource_name = dsource.text
        dsource_id = dsource.get("id")
        return model.DataSource(name=dsource_name, dsource_id=dsource_id)

    def get_dataset(self):
        """
        :returns: dataset data found in the XML file.
        """
        dataset = model.Dataset()
        dataset.id = self._root.get('id')
        dataset.sdmx_frequency = self._root.find('import_process').\
            find('sdmx_frequency').text
        dataset.license = self.get_license()
        return dataset

    def get_license(self):
        """
        :returns: license data of the XML file.
        """
        name = self._root.find('license').find('lic_name').text
        description = self._root.find('license').find('lic_description').text
        republish = self._root.find('license').find('republish').text
        url = self._root.find('license').find('lic_url').text
        return model.License(name=name, description=description,\
            republish=bool(republish), url=url)

    def _get_simple_indicator(self, ind):
        indicator = model.Indicator(id=ind.get('id'))
        indicator.measurement_unit = self._parse_measurement_unit(ind.find("measure_unit"))
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
        if ind.find('splitsIn') is not None:
            for rel in ind.find('splitsIn').findall('indicator-ref'):
                indicator.related_id.append(rel.get('id'))
        return indicator

    def _get_compound_indicator(self, ind):
        indicator = model.CompoundIndicator(id=ind.get('id'))
        indicator.measurement_unit = self._parse_measurement_unit(ind.find("measure_unit"))
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
        """
        :returns: list of observations found in the XML files.  Every observation
            comes with its ref_time, value and computation.  Each observation
            has the fields 'region_code' (UN_code) and 'country_code' (ISO3) of
            the region they reffer to.
        """
        obs_root = self._root.find("observations")
        return (self._get_observation(obs) for obs in obs_root.findall("observation"))

    def get_slices(self):
        """
        :returns: list of slices found in the XML files.  Each slice
            has the fields 'region_code' (UN_code) and 'country_code' (ISO3) of
            the region they reffer to.
        """
        sli_root = self._root.find('slices')
        return (self._get_slice(sli) for sli in sli_root.findall('slice'))

    def _get_observation(self, obs):
        def get_slice_id(obs_id):
            try:
                return self._observations_slices[obs_id]
            except KeyError:
                return None

        observation = model.Observation()
        observation.id = obs.get('id')
        observation.indicator_id = obs.find('indicator-ref').get('indicator')
        observation.ref_time = self._parse_time(obs.find('time'))
        observation.issued = self._parse_issued(obs.find('issued'))
        observation.value = self._parse_obs_value(obs.find('obs-status'), obs.find('value'))
        observation.computation = self._parse_computation(obs.find('computation'))
        observation.indicator_group_id = obs.get('group')
        observation.slice_id = get_slice_id(observation.id)
        observation.dataset_id = self.get_dataset().id
        # An observation may refer to a country or to a whole region
        # This fields will not be persisted to the database, instead it will
        # be used to link the observation with is referred region or country in the
        # services layer.
        observation.region_code = obs.find("region").text\
                if obs.find("region") is not None\
                else None
        observation.country_code = obs.find("country").text\
                if obs.find("country") is not None\
                else None
        return observation

    def _get_slice(self, sli):
        slice = model.Slice(id=sli.get('id'))
        slice.indicator_id = sli.find('sli_metadata')\
            .find('indicator-ref').get('id')
        metadata = sli.find("sli_metadata")
        slice.dataset_id = self.get_dataset().id
        # The slice's dimension may be a Region or a Time. If it is a Time we
        # can create it here and link it with the slice. If it is a Region we
        # we must check the API using it's region code or iso3 code.
        slice.dimension = self._parse_time(metadata.find("time"))\
                if metadata.find("time") is not None\
                else None
        # Those fields will not be persisted to the database, instead it will
        # be used to link the slice with its regions from the helpers layer.
        slice.region_code = metadata.find("region").text\
                if metadata.find("region") is not None\
                else None
        slice.country_code = metadata.find("country").text\
                if metadata.find("country") is not None\
                else None
        return slice

    @staticmethod
    def _parse_time(node):
        if node.get("unit") == "years":
            interval = node.find("interval")
            if interval is not None:
                start_year = int(interval.find("beginning").text)
                end_year = int(interval.find("end").text)

                beginning = datetime.date(year=start_year, month=1, day=1)
                end = datetime.date(year=end_year+1, month=1, day=1)
                return model.Interval(beginning, end)
            else:
                return model.YearInterval(int(node.text))
        elif node.get("unit") == "months":
            #The information comes in the format MM/YYYY
            month = int(node.text.split("/")[0])
            year = int(node.text.split("/")[1])
            return model.MonthInterval(month, year)


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
        computation = model.Computation(description=node.text, uri=node.get("type"))
        return computation

    @staticmethod
    def _parse_measurement_unit(node):
        return model.MeasurementUnit(
            name=node.text,
            convertible_to=node.get("convertible_to"),
            factor=node.get("factor")
        )
