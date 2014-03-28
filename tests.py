import unittest
import app
import create_db
from flask_testing import TestCase

if __name__ == '__main__':
    unittest.main()


class ServiceTest(TestCase):
    """Generic base class for all Receiver tests.
    """
    def create_app(self):
        app.app.config['TESTING'] = True
        return app.app

    def setUp(self):
        create_db.create_database()

    def tearDown(self):
        app.db.session.remove()
        app.db.drop_all()

    def send_request(self, content=None):
        """Send a request to the Receiver with the specified POST content.
         Returns the response gotten from the Receiver.
        """
        return self.client.post("/receiver", data=content)


class ReceiverInterfaceTest(ServiceTest):
    """Class for testing of the Receiver HTTP interface.
    """
    def test_with_data(self):
        """Test that a correct request results in a 200 response.
        """
        xml = open('xml/example_xml_ipfri.xml', 'r').read()
        response = self.send_request(content={'xml': xml})
        self.assert200(response)

    def test_with_no_data(self):
        """Test that an incorrect request results in a 400 response.
        """
        response = self.send_request()
        self.assert400(response)


class ReceiverParserTest(ServiceTest):
    """Base class for tesing the Receiver parsing service.
    """

    def setUp(self):
        #Create the database as in ServiceTest
        super(ReceiverParserTest, self).setUp()
        #Send a request to the Receiver to populate the database
        xml = open('xml/example_xml_ipfri.xml', 'r').read()
        self.send_request(content={'xml': xml})
        #Open a session that will be used in the tests
        self.session = app.db.session
        #Import the models

    def _test_model_number(self, model):
        """Return the number of model objects in the database.
        """
        return len(self.session.query(model).all())


class CountryParserTest(ReceiverParserTest):
    """Country and CountryTranslations tests.
    """
    from model.models import Country

    def test_countries_number(self):
        """Test if all countries are in the database.
        """
        countries = self._test_model_number(self.Country)
        #There should be 248 countries in the database
        self.assertTrue(countries == 248)

    def test_countries_data(self):
        """Test if the country data in the database is correct.
        """
        #Fetch a country from the database
        spain = self.session.query(self.Country).filter(self.Country.iso3 == 'ESP').first()
        # Check that the country exists
        self.assertTrue(spain is not None)
        #Check that the ISO2 code is correct
        self.assertTrue(spain.iso2 == 'ES')
        #Check that the FAO_URI is well formed
        self.assertTrue(spain.faoURI == 'http://landportal.info/ontology/country/ESP')

    def test_countries_translations(self):
        """Test if the country translations are in the database.
        """
        france = self.session.query(self.Country).filter(self.Country.iso3 == 'FRA').first()
        # Check that the country exists
        self.assertTrue(france is not None)
        #Check that the country names are well translated
        self.assertTrue(len(france.translations) == 3)


class TopicParserTest(ReceiverParserTest):
    """Topic and TopicTranslation tests.
    """
    from model.models import Topic

    def test_topics_number(self):
        """Test if all topics are in the database.
        """
        topics = self._test_model_number(self.Topic)
        #There should be 8 topics in the database
        self.assertTrue(topics == 8)

    def test_topics_data(self):
        """Test if the topic data in the database is correct.
        """
        #Fetch a topic from the database
        topic99 = self.session.query(self.Topic).filter(self.Topic.id == 'TOP99').first()
        topic1 = self.session.query(self.Topic).filter(self.Topic.id == 'TOP1').first()
        #Check that the topic exists
        self.assertTrue(topic99 is not None)
        self.assertTrue(topic1 is not None)
        #Check that the topic name is correct
        self.assertTrue(topic99.name == 'TOPIC_TEMPORAL')
        #Check the topic indicators
        self.assertTrue(len(topic99.indicators) == 4)
        self.assertTrue(len(topic1.indicators) == 0)

    def test_topics_translations(self):
        """Test if the topics have the correct translations.
        """
        topics = self.session.query(self.Topic).all()
        for topic in topics:
            self.assertTrue(len(topic.translations) == 1)


class IndicatorParserTest(ReceiverParserTest):
    """Indicator and IndicatorTranslation tests.
    """
    from model.models import Indicator

    def test_indicators_number(self):
        """Test if all indicators are in the database.
        """
        indicators = self._test_model_number(self.Indicator)
        #There should be 4 indicators in the database
        self.assertTrue(indicators == 4)

    def test_indicators_translations(self):
        """Test if the indicators have the correct translations.
        """
        indicators = self.session.query(self.Indicator).all()
        for ind in indicators:
            self.assertTrue(len(ind.translations) == 3)

