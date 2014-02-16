__author__ = 'guillermo'

try:
    import xml.etree.cElementTree as et
except ImportError:
    import xml.etree.ElementTree as et

from models.observation import Observation

with open('xml/test.xml', 'rt') as f:
    tree = et.parse(f)


def parse_nodes_content():
    """
    Creates a collection of objects from the
    xml node list
    :return nodes
    """
    nodes = []
    for node in tree.iter():
        if node.tag == 'observation':
            nodes.append(Observation(issued=node.find('issued').text,
                                     computation=node.find('computation').text,
                                     country=node.find('country').text,
                                     relatedObs=node.find('relatedObs').text,
                                     relatedProperty=node.find(
                                         'relatedProperty').text,
                                     time=node.find('time').text,
                                     indicator=node.find('indicator').text))

    print nodes
    return nodes


def parse_nodes_attrib():
    """
    Creates a collection of objects from the
    xml node list
    :return nodes
    """
    nodes = []
    for node in tree.iter():
        if node.tag == 'observation':
            nodes.append(Observation(issued=node.get('issued'),
                                     computation=node.get('computation'),
                                     country=node.get('country'),
                                     relatedObs=node.get('relatedObs'),
                                     relatedProperty=node.get(
                                         'relatedProperty'),
                                     time=node.get('time'),
                                     indicator=node.get('indicator')))

    print nodes
    return nodes