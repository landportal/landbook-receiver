import app
import model.models as model
import datetime
from parser import Parser


class ReceiverSQLService(object):
    def __init__(self, content):
        self.parser = Parser(content)
        self.time = datetime.datetime.now()

    def store_data(self, user_ip):
        session = app.db.session
        try:
            self._store_data(user_ip, session)
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()

    def _store_data(self, user_ip, session):
        dataset = self._store_metadata(user_ip, session)
        session.flush()
        # Store indicators
        self._store_simple_indicators(dataset, session)
        self._store_compound_indicators(dataset, session)
        self._store_indicator_relationships(session)
        self._store_indicator_groups(session)
        # Store observations
        self._store_observations(dataset, session)
        # Store slices
        self._store_slices(dataset, session)

    def _store_simple_indicators(self, dataset, session):
        def enrich_indicator(ind):
            ind.starred = DBHelper.check_indicator_starred(session, ind.id)
            ind.last_update = self.time
            return ind

        for item in self.parser.get_simple_indicators():
            indicator = session.merge(enrich_indicator(item))
            dataset.add_indicator(indicator)
        session.flush()

    def _store_compound_indicators(self, dataset, session):
        def enrich_indicator(ind):
            ind.starred = DBHelper.check_indicator_starred(session, ind.id)
            ind.last_update = self.time
            for rel in DBHelper.find_indicators(session, ind.related_id):
                rel.compound_indicator_id = ind.id
            return ind

        for item in self.parser.get_compound_indicators():
            indicator = session.merge(enrich_indicator(item))
            dataset.add_indicator(indicator)
        session.flush()

    def _store_indicator_groups(self, session):
        for group in self.parser.get_indicator_groups():
            indicator_ref = DBHelper.find_compound_indicator(session, group.indicator_ref)
            indicator_ref.indicator_ref_group_id = group.id
            session.merge(group)
        session.flush()

    def _store_indicator_relationships(self, session):
        indicators = self.parser.get_simple_indicators()
        for ind in indicators:
            # Each indicator may be related with others
            # The related_id field was created in the parser and WILL NOT be
            # persisted, it is only used to create the relationship objects
            relationships = []
            for rel_id in ind.related_id:
                rel = model.IndicatorRelationship()
                rel.source_id = ind.id
                rel.target_id = rel_id
                relationships.append(rel)
            session.add_all(relationships)
        session.flush()

    def _store_metadata(self, user_ip, session):
        datasource = self.parser.get_datasource()
        dataset = self.parser.get_dataset()
        organization = self.parser.get_organization()
        user = self.parser.get_user()
        user.ip = user_ip
        user.organization = organization
        datasource.organization = organization
        dataset.datasource = datasource
        return session.merge(dataset)

    def _store_observations(self, dataset, session):
        def enrich_observation(obs):
            obs.dataset_id = dataset.id
            if obs.region_code is not None:
                obs.region_id = DBHelper.find_region_id(session, obs.region_code)
            elif obs.country_code is not None:
                obs.region_id = DBHelper.find_country_id(session, obs.country_code)
            return obs

        for observation in self.parser.get_observations():
            session.add(enrich_observation(observation))
        session.flush()
        session.expunge_all()

    def _store_slices(self, dataset, session):
        def enrich_slice(sli):
            sli.dataset_id = dataset.id
            for rel_obs in DBHelper.find_observations(session, sli.observation_ids):
                rel_obs.slice_id = sli.id
            if sli.region_code is not None:
                sli.dimension_id = DBHelper.find_region_id(session, sli.region_code)
            elif sli.country_code is not None:
                sli.dimension_id = DBHelper.find_country_id(session, sli.country_code)
            return sli

        for slice in self.parser.get_slices():
            session.add(enrich_slice(slice))
        session.flush()
        session.expunge_all()


class DBHelper(object):
    @staticmethod
    def check_datasource(session, datasource_name):
        """Find a DataSource by name in the DB. Returns None if not found."""
        datasource = session.query(model.DataSource)\
            .filter(model.DataSource.name == datasource_name)\
            .first()
        return datasource

    @staticmethod
    def check_indicator_starred(session, indicator_id):
        """Check if an Indicator is starred"""
        indicator = session.query(model.Indicator)\
            .filter(model.Indicator.id == indicator_id)\
            .first()
        return indicator.starred if indicator is not None else False

    @staticmethod
    def find_region_id(session, reg_code):
        """Get the Region ID using its UN_CODE"""
        region = session.query(model.Region)\
            .filter(model.Region.un_code == reg_code)\
            .first()
        if region is None:
            raise Exception("The region with UN_CODE = {} does not exist in "
                            "the database".format(reg_code))
        else:
            return region.id

    @staticmethod
    def find_country_id(session, country_code):
        """Get the Country ID using its ISO3"""
        country = session.query(model.Country)\
            .filter(model.Country.iso3 == country_code)\
            .first()
        if country is None:
            raise Exception("The country with ISO3 = {} does not exist in "
                            "the database".format(country_code))
        else:
            return country.id

    @staticmethod
    def find_observations(session, ids):
        """Get all observations in a list of IDs"""
        return session.query(model.Observation)\
            .filter(model.Observation.id.in_(ids))\
            .all()

    @staticmethod
    def find_indicators(session, ids):
        """Get all indicators in a list of IDs"""
        return session.query(model.Indicator)\
            .filter(model.Indicator.id.in_(ids))\
            .all()

    @staticmethod
    def find_compound_indicator(session, ind_id):
        """Get a compound indicator by its ID"""
        return session.query(model.CompoundIndicator)\
            .filter(model.CompoundIndicator.id == ind_id)\
            .first()
