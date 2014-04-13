import helpers
import app
import model.models as model


class ReceiverSQLService(object):
    def __init__(self, content):
        self.metadata_serv = helpers.MetadataSQLService(content)
        self.indicator_serv = helpers.IndicatorSQLService(content)
        self.observation_serv = helpers.ObservationSQLService(content)
        self.slice_serv = helpers.SliceSQLService(content)

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
        indicators = self._store_simple_indicators(dataset, session)
        compounds = self._store_compound_indicators(dataset, indicators, session)
        self._store_indicator_relationships(dataset, session)
        groups = self._store_indicator_groups(session, compounds)
        session.flush()
        # Store observations
        observations = self._store_observations(dataset, session)
        session.flush()
        # Store slices
        slices = self._store_slices(dataset, observations, session)
        session.flush()

    def _store_slices(self, dataset, observations, session):
        slices = self.slice_serv.get_slices()
        for sli in slices:
            sli.dataset_id = dataset.id
            # The region_iso3 field was created in the parser and WILL NOT be
            # peristed, it is only used to link with the corresponding region
            if sli.region_code is not None:
                region = self.get_region_by_uncode(session, sli.region_code)
                sli.dimension = region
            # The observation_ids list was created in the parser and WILL NOT be
            # persisted. The list is only used here to link with the observations
            for rel_obs in [obs for obs in observations if obs.id 
                    in sli.observation_ids]:
                rel_obs.slice_id = sli.id
        session.add_all(slices)
        return slices

    def get_region_by_uncode(self, session, un_code):
        if un_code is not None:
            return session.query(model.Region)\
                    .filter(model.Region.un_code == un_code).first()
        else:
            return None

    def _store_indicator_groups(self, session, compounds):
        groups = self.indicator_serv.get_indicator_groups()
        result = []
        for group in groups:
            indicator_ref = next((comp for comp in compounds \
                if comp.id == group.indicator_ref), None)
            indicator_ref.indicator_ref_group_id = group.id
            result.append(session.merge(group))
        return result

    def _store_simple_indicators(self, dataset, session):
        indicators = self.indicator_serv.get_simple_indicators()
        result = []
        for ind in indicators:
            # The db_ind contains the indicator data merged with the database and
            # will be used to link with all the other objects
            db_ind = session.merge(ind)
            session.flush()
            # The indicator may already exist n the DB, so we have to check
            # before the assignment
            if not db_ind.id in [indicator.id for indicator in dataset.indicators]:
                dataset.add_indicator(db_ind)
            result.append(db_ind)
        return result

    def _store_indicator_relationships(self, dataset, session):
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


    def _store_compound_indicators(self, dataset, indicators, session):
        compounds = self.indicator_serv.get_compound_indicators()
        result = []
        for ind in compounds:
            db_ind = session.merge(ind)
            session.flush()
            # The related_id field was created in the parser and WILL NOT be
            # persisted to the database. It is used to link the simple
            # indicators with its compound indicator
            for id in ind.related_id:
                related = next(rel for rel in indicators if rel.id == id)
                related.compound_indicator_id = db_ind.id
            if not db_ind.id in [indicator.id for indicator in dataset.indicators]:
                dataset.add_indicator(db_ind)
            result.append(db_ind)
        return result

    def _store_metadata(self, user_ip, session):
        datasource = self.metadata_serv.get_datasource()
        dataset = self.metadata_serv.get_dataset()
        organization = self.metadata_serv.get_organization()
        user = self.metadata_serv.get_user(ip=user_ip)
        user.organization = organization
        datasource.organization = organization
        dataset.datasource = datasource
        return session.merge(dataset)

    def _store_observations(self, dataset, session):
        observations = self.observation_serv.get_observations()
        for obs in observations:
            obs.dataset_id = dataset.id
            # The region_code field was created in the parser and WILL NOT be
            # persisted, it is only used to link with the corresponding region
            if obs.region_code is not None:
                region = self.get_region_by_uncode(session, obs.region_code)
                if region is not None:
                    obs.region_id = region.id
        session.add_all(observations)
        return observations
