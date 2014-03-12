__author__ = 'Herminio'

import unittest
import app
from flask_testing import TestCase

class ApiTest(TestCase):
    """
    Generic class for all test concerning Flask on this API
    """
    def create_app(self):
        app.app.config['TESTING'] = True
        return app.app


class TestCountry(ApiTest):
    def test_item(self):
        response = self.client.get("/receiver")
        self.assert200(response)
        print(response)

if __name__ == '__main__':
    unittest.main()