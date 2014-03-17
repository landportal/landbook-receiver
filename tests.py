import unittest
import app
from flask_testing import TestCase

if __name__ == '__main__':
    unittest.main()


class ServiceTest(TestCase):
    """
    Generic class for all test concerning Flask on this API
    """
    def create_app(self):
        app.app.config['TESTING'] = True
        return app.app


class TestParser(ServiceTest):

    def test_with_data(self):
        xml = open('xml/example_xml_ipfri_with_slices.xml', 'r').read()
        response = self.client.post("/receiver", data={'xml': xml})
        self.assert200(response)

    def test_with_no_data(self):
        response = self.client.post('/receiver')
        self.assert400(response)
