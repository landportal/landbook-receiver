import helpers
import app


class ReceiverSQLService(object):

    def __init__(self, content):
        parser = helpers.Parser(content)
        self.metadata_serv = helpers.MetadataSQLService(parser)
        self.indicator_serv = helpers.IndicatorSQLService(parser)
        self.observation_serv = helpers.ObservationSQLService(parser)
        self.slice_serv = helpers.SliceSQLService(parser)

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
        for ind in indicators:
            ind.dataset_id = dataset.id
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
        session.commit()
