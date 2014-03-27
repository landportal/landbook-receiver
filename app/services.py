from model import models
import datetime
import xml.etree.ElementTree as Et


class ParserService(object):

    def parse_nodes_content(self, content, ip, countries):
        """Parse a XML file and return the corresponding model.

        Parse a XML (the XML file must conform with the Landportal schema)
        to create an object representation based on the Landportal-model.
        Returns the root of the model-tree (the Dataset).
        """
        root_node = Et.fromstring(content)
        dataset = self._parse_dataset(root_node, ip, countries)
        return dataset

    def _parse_dataset(self, node, ip, countries):
        """Parse a dataset node and return a Dataset object."""
        dataset = models.Dataset()
        datasource = self._parse_import_process(node.find('import_process'), ip)
        dataset.datasource = datasource
        license = self._parse_license(node.find('license'))
        dataset.license = license
        indicators = self._parse_indicators(node.find('indicators'), dataset)
        # Dataset observations
        observations = {}
        for item in node.find('observations').findall('observation'):
            obs = self._parse_observation(item, dataset, indicators, countries)
            observations[obs.id] = obs
        self._parse_slices(node.find('slices'), dataset, indicators, observations)
        return dataset

    def _parse_slices(self, node, dataset, indicators, observations):
        slices = {}
        for item in node.findall('slice'):
            slice = self._parse_slice(item, dataset, indicators, observations)
            slices[slice.id] = slice
        return slices

    def _parse_slice(self, node, dataset, indicators, observations):
        time = self._parse_time(node.find('sli_metadata').find('time'))
        indicator_id = node.find('sli_metadata').find('indicator-ref').get('id')
        indicator = indicators[indicator_id] if indicator_id in indicators else None
        slice = models.Slice(id=node.get('id'), dimension=time, indicator=indicator)
        dataset.add_slice(slice)
        for obs in node.find('referred').findall('observation-ref'):
            slice.add_observation(observations[obs.get('id')])
        return slice


    def _parse_import_process(self, node, ip):
        datasource = self._parse_datasource(node.find('datasource'))
        user = self._parse_user(node.find('user'), ip)
        organization = self._parse_organization(node.find('organization_name'), node.find('organization_url'))
        user.organization = organization
        datasource.organization = organization
        return datasource

    def _parse_datasource(self, node):
        """Parse a datasource node and return a Datasource object."""
        datasource = models.DataSource(id_source=node.text)
        return datasource

    def _parse_user(self, node, ip):
        user = models.User(id=node.text, ip=ip, timestamp=datetime.datetime.utcnow())
        return user

    def _parse_organization(self, name, url):
        organization = models.Organization(name=name.text, id=url.text)
        return organization

    def _parse_license(self, node):
        """Parse a license node and return a License object."""
        license = models.License(name=node.find('lic_name').text,
                                 description=node.find('lic_description').text,
                                 republish=bool(node.find('republish').text),
                                 url=node.find('lic_url').text)
        return license

    def _parse_indicators(self, node, dataset):
        """Parse all indicators and return a dictionary.

        Parse all indicators, including simple and compound indicators and
        return a dictionary in which the key will be the indicator.source_id
        and the value will be the indicator object.
        """
        indicators = {}
        # Single indicators
        for item in node.findall('indicator'):
            ind = self._parse_simple_indicator(item, dataset)
            indicators[ind.id] = ind
        # Compound indicators
        for item in node.findall('compound_indicator'):
            ind = self._parse_compound_indicator(item, dataset, indicators)
            indicators[ind.id] = ind
        return indicators


    def _parse_simple_indicator(self, node, dataset):
        """Parse an indicator node and return an Indicator object."""
        id_source = node.get('id')
        name = node.find('ind_name').text
        description = node.find('ind_description').text
        measurement = self._parse_measurement(node.find('measure_unit'))

        indicator = models.Indicator(id=id_source,
                                     name=name,
                                     description=description,
                                     )
        indicator.measurement_unit = measurement
        indicator.dataset = dataset
        return indicator

    def _parse_measurement(self, node):
        """Parse a measurement node and return a MeasurementUnit object."""
        measurement = models.MeasurementUnit(name=node.text)
        return measurement

    def _parse_compound_indicator(self, node, dataset, indicators):
        """Parse a compound indicator node and return a CompoundIndicator object."""
        id_source = node.get('id')
        name = node.find('ind_name').text
        description = node.find('ind_description').text
        measurement = self._parse_measurement(node.find('measure_unit'))

        indicator = models.CompoundIndicator(id=id_source,
                                             name=name,
                                             description=description,
                                             )
        indicator.measurement_unit = measurement
        indicator.dataset = dataset
        #TODO: link with indicator when the relation is mapped by the model
        #for rel in node.findall('indicator-ref'):
            # Buscar el indicador que sea en la coleccion de indicadores y
            # establecer en dicho indicador que esta relacionado con este
        #    indicators[rel.get('id')].compound_indicator = indicator
        return indicator

    def _parse_observation(self, node, dataset, indicators, countries):
        # TODO: parse indicator group
        observation = models.Observation()
        observation.id = node.get('id')
        rel_indicator_id = node.find('indicator-ref').get('indicator')
        observation.indicator = indicators[rel_indicator_id]
        observation.dataset = dataset
        observation.ref_time = self._parse_time(node.find('time'))
        observation.issued = self._parse_issued(node.find('issued'))
        observation.value = self._parse_obs_value(node.find('obs-status'), node.find('value'))
        observation.computation = self._parse_computation(node.find('computation'))
        # Set observation country
        country_uri = node.find('country').text
        observation.region_id = countries[country_uri].id if country_uri in countries else None
        return observation

    def _parse_time(self, node):
        is_interval = node.find('interval') is not None
        if is_interval:
            interval = node.find('interval')
            start_year = int(interval.find('beginning').text)
            end_year = int(interval.find('end').text)

            beginning = datetime.date(year=start_year, month=1, day=1)
            end = datetime.date(year=end_year, month=1, day=1)
            return models.Interval(start_time=beginning, end_time=end)
        else:
            return models.YearInterval(year=node.text)

    def _parse_issued(self, node):
        date = datetime.datetime.strptime(node.text, '%Y-%m-%dT%H:%M:%S')
        return models.Instant(instant=date)

    def _parse_obs_value(self, status_node, value_node):
        value = models.Value(obs_status=status_node.text)
        if value_node is not None:
            value.value = value_node.text
        return value

    def _parse_computation(self, node):
        computation = models.Computation(uri=node.text)
        return computation
