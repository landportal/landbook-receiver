import unittest
import app
import create_db
import flask_testing
import model.models as model
import app.helpers


def mockAPI():
    """Mock the APIHelper for testing purposes."""
    app.helpers.APIHelper.check_datasource = classmethod(lambda cls, datasource: None)
    app.helpers.APIHelper.check_indicator_starred = classmethod(lambda cls, ind_id: ind_id == "INDIPFRI0")


class ServiceTest(flask_testing.TestCase):
    """Generic base class for all Receiver tests.
    """
    def create_app(self):
        app.app.config['TESTING'] = True
        # Use an SQLite instance for testing
        app.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        return app.app

    def setUp(self):
        # Mock the APIHelper for the tests
        mockAPI()
        create_db.create_database()

    def tearDown(self):
        app.db.session.remove()
        app.db.drop_all()

    def send_request(self, content=None):
        """Send a request to the Receiver with the specified POST content.
         Returns the response gotten from the Receiver.
        """
        return self.client.post("/", data=content)


class ReceiverInterfaceTest(ServiceTest):

    """Class for testing of the Receiver HTTP interface.
    """
    def test_with_data(self):
        """Test that a correct request results in a 200 response.
        """
        xml = open('xml/example_xml_ipfri.xml', 'r').read()
        response = self.send_request(content={'xml': unicode(xml).encode('UTF-8')})
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
        # Mock the APIHelper for the tests
        mockAPI()
        #Create the database as in ServiceTest
        super(ReceiverParserTest, self).setUp()
        #Send a request to the Receiver to populate the database
        with open('xml/example_xml_ipfri.xml') as xml:
            self.send_request(content={'xml': xml.read()})
        #Open a session that will be used in the tests
        self.session = app.db.session

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
        self.assertTrue(spain.un_code == 724)

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

        europe = self.session.query(self.Region)\
            .filter(self.Region.id == spain.is_part_of_id)\
            .first()
        self.assertTrue(europe.un_code == 150)

        eur_name_en = self.session.query(self.RegionTranslation) \
            .filter(self.RegionTranslation.region_id == europe.id) \
            .filter(self.RegionTranslation.lang_code == 'en').first()
        eur_name_es = self.session.query(self.RegionTranslation) \
            .filter(self.RegionTranslation.region_id == europe.id) \
            .filter(self.RegionTranslation.lang_code == 'es').first()

        self.assertTrue(eur_name_en.name == 'Europe')
        self.assertTrue(eur_name_es.name == 'Europa')

    def test_region_obs(self):
        region = self.session.query(model.Region)\
            .filter(model.Region.un_code == 4)\
            .first()
        self.assertTrue(region.observations)

        obsipfri0 = next((obs for obs in region.observations
                          if obs.id == 'OBSIPFRI0'), None)
        self.assertTrue(obsipfri0 is not None)


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
        #Check the topic indicators
        self.assertTrue(len(topic99.indicators) == 5)
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
        """Test if all indicators are in the database."""
        indicators = self._test_model_number(self.Indicator)
        #There should be 4 indicators in the database (3 simple and 1 compound)
        #One simple indicator has been left out with a fake request to the api
        self.assertTrue(indicators == 5)

    def test_indicators_data(self):
        """Test if the indicators have the correct data."""
        ind = self.session.query(model.Indicator)\
            .filter(model.Indicator.id == 'INDIPFRI2')\
            .first()
        self.assertTrue(ind.preferable_tendency == 'decrease')
        self.assertTrue(len(ind.datasets) == 1)

    def test_indicators_translations(self):
        """Test if the indicators have the correct translations."""
        indicators = self.session.query(self.Indicator).all()
        for ind in indicators:
            self.assertTrue(len(ind.translations) == 3)

    def test_relathionships(self):
        """Test the simple indicator relationships."""
        indipfri2 = self.session.query(model.Indicator)\
            .filter(model.Indicator.id == 'INDIPFRI2').first()
        rels = self.session.query(model.IndicatorRelationship)\
            .filter(model.IndicatorRelationship.source_id == indipfri2.id).all()
        self.assertTrue(len(rels) == 2)
        targets = [ind.target_id for ind in rels]
        self.assertTrue('INDIPFRI0' in targets)
        self.assertTrue('INDIPFRI1' in targets)

    def test_compounds(self):
        """Test the compound indicators."""
        compound = self.session.query(model.CompoundIndicator)\
            .filter(model.CompoundIndicator.id == 'INDIPFRI4').first()
        self.assertTrue(len(compound.datasets) == 1)
        self.assertTrue(compound.indicator_ref_group.id == "GINDIPFRI0")
        translations = self.session.query(model.IndicatorTranslation)\
            .filter(model.IndicatorTranslation.indicator_id == compound.id).all()
        self.assertTrue(len(translations) == 3)
        self.assertTrue(len(compound.indicator_refs) == 2)
        ref_ids = [ind.id for ind in compound.indicator_refs]
        self.assertTrue("INDIPFRI0" in ref_ids)
        self.assertTrue("INDIPFRI2" in ref_ids)

    def test_groups(self):
        """Test indicator groups"""
        group = self.session.query(model.IndicatorGroup)\
            .filter(model.IndicatorGroup.id == 'GINDIPFRI0')\
            .first()
        self.assertTrue(group.compound_indicator.id == "INDIPFRI4")
        self.assertTrue(len(group.observations) == 2)
        obs_ids = [obs.id for obs in group.observations]
        self.assertTrue("OBSIPFRI2599" in obs_ids)
        self.assertTrue("OBSIPFRI2598" in obs_ids)

    def test_starred(self):
        """Test Indicator and CompoundIndicator starred state.
        By default new indicators will not be starred. If an indicator is
        already starred it will preserve its state."""
        ind1 = self.session.query(model.Indicator)\
                .filter(model.Indicator.id == "INDIPFRI0").first()
        self.assertTrue(ind1.starred)
        ind2 = self.session.query(model.Indicator)\
                .filter(model.Indicator.id == "INDIPFRI1").first()
        self.assertFalse(ind2.starred)


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

    def test_time(self):
        obs1 = self.session.query(model.Observation)\
            .filter(model.Observation.id == "OBSIPFRI2599").first()
        self.assertTrue(obs1.ref_time.start_time.month == 12)
        self.assertTrue(obs1.ref_time.start_time.year == 2013)
        self.assertTrue(obs1.ref_time.end_time.month == 1)
        self.assertTrue(obs1.ref_time.end_time.year == 2014)
        obs2 = self.session.query(model.Observation)\
            .filter(model.Observation.id == "OBSIPFRI2598").first()
        self.assertTrue(obs2.ref_time.start_time.month == 2)
        self.assertTrue(obs2.ref_time.start_time.year == 2013)
        self.assertTrue(obs2.ref_time.end_time.month == 3)
        self.assertTrue(obs2.ref_time.end_time.year == 2013)

    def test_group(self):
        observations = self.session.query(model.Observation)\
            .filter(model.Observation.indicator_group_id == "GINDIPFRI0")\
            .all()
        self.assertTrue(len(observations) == 2)
        observation_ids = [obs.id for obs in observations]
        self.assertTrue("OBSIPFRI2598" in observation_ids)
        self.assertTrue("OBSIPFRI2599" in observation_ids)


class MetadataParserTest(ReceiverParserTest):
    """Tests for metadata of the import process.
    Includes tests for Organization, User, Dataset and Datasource"""
    def test_organization(self):
        organizations = self.session.query(model.Organization).all()
        self.assertTrue(len(organizations) == 1)
        org = self.session.query(model.Organization) \
            .filter(model.Organization.id == 'http://www.ifpri.org/') \
            .first()
        self.assertTrue(org is not None)
        self.assertTrue('IFPRI' in org.name)
        self.assertTrue(org.users)

    def test_user(self):
        users = self.session.query(model.User).all()
        self.assertTrue(len(users) == 1)
        user = users[0]
        self.assertTrue(user.id == 'USRIPFRIIMPORTER')

    def test_datasource(self):
        dsource = self.session.query(model.DataSource).first()
        self.assertTrue('IFPRI' in dsource.name)
        self.assertTrue(dsource.organization is not None)
        self.assertTrue(dsource.datasets is not None)

    def test_dataset(self):
        dataset = self.session.query(model.Dataset).first()
        self.assertTrue(dataset.datasource is not None)
        self.assertTrue('IFPRI' in dataset.datasource.name)
        self.assertTrue(dataset.license is not None)
        # The license of this dataset allows republishing (this may not be
        # applicable for other licenses)
        self.assertTrue(dataset.license.republish)
        self.assertTrue(len(dataset.indicators) == 5)
        self.assertTrue(dataset.sdmx_frequency == 'http://test_ontology.org/frequency')


class SliceParserTest(ReceiverParserTest):
    def test_info(self):
        sli = self.session.query(model.Slice)\
            .filter(model.Slice.id == 'SLIIPFRI0').first()
        self.assertTrue(sli is not None)
        self.assertTrue(sli.indicator.id == 'INDIPFRI0')
        self.assertTrue(sli.dataset is not None)

    def test_observations(self):
        sli = self.session.query(model.Slice)\
            .filter(model.Slice.id == 'SLIIPFRI0').first()
        # Check that the slice has linked observations
        self.assertTrue(sli.observations)
        # Check for a concrete observation
        observation = next((obs for obs in sli.observations
                            if obs.id == 'OBSIPFRI0'), None)
        self.assertTrue(observation is not None)

    def test_dimension(self):
        # Dimension may be a Region...
        sli = self.session.query(model.Slice)\
            .filter(model.Slice.id == 'SLIIPFRI0').first()
        self.assertTrue(sli.dimension.iso3 == 'ESP')
        # ... or a Time
        sli = self.session.query(model.Slice)\
            .filter(model.Slice.id == 'SLIIPFRI1').first()
        self.assertTrue(sli.dimension.start_time.year == 1994)
        self.assertTrue(sli.dimension.end_time.year == 1996)

if __name__ == '__main__':
    unittest.main()

