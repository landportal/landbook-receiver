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
        indicators = self.indicator_serv.get_indicators()
        session.add_all(indicators)
        """
        #for ind in indicators:
        #    ind.dataset_id = dataset.id
        session.flush()
        for id in self.indicator_serv.get_indicators_id():
            ind = session.query(model.Indicator).filter(model.Indicator.id == id).first()
            if ind is not None:
        """
        # Store observations
        observations = self.observation_serv.get_observations()
        session.add_all(observations)
        for obs in observations:
            obs.dataset_id = dataset.id
        # Store slices
        slices = self.slice_serv.get_slices()
        session.add_all(slices)
        for sli in slices:
            sli.dataset_id = dataset.id
            # The region_iso3 field was created in the parser and WILL NOT be
            # peristed, it is only used to link with the corresponding region
            if sli.region_code is not None:
                region = session.query(model.Region)\
                    .filter(model.Region.un_code == sli.region_code).first()
                sli.dimension = region
            # The observation_ids list was created in the parser and WILL NOT be
            # persisted. The list is only used here to link with the observatios
            for obs_id in sli.observation_ids:
                related_obs = next((obs for obs in observations
                                    if obs.id == obs_id), None)
                sli.observations.append(related_obs)
        session.commit()
