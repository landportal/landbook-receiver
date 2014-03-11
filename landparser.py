__author__ = 'guillermo'

try:
    import xml.etree.cElementTree as et
except ImportError:
    import xml.etree.ElementTree as et

from models import Indicator, MeasurementUnit

#with open('xml/sample.xml', 'rt') as f:
with open('xml/example_xml_ipfri_no_slices.xml', 'rt') as f:
    tree = et.parse(f)


def parse_nodes_content():
    """
    Creates a collection of objects from the
    xml node list
    :return observations, indicators
    """
    indicators = set()
    for node in tree.iter():
        if node.tag == 'indicator':
            indicator = Indicator(id_source=node.get('id'),
                                  name=node.find('ind_name').text,
                                  description=node.find('ind_description').text)
            measurement = MeasurementUnit(name=node.find('measure_unit').text)
            indicator.measurement_unit = measurement
            indicators.add(indicator)

    return list(indicators)
