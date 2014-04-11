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
        # Store dataset metadata
        datasource = self.metadata_serv.get_datasource()
        dataset = self.metadata_serv.get_dataset()
        organization = self.metadata_serv.get_organization()
        user = self.metadata_serv.get_user(ip=user_ip)
        session.add(datasource)
        session.add(dataset)
        session.add(organization)
        session.add(user)
        session.flush()
        datasource.organization_id = organization.id
        dataset.datasource_id = datasource.id
        user.organization_id = organization.id
        # Store indicators
        self.store_indicators(dataset, session)
        session.flush()
        # Store observations
        observations = self.observation_serv.get_observations()
        session.add_all(observations)
        for obs in observations:
            obs.dataset_id = dataset.id
            # The region_code field was created in the parser and WILL NOT be
            # persisted, it is only used to link with the corresponding region
            if obs.region_code is not None:
                region = self.get_region_by_uncode(session, obs.region_code)
                if region is not None:
                    obs.region_id = region.id
            obs.indicator = session.query(model.Indicator).filter(model.Indicator.id == obs.indicator_id).first()
            obs.indicator_id = None
            obs.indicator_group = session.query(model.IndicatorGroup).filter(model.IndicatorGroup.id == obs.indicator_group_id).first()
            obs.indicator_group_id = None
        # Store slices
        slices = self.slice_serv.get_slices()
        session.add_all(slices)
        for sli in slices:
            sli.dataset_id = dataset.id
            sli.indicator = session.query(model.Indicator).filter(model.Indicator.id == sli.indicator_id).first()
            sli.indicator_id = None
            # The region_iso3 field was created in the parser and WILL NOT be
            # peristed, it is only used to link with the corresponding region
            if sli.region_code is not None:
                region = self.get_region_by_uncode(session, sli.region_code)
                sli.dimension = region
            # The observation_ids list was created in the parser and WILL NOT be
            # persisted. The list is only used here to link with the observatios
            for obs_id in sli.observation_ids:
                #related_obs = next((obs for obs in observations
                #                    if obs.id == obs_id), None)
                related_obs = session.query(model.Observation).filter(model.Observation.id == obs_id).first()
                sli.observations.append(related_obs)

    def get_region_by_uncode(self, session, un_code):
        if un_code is not None:
            return session.query(model.Region)\
                    .filter(model.Region.un_code == un_code).first()
        else:
            return None

    def store_indicator_groups(self, session, compounds):
        groups = self.indicator_serv.get_indicator_groups()
        session.add_all(groups)
        for group in groups:
            indicator_ref = next((comp for comp in compounds if comp.id == group.indicator_ref), None)
            indicator_ref.indicator_ref_group = group
        return groups

    def store_indicators(self, dataset, session):
        indicators = self.indicator_serv.get_simple_indicators()
        compounds = self.indicator_serv.get_compound_indicators()
        session.add_all(indicators + compounds)

        for ind in indicators + compounds:
            dataset.add_indicator(ind)

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

        for ind in compounds:
            # The related_id field was created in the parser and WILL NOT be
            # persisted to the database. It is used to link the simple
            # indicators with its compound indicator
            for id in ind.related_id:
                related = next((rel for rel in indicators if rel.id == id), None)
                ind.indicator_refs.append(related)
        self.store_indicator_groups(session, compounds)



