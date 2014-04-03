import unittest
import app
import create_db
import flask_testing
import model.models as model


class ServiceTest(flask_testing.TestCase):
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
        with open('xml/example_xml_ipfri.xml') as xml:
            self.send_request(content={'xml': xml.read()})
        #Open a session that will be used in the tests
        self.session = app.db.session
        #Import the models

    def _test_model_number(self, model):
        """Return the number of model objects in the database.
        """
        return len(self.session.query(model).all())


class CountryParserTest(ReceiverParserTest):
    """Region and RegionTranslations tests.
    """
    from model.models import Country, RegionTranslation, Region

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

    def test_region(self):
        """Test if the country region is set correctly.
        """
        #Get Spain (as a region, because countries don't have
        # is_part_of attribute)
        spain = self.session.query(self.Region) \
            .join(self.Country, self.Region.id == self.Country.id) \
            .filter(self.Country.iso3 == 'ESP') \
            .first()

        region = self.session.query(self.RegionTranslation) \
            .filter(self.RegionTranslation.region_id == spain.is_part_of_id) \
            .filter(self.RegionTranslation.lang_code == 'en').first()

        self.assertTrue(region.name == 'Europe')


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
        # Because one indicator has been left with a fake request to the
        # API, the topic should have only 3 indicators (not 4)
        self.assertTrue(len(topic99.indicators) == 3)
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
        #There should be 3 indicators in the database
        # ONE INDICATOR HAS BEEN LEFT WITH A FAKE QUERY TO THE API
        self.assertTrue(indicators == 3)

    def test_indicators_translations(self):
        """Test if the indicators have the correct translations.
        """
        indicators = self.session.query(self.Indicator).all()
        for ind in indicators:
            self.assertTrue(len(ind.translations) == 3)

    def test_indicators_excluded(self):
        indicators = self.session.query(model.Indicator).all()
        should_be_none = next((ind for ind in indicators if ind.id == 'INDIPFRI3'), None)
        self.assertTrue(should_be_none is None)


class ObservationParserTest(ReceiverParserTest):
    def test_observations_info(self):
        obsipfri0 = self.session.query(model.Observation) \
            .filter(model.Observation.id == 'OBSIPFRI1').first()
        self.assertTrue(obsipfri0 is not None)
        indicator = obsipfri0.indicator
        self.assertTrue(indicator.id == 'INDIPFRI0')
        computation = obsipfri0.computation
        self.assertTrue(computation.uri == 'purl.org/weso/ontology/computex#Raw')
        value = obsipfri0.value
        self.assertTrue(value.value == '9.0')
        self.assertTrue(value.obs_status == 'http://purl.org/linked-data/sdmx/2009/code#obsStatus-A')


class MetadataParserTest(ReceiverParserTest):
    def test_organization_info(self):
        organizations = self.session.query(model.Organization).all()
        self.assertTrue(len(organizations) == 1)
        org = self.session.query(model.Organization) \
            .filter(model.Organization.id == 'http://www.ifpri.org/') \
            .first()
        self.assertTrue(org is not None)
        self.assertTrue('IFPRI' in org.name)
        self.assertTrue(org.users)

    def test_user_info(self):
        users = self.session.query(model.User).all()
        self.assertTrue(len(users) == 1)
        user = users[0]
        self.assertTrue(user.id == 'USRIPFRIIMPORTER')


class SliceParserTest(ReceiverParserTest):
    def test_slices_info(self):
        sli = self.session.query(model.Slice).filter(model.Slice.id == 'SLIIPFRI0').first()
        self.assertTrue(sli is not None)
        # Check that the slice is linked to an indicator
        self.assertTrue(sli.indicator.id == 'INDIPFRI0')

    def test_slices_observations(self):
        sli = self.session.query(model.Slice).filter(model.Slice.id == 'SLIIPFRI0').first()
        # Check that the slice has linked observations
        self.assertTrue(sli.observations)
        # Check for a concrete observation
        observation = next((obs for obs in sli.observations
                            if obs.id == 'OBSIPFRI0'), None)
        self.assertTrue(observation is not None)

if __name__ == '__main__':
    unittest.main()

