from app import db
from model import models


class ParserService(object):

    def __init__(self):
        self.tm = TransactionManager()

    def parse_nodes_content(self):
        import xml.etree.ElementTree as Et
        tree = Et.parse('xml/example_xml_ipfri_no_slices.xml')
        dataset = self._parse_dataset(tree.getroot())
        return dataset

    def _parse_dataset(self, node):
        """Parse a dataset node and return a Dataset object."""
        dataset = models.Dataset()
        datasource = self._parse_datasource(node.find('import_process').find('datasource'))
        dataset.datasource = datasource
        license = self._parse_license(node.find('license'))
        dataset.license = license
        # Dataset observations
        #indicators = []
        #for item in node.find('indicators').findall('indicator'):
        #    indicators.append(self._parse_indicator(item, dataset))
        return dataset

    def _parse_datasource(self, node):
        """Parse a datasource node and return a Datasource object."""
        datasource = models.DataSource(id_source=node.text)
        return datasource

    def _parse_license(self, node):
        """Parse a license node and return a License object."""
        license = models.License(name=node.find('lic_name').text,
                                 description=node.find('lic_description').text,
                                 republish=bool(node.find('republish').text),
                                 url=node.find('lic_url').text)
        return license

    def _parse_indicator(self, node, dataset):
        indicator = models.Indicator(id_source=node.get('id'))
        indicator.dataset = dataset
        indicator.name = node.find('ind_name').text
        indicator.description = node.find('ind_description').text
        measurement = self._parse_measurement(node.find('measure_unit'))
        indicator.measurement_unit = measurement
        return indicator

    def _parse_measurement(self, node):
        measurement = models.MeasurementUnit(name=node.text)
        return measurement


class TransactionManager(object):
    '''
    Transaction manager that helps to abstract from the execution

    @author: Herminio
    '''

    def execute(self, dao, function, *args):
        '''
        Abstraction for all calls to the dao methods, like command executor
        '''
        session = db.session
        getattr(dao, 'set_session')(session)
        result = function(*args)
        session.commit()

        return result


