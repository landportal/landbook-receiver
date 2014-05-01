import helpers
import app
import model.models as model
#from memory_profiler import profile


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

    #@profile
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

    #@profile
    def _store_observations(self, dataset, session):
        for obs in self.observation_serv.get_observations():
            obs.dataset_id = dataset.id
            session.add(obs)
