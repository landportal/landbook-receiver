import app
import model.models as model
import datetime
from parser import Parser
from memory_profiler import profile


class ReceiverSQLService(object):
    def __init__(self, content):
        parser = Parser(content)
        self.metadata_serv = MetadataHelper(parser)
        self.indicator_serv = IndicatorHelper(parser)
        self.observation_serv = ObservationHelper(parser)
        self.slice_serv = SliceHelper(parser)

    def store_data(self, user_ip):
        session = app.db.session
        try:
            self._store_data(user_ip, session)
            #session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()

    @profile
    def _store_data(self, user_ip, session):
        dataset = self._store_metadata(user_ip, session)
        session.flush()
        # Store indicators
        self._store_simple_indicators(dataset, session)
        session.flush()
        self._store_compound_indicators(dataset, session)
        session.flush()
        self._store_indicator_relationships(session)
        session.flush()
        self._store_indicator_groups(session)
        session.flush()
        session.expunge_all()
        # Store observations
        self._store_observations(dataset, session)
        session.flush()
        session.expunge_all()
        # Store slices
        self._store_slices(dataset, session)
        session.flush()

    def _store_slices(self, dataset, session):
        # The observation_ids list was created in the parser and WILL NOT be
        # persisted. The list is only used here to link with the observations
        for sli in self.slice_serv.get_slices():
            sli.dataset_id = dataset.id
            for rel_obs in session.query(model.Observation)\
                    .filter(model.Observation.id.in_(sli.observation_ids)).all():
                rel_obs.slice_id = sli.id
            session.add(sli)

    def _store_indicator_groups(self, session):
        groups = self.indicator_serv.get_indicator_groups()
        for group in groups:
            indicator_ref = session.query(model.CompoundIndicator)\
                .filter(model.CompoundIndicator.id == group.indicator_ref)\
                .first()
            indicator_ref.indicator_ref_group_id = group.id
            session.merge(group)

    def _store_simple_indicators(self, dataset, session):
        for item in self.indicator_serv.get_simple_indicators():
            ind = session.merge(item)
            dataset.add_indicator(ind)

    def _store_indicator_relationships(self, session):
        indicators = self.indicator_serv.get_simple_indicators()
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

    def _store_compound_indicators(self, dataset, session):
        for item in self.indicator_serv.get_compound_indicators():
            ind = session.merge(item)
            dataset.add_indicator(ind)
            for related in session.query(model.Indicator)\
                    .filter(model.Indicator.id.in_(item.related_id)).all():
                related.compound_indicator_id = ind.id

    def _store_metadata(self, user_ip, session):
        datasource = self.metadata_serv.get_datasource()
        dataset = self.metadata_serv.get_dataset()
        organization = self.metadata_serv.get_organization()
        user = self.metadata_serv.get_user(ip=user_ip)
        user.organization = organization
        datasource.organization = organization
        dataset.datasource = datasource
        return session.merge(dataset)

    @profile
    def _store_observations(self, dataset, session):
        for obs in self.observation_serv.get_observations():
            obs.dataset_id = dataset.id
            session.add(obs)


class IndicatorHelper(object):
    def __init__(self, parser):
        self._parser = parser
        self._time = datetime.datetime.now()
        self._dbhelper = DBHelper()

    def get_simple_indicators(self):
        #indicators = self._parser.get_simple_indicators()
        #Enrich the indicators data querying the API to get its starred state
        #and setting the last_update field
        return (self._enrich_indicator(ind) for ind
                in self._parser.get_simple_indicators())

    def _enrich_indicator(self, ind):
        ind.starred = self._dbhelper.check_indicator_starred(ind.id)
        ind.last_update = self._time
        return ind

    def get_compound_indicators(self):
        return (self._enrich_indicator(ind) for ind
                in self._parser.get_compound_indicators())

    def get_indicator_groups(self):
        return self._parser.get_indicator_groups()


class ObservationHelper(object):
    def __init__(self, parser):
        self._parser = parser
        self._dbhelper = DBHelper()

    @profile
    def get_observations(self):
        return (self._enrich_observation(obs) for obs
                in self._parser.get_observations())

    def _enrich_observation(self, obs):
        if obs.region_code is not None:
            obs.region_id = self._dbhelper.find_region_id(obs.region_code)
        elif obs.country_code is not None:
            obs.region_id = self._dbhelper.find_country_id(obs.country_code)
        return obs


class MetadataHelper(object):
    """Provides access to the dataset metadata
    """
    def __init__(self, parser):
        self._parser = parser
        self._dbhelper = DBHelper()

    def get_user(self, ip):
        user = self._parser.get_user()
        user.ip = ip
        return user

    def get_organization(self):
        return self._parser.get_organization()

    def get_datasource(self):
        datasource = self._parser.get_datasource()
        # Check if the datasource already exists in the database
        other = self._dbhelper.check_datasource(datasource.name)
        return other if other is not None else datasource

    def get_dataset(self):
        return self._parser.get_dataset()


class SliceHelper(object):
    def __init__(self, parser):
        self._parser = parser
        self._dbhelper = DBHelper()

    def get_slices(self):
        # Enrich the slices linking the to its correspoding dimension. If the
        # dimension is a Time, it comes already linked from the parser.
        return (self._enrich_slice(sli) for sli in self._parser.get_slices())

    def _enrich_slice(self, sli):
        if sli.region_code is not None:
            sli.dimension_id = self._dbhelper.find_region_id(sli.region_code)
        elif sli.country_code is not None:
            sli.dimension_id = self._dbhelper.find_country_id(sli.country_code)
        return sli


class DBHelper(object):
    def __init__(self):
        self.session = app.db.session

    def check_datasource(self, datasource_name):
        """Find a DataSource by name in the DB. Returns None if not found."""
        datasource = self.session.query(model.DataSource)\
            .filter(model.DataSource.name == datasource_name)\
            .first()
        return datasource

    def check_indicator_starred(self, indicator_id):
        """Check if an Indicator is starred"""
        indicator = self.session.query(model.Indicator)\
            .filter(model.Indicator.id == indicator_id)\
            .first()
        return indicator.starred if indicator is not None else False

    def find_region_id(self, reg_code):
        """Get the Region ID using its UN_CODE"""
        region = self.session.query(model.Region)\
            .filter(model.Region.un_code == reg_code)\
            .first()
        if region is None:
            raise Exception("The region with UN_CODE = {} does not exist in "
                            "the database".format(reg_code))
        else:
            return region.id

    def find_country_id(self, country_code):
        """Get the Country ID using its ISO3"""
        country = self.session.query(model.Country)\
            .filter(model.Country.iso3 == country_code)\
            .first()
        if country is None:
            raise Exception("The country with ISO3 = {} does not exist in "
                            "the database".format(country_code))
        else:
            return country.id
