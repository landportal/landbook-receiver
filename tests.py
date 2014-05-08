import unittest
import app
import create_db
import flask_testing
import model.models as model
import config


class ServiceTest(flask_testing.TestCase):
    """Base class for all tests. Sets up the testing environment"""
    def create_app(self):
        app.app.config["TESTING"] = True
        app.app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite://'
        return app.app

    def setUp(self):
        create_db.create_database()
        config.ALLOWED_IPS = []

    def tearDown(self):
        app.db.session.remove()
        app.db.drop_all()

    def send_request(self, content):
        """Send a request to the Receiver with the specified POST content.
         Returns the response gotten from the Receiver.
        """
        return self.client.post("/", data=content)


class ReceiverInterfaceTest(ServiceTest):
    """Tests for the receiver interface"""
    def test_request_with_data(self):
        """Send a request with data to the Receiver"""
        xml = open('xml/test_file.xml', 'r').read()
        content = unicode(xml).encode("UTF-8")
        response = self.send_request(content={'xml': content})
        self.assert200(response)

    def test_request_with_no_data(self):
        """Send an empty request to the Receiver"""
        response = self.send_request(content=None)
        self.assert400(response)

    def test_disallowed_ip(self):
        """Send a request with a disallowed IP"""
        config.ALLOWED_IPS = ["127.0.0.1"]
        response = self.send_request(content=None)
        self.assert403(response)


class ReceiverParserTest(ServiceTest):
    """Base class for testing the Receiver parsing"""
    def setUp(self):
        super(ReceiverParserTest, self).setUp()
        with open('xml/test_file.xml') as xml:
            self.send_request(content={'xml': xml.read()})
        self.session = app.db.session


class CountriesTest(ReceiverParserTest):
    """Country tests"""
    def test_country_number(self):
        countries = self.session.query(model.Country).all()
        self.assertTrue(len(countries) == 248)

    def test_country_iso2(self):
        country = self.session.query(model.Country)\
            .filter(model.Country.iso3 == "ESP")\
            .first()
        self.assertTrue(country.iso2 == "ES")

    def test_country_faouri(self):
        country = self.session.query(model.Country)\
            .filter(model.Country.iso3 == "ESP")\
            .first()
        expected_faouri = "http://landportal.info/ontology/country/ESP"
        self.assertTrue(country.faoURI == expected_faouri)

    def test_country_uncode(self):
        country = self.session.query(model.Country)\
            .filter(model.Country.iso3 == "ESP")\
            .first()
        self.assertTrue(country.un_code == 724)

    def test_country_translations(self):
        country = self.session.query(model.Country)\
            .filter(model.Country.iso3 == "FRA")\
            .first()
        translation_en = self.session.query(model.RegionTranslation)\
            .filter(model.RegionTranslation.region_id == country.id)\
            .filter(model.RegionTranslation.lang_code == "en")\
            .first()
        self.assertTrue(translation_en.name == "France")
        translation_es = self.session.query(model.RegionTranslation)\
            .filter(model.RegionTranslation.region_id == country.id)\
            .filter(model.RegionTranslation.lang_code == "es")\
            .first()
        self.assertTrue(translation_es.name == "Francia")


class RegionsTest(ReceiverParserTest):
    """Regions tests"""
    def test_region(self):
        country = self.session.query(model.Region)\
            .join(model.Country, model.Region.id == model.Country.id)\
            .filter(model.Country.iso3 == 'ESP')\
            .first()
        region = self.session.query(model.Region)\
            .filter(model.Region.id == country.is_part_of_id)\
            .first()
        self.assertTrue(region.un_code == 150)
        region_name_en = self.session.query(model.RegionTranslation)\
            .filter(model.RegionTranslation.region_id == region.id)\
            .filter(model.RegionTranslation.lang_code == 'en')\
            .first()
        self.assertTrue(region_name_en.name == "Europe")
        region_name_es = self.session.query(model.RegionTranslation)\
            .filter(model.RegionTranslation.region_id == region.id)\
            .filter(model.RegionTranslation.lang_code == 'es')\
            .first()
        self.assertTrue(region_name_es.name == "Europa")

    def test_region_observations(self):
        region = self.session.query(model.Country)\
            .filter(model.Country.iso3 == "ESP")\
            .first()
        obs_ids = [obs.id for obs in region.observations]
        self.assertTrue("OBSIPFRI0" in obs_ids)

    def test_global_region(self):
        spain = self.session.query(model.Region)\
            .join(model.Country, model.Region.id == model.Country.id)\
            .filter(model.Country.iso3 == "ESP")\
            .first()
        #Spain is part of Europe, which UN_CODE is 150
        europe = self.session.query(model.Region)\
            .filter(model.Region.id == spain.is_part_of_id)\
            .first()
        self.assertTrue(europe.un_code == 150)
        #Europe is part of Global, which UN_CODE is 1
        global_reg = self.session.query(model.Region)\
            .filter(model.Region.id == europe.is_part_of_id)\
            .first()
        self.assertTrue(global_reg.un_code == 1)


class TopicsTest(ReceiverParserTest):
    """Topic and TopicTranslation tests"""
    def test_number(self):
        topics = self.session.query(model.Topic).all()
        self.assertTrue(len(topics) == 7)

    def test_indicators(self):
        topic = self.session.query(model.Topic)\
            .filter(model.Topic.id == 'TEMP_TOPIC')\
            .first()
        self.assertTrue(len(topic.indicators) == 1)
        topic2 = self.session.query(model.Topic)\
            .filter(model.Topic.id == 'LAND_TENURE')\
            .first()
        self.assertTrue(len(topic2.indicators) == 2)
        topic3 = self.session.query(model.Topic)\
            .filter(model.Topic.id == 'FSECURITY_HUNGER')\
            .first()
        self.assertTrue(len(topic3.indicators) == 0)

    def test_translations(self):
        topics = self.session.query(model.Topic).all()
        for topic in topics:
            self.assertTrue(len(topic.translations) == 1)


class IndicatorsTest(ReceiverParserTest):
    """Indicator and IndicatorTranslation tests"""
    def test_number(self):
        indicators = self.session.query(model.Indicator).all()
        self.assertTrue(len(indicators) == 4)

    def test_preferable_tendency(self):
        ind = self.session.query(model.Indicator)\
            .filter(model.Indicator.id == "INDIPFRI2")\
            .first()
        self.assertTrue(ind.preferable_tendency == "decrease")

    def test_dataset(self):
        ind = self.session.query(model.Indicator)\
            .filter(model.Indicator.id == "INDIPFRI0")\
            .first()
        self.assertTrue(len(ind.datasets) == 1)

    def test_translations(self):
        indicators = self.session.query(model.Indicator).all()
        for ind in indicators:
            self.assertTrue(len(ind.translations) == 3)

    def test_relathionships(self):
        indipfri2 = self.session.query(model.Indicator)\
            .filter(model.Indicator.id == 'INDIPFRI2').first()
        rels = self.session.query(model.IndicatorRelationship)\
            .filter(model.IndicatorRelationship.source_id == indipfri2.id).all()
        self.assertTrue(len(rels) == 2)
        targets = [ind.target_id for ind in rels]
        self.assertTrue('INDIPFRI0' in targets)
        self.assertTrue('INDIPFRI1' in targets)

    def test_starred(self):
        ind = self.session.query(model.Indicator)\
            .filter(model.Indicator.id == "INDIPFRI1")\
            .first()
        self.assertTrue(ind.starred is False)

    def test_last_update(self):
        indicators = self.session.query(model.Indicator).all()
        for ind in indicators:
            self.assertTrue(ind.last_update is not None)
        ref_time = indicators[0].last_update
        for ind in indicators:
            self.assertTrue(ind.last_update == ref_time)

    def test_measurement_unit_smaller(self):
        ind = self.session.query(model.Indicator).filter(model.Indicator.id == "INDIPFRI2").first()
        measurement = ind.measurement_unit
        self.assertTrue(measurement.name == "%")
        self.assertTrue(measurement.convertible_to == "porcentaje")
        self.assertTrue(measurement.factor == 0.001)

    def test_measurement_unit_bigger(self):
        ind = self.session.query(model.Indicator).filter(model.Indicator.id == "INDIPFRI0").first()
        measurement = ind.measurement_unit
        self.assertTrue(measurement.name == "%")
        self.assertTrue(measurement.convertible_to == "porcentaje")
        self.assertTrue(measurement.factor == 100.4)


class CompoundIndicatorsTest(ReceiverParserTest):
    """CompoundIndicator tests"""
    def test_dataset(self):
        compound = self.session.query(model.CompoundIndicator)\
            .filter(model.CompoundIndicator.id == "INDIPFRI3")\
            .first()
        self.assertTrue(len(compound.datasets) == 1)

    def test_group(self):
        compound = self.session.query(model.CompoundIndicator)\
            .filter(model.CompoundIndicator.id == "INDIPFRI3")\
            .first()
        self.assertTrue(compound.indicator_ref_group.id == "GINDIPFRI0")

    def test_translations(self):
        translations = self.session.query(model.IndicatorTranslation)\
            .filter(model.IndicatorTranslation.indicator_id == "INDIPFRI3")\
            .all()
        self.assertTrue(len(translations) == 3)

    def test_references(self):
        compound = self.session.query(model.CompoundIndicator)\
            .filter(model.CompoundIndicator.id == "INDIPFRI3")\
            .first()
        self.assertTrue(len(compound.indicator_refs) == 2)
        ref_ids = [ind.id for ind in compound.indicator_refs]
        self.assertTrue("INDIPFRI0" in ref_ids)
        self.assertTrue("INDIPFRI2" in ref_ids)

    def test_measurement_unit(self):
        ind = self.session.query(model.Indicator).filter(model.Indicator.id == "INDIPFRI3").first()
        measurement = ind.measurement_unit
        self.assertTrue(measurement.name == "meters")
        self.assertTrue(measurement.convertible_to == "kilometers")
        self.assertTrue(measurement.factor == 1000)

class IndicatorGroupsTest(ReceiverParserTest):
    """IndicatorGroup tests"""
    def test_compound_indicator(self):
        group = self.session.query(model.IndicatorGroup)\
            .filter(model.IndicatorGroup.id == 'GINDIPFRI0')\
            .first()
        self.assertTrue(group.compound_indicator.id == "INDIPFRI3")

    def test_observations(self):
        group = self.session.query(model.IndicatorGroup)\
            .filter(model.IndicatorGroup.id == 'GINDIPFRI0')\
            .first()
        self.assertTrue(len(group.observations) == 2)
        obs_ids = [obs.id for obs in group.observations]
        self.assertTrue("OBSIPFRI2599" in obs_ids)
        self.assertTrue("OBSIPFRI2598" in obs_ids)


class ObservationsTest(ReceiverParserTest):
    """Observation tests"""
    def test_indicator(self):
        obs = self.session.query(model.Observation) \
            .filter(model.Observation.id == 'OBSIPFRI1')\
            .first()
        self.assertTrue(obs.indicator.id == 'INDIPFRI1')

    def test_computation(self):
        obs = self.session.query(model.Observation)\
            .filter(model.Observation.id == "OBSIPFRI1")\
            .first()
        computation = obs.computation.uri
        self.assertTrue(computation == "purl.org/weso/ontology/computex#Raw")

    def test_value(self):
        obs = self.session.query(model.Observation)\
            .filter(model.Observation.id == "OBSIPFRI2597")\
            .first()
        self.assertTrue(obs.value.value == "26.5")
        self.assertTrue(obs.value.obs_status ==\
            "http://purl.org/linked-data/sdmx/2009/code#obsStatus-A")

    def test_missing_value(self):
        obs = self.session.query(model.Observation)\
            .filter(model.Observation.id == "OBSIPFRI0")\
            .first()
        self.assertTrue(obs.value.obs_status ==\
            "http://purl.org/linked-data/sdmx/2009/code#obsStatus-M")
        self.assertTrue(obs.value.value is None)

    def test_month_interval(self):
        obs1 = self.session.query(model.Observation)\
            .filter(model.Observation.id == "OBSIPFRI2599")\
            .first()
        self.assertTrue(obs1.ref_time.type == "monthIntervals")
        self.assertTrue(obs1.ref_time.month == 12)
        self.assertTrue(obs1.ref_time.year == 2013)
        self.assertTrue(str(obs1.ref_time.start_time) == "2013-12-01")
        self.assertTrue(str(obs1.ref_time.end_time) == "2014-01-01")

    def test_year(self):
        obs = self.session.query(model.Observation)\
            .filter(model.Observation.id == "OBSIPFRI2597")\
            .first()
        self.assertTrue(obs.ref_time.type == "yearIntervals")
        self.assertTrue(obs.ref_time.year == 2013)
        self.assertTrue(str(obs.ref_time.start_time) == "2013-01-01")
        self.assertTrue(str(obs.ref_time.end_time) == "2014-01-01")

    def test_interval(self):
        obs = self.session.query(model.Observation)\
            .filter(model.Observation.id == "OBSIPFRI0")\
            .first()
        self.assertTrue(obs.ref_time.type == "intervals")
        self.assertTrue(str(obs.ref_time.start_time) == "1990-01-01")
        self.assertTrue(str(obs.ref_time.end_time) == "1993-01-01")

    def test_group(self):
        observations = self.session.query(model.Observation)\
            .filter(model.Observation.indicator_group_id == "GINDIPFRI0")\
            .all()
        self.assertTrue(len(observations) == 2)
        observation_ids = [obs.id for obs in observations]
        self.assertTrue("OBSIPFRI2598" in observation_ids)
        self.assertTrue("OBSIPFRI2599" in observation_ids)


class OrganizationsTest(ReceiverParserTest):
    """Observation tests"""
    def test_number(self):
        organizations = self.session.query(model.Organization).all()
        self.assertTrue(len(organizations) == 1)

    def test_organization_name(self):
        org = self.session.query(model.Organization) \
            .filter(model.Organization.id == 'http://www.ifpri.org/') \
            .first()
        self.assertTrue('IFPRI' in org.name)

    def test_organization_users(self):
        org = self.session.query(model.Organization) \
            .filter(model.Organization.id == "http://www.ifpri.org/") \
            .first()
        self.assertTrue(org.users)


class UsersTest(ReceiverParserTest):
    """User tests"""
    def test_number(self):
        users = self.session.query(model.User).all()
        self.assertTrue(len(users) == 1)

    def test_user_name(self):
        user = self.session.query(model.User)\
            .filter(model.User.id == "USRIPFRIIMPORTER")\
            .first()
        self.assertTrue(user is not None)
        self.assertTrue(user.timestamp is not None)

    def test_organization(self):
        user = self.session.query(model.User)\
            .filter(model.User.id == "USRIPFRIIMPORTER")\
            .first()
        self.assertTrue(user.organization.id == "http://www.ifpri.org/")


class DataSourceTests(ReceiverParserTest):
    """DataSource tests"""
    def test_number(self):
        datasources = self.session.query(model.DataSource).all()
        self.assertTrue(len(datasources) == 1)

    def test_name(self):
        dsource = self.session.query(model.DataSource).first()
        self.assertTrue('IFPRI' in dsource.name)

    def test_organization(self):
        dsource = self.session.query(model.DataSource).first()
        self.assertTrue(dsource.organization.id == "http://www.ifpri.org/")

    def test_datasets(self):
        dsource = self.session.query(model.DataSource).first()
        self.assertTrue(len(dsource.datasets) == 1)


class DatasetTests(ReceiverParserTest):
    """Dataset tests"""
    def test_number(self):
        datasets = self.session.query(model.Dataset).all()
        self.assertTrue(len(datasets) == 1)

    def test_datasource(self):
        dataset = self.session.query(model.Dataset).first()
        self.assertTrue('IFPRI' in dataset.datasource.name)

    def test_license(self):
        dataset = self.session.query(model.Dataset).first()
        self.assertTrue(dataset.license.republish)

    def test_indicators(self):
        dataset = self.session.query(model.Dataset).first()
        self.assertTrue(len(dataset.indicators) == 4)

    def test_frequency(self):
        dataset = self.session.query(model.Dataset).first()
        self.assertTrue(dataset.sdmx_frequency ==\
            'http://test_ontology.org/frequency')


class SliceParserTest(ReceiverParserTest):
    """Slice tests"""
    def test_numbrer(self):
        slices = self.session.query(model.Slice).all()
        self.assertTrue(len(slices) == 3)

    def test_indicator(self):
        sli = self.session.query(model.Slice)\
            .filter(model.Slice.id == 'SLIIPFRI0')\
            .first()
        self.assertTrue(sli is not None)
        self.assertTrue(sli.indicator.id == 'INDIPFRI0')

    def test_dataset(self):
        sli = self.session.query(model.Slice)\
            .filter(model.Slice.id == 'SLIIPFRI0')\
            .first()
        self.assertTrue(sli.dataset is not None)

    def test_observations(self):
        sli = self.session.query(model.Slice)\
            .filter(model.Slice.id == 'SLIIPFRI0').first()
        self.assertTrue(sli.observations)
        obs_ids = [obs.id for obs in sli.observations]
        self.assertTrue("OBSIPFRI0" in obs_ids)

    def test_dimension_time(self):
        """A slice dimension may be a time."""
        sli = self.session.query(model.Slice)\
            .filter(model.Slice.id == "SLIIPFRI2")\
            .first()
        self.assertTrue(str(sli.dimension.start_time) == "1999-01-01")
        self.assertTrue(str(sli.dimension.end_time) == "2002-01-01")

    def test_dimension_region_uncode(self):
        """A slice dimension may be a region. The region can be declared using
        its UN_CODE."""
        sli = self.session.query(model.Slice)\
            .filter(model.Slice.id == 'SLIIPFRI0')\
            .first()
        self.assertTrue(sli.dimension.iso3 == 'ESP')

    def test_dimension_region_iso3(self):
        """A slice dimension may be a region. The region can be declared using
        its ISO3 code."""
        sli = self.session.query(model.Slice)\
            .filter(model.Slice.id == "SLIIPFRI1")\
            .first()
        self.assertTrue(sli.dimension.iso3 == "FRA")

if __name__ == '__main__':
    unittest.main()
