__author__ = 'guillermo'

try:
    import xml.etree.cElementTree as et
except ImportError:
    import xml.etree.ElementTree as et

from models import Observation, Indicator, Country

with open('xml/sample.xml', 'rt') as f:
    tree = et.parse(f)


def parse_nodes_content():
    """
    Creates a collection of objects from the
    xml node list
    :return observations, indicators
    """
    observations = []
    indicators = []
    for node in tree.iter():
        if node.tag == 'indicator':
            indicators.append(Indicator(id_source=node.get('id'),
                                        name=node.find('ind_name').text,
                                        description=node.find(
                                            'ind_description').text,
                                        measure_unit=node.find(
                                            'measure_unit').text))
        if node.tag == 'observation':
            observations.append(Observation(id_source=node.get('id'),
                                            issued=node.find('issued').text,
                                            obs_status=node.find(
                                                'obs-status').text,
                                            indicator_ref=node.find(
                                                'indicator-ref').
                                            get('id'),
                                            computation=node.find(
                                                'computation').text,
                                            country=Country(iso_code3=node.find(
                                                'country').text),
                                            time='timess'))
    return indicators + observations