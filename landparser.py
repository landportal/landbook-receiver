__author__ = 'guillermo'

try:
    import xml.etree.cElementTree as et
except ImportError:
    import xml.etree.ElementTree as et

from landportal_model import models

#with open('xml/sample.xml', 'rt') as f:
with open('xml/example_xml_ipfri_no_slices.xml', 'rt') as f:
    tree = et.parse(f)


def parse_nodes_content():
    """
    Creates a collection of objects from the
    xml node list
    :return observations, indicators
    """
    dataset = _parse_dataset(tree.getroot())
    #for node in tree.iter():
        # if node.tag == 'indicator':
        #     indicator = Indicator(id_source=node.get('id'),
        #                           name=node.find('ind_name').text,
        #                           description=node.find('ind_description').text)
        #     measurement = MeasurementUnit(name=node.find('measure_unit').text)
        #     indicator.measurement_unit = measurement
        #     indicators.add(indicator)


    return dataset

def _parse_dataset(node):
    dataset = models.Dataset()
    datasource = _parse_datasource(node.find('import_process').find('datasource'))
    dataset.datasource = datasource
    license = _parse_license(node.find('license'))
    dataset.license = license
    return dataset

def _parse_datasource(node):
    datasource = models.DataSource(id_source=node.text)
    return datasource

def _parse_license(node):
    license = models.License(name=node.find('lic_name').text,
                             description=node.find('lic_description').text,
                             republish=bool(node.find('republish').text),
                             url=node.find('lic_url').text)
    return license