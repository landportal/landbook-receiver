import parser
import requests
import model.models as model
import datetime
import app


class IndicatorSQLService(object):
    def __init__(self, content):
        self._parser = parser.Parser(content)
        self._time = datetime.datetime.now()
        self._dbhelper = DBHelper()

    def get_simple_indicators(self):
        indicators = self._parser.get_simple_indicators()
        #Enrich the indicators data querying the API to get its starred state
        #and setting the last_update field
        for ind in indicators:
            #ind.starred = APIHelper().check_indicator_starred(ind.id)
            ind.starred = self._dbhelper.check_indicator_starred(ind.id)
            ind.last_update = self._time
        return indicators

    def get_compound_indicators(self):
        compounds = self._parser.get_compound_indicators()
        for comp in compounds:
            #comp.starred = APIHelper().check_indicator_starred(comp.id)
            comp.starred = self._dbhelper.check_indicator_starred(comp.id)
            comp.last_update = self._time
        return compounds

    def get_indicator_groups(self):
        return self._parser.get_indicator_groups()


class ObservationSQLService(object):
    def __init__(self, content):
        self._parser = parser.Parser(content)
        self._dbhelper = DBHelper()

    def get_observations(self):
        observations = self._parser.get_observations()
        # Enrich the observations linking them to its corresponding region.
        for obs in observations:
            if obs.region_code is not None:
                #obs.region_id = APIHelper().find_region_id(obs.region_code)
                obs.region_id = self._dbhelper.find_region_id(obs.region_code)
            elif obs.country_code is not None:
                #obs.region_id = APIHelper().find_country_id(obs.country_code)
                obs.region_id = self._dbhelper.find_country_id(obs.country_code)
        return observations


class MetadataSQLService(object):
    """Provides access to the dataset metadata
    """
    def __init__(self, content):
        self._parser = parser.Parser(content)
        self._dbhelper = DBHelper()

    def get_user(self, ip):
        """Return the User object representing the dataset user"""
        user = self._parser.get_user()
        user.ip = ip
        return user

    def get_organization(self):
        return self._parser.get_organization()

    def get_datasource(self):
        datasource = self._parser.get_datasource()
        # Check if the datasource already exists in the database
        #other = APIHelper().check_datasource(datasource.name)
        other = self._dbhelper.check_datasource(datasource.name)
        return other if other is not None else datasource

    def get_dataset(self):
        return self._parser.get_dataset()


class SliceSQLService(object):
    def __init__(self, content):
        self._parser = parser.Parser(content)
        self._dbhelper = DBHelper()

    def get_slices(self):
        #return self._parser.get_slices()
        # Enrich the slices linking the to its correspoding dimension. If the
        # dimension is a Time, it comes already linked from the parser.
        slices = self._parser.get_slices()
        for sli in slices:
            if sli.region_code is not None:
                #sli.dimension_id = APIHelper().find_region_id(sli.region_code)
                sli.dimension_id = self._dbhelper.find_region_id(sli.region_code)
            elif sli.country_code is not None:
                #sli.dimension_id = APIHelper().find_country_id(sli.country_code)
                sli.dimension_id = self._dbhelper.find_country_id(sli.country_code)
        return slices


class DBHelper(object):
    def __init__(self):
        self.session = app.db.session

    def check_datasource(self, datasource_name):
        """Find a DataSource in the DB. Returns None if not found."""
        datasource = self.session.query(model.DataSource)\
                .filter(model.DataSource.name == datasource_name)\
                .first()
        return self._make_datasource(datasource) if datasource is not None else None

    def _make_datasource(self, datasource_data):
        datasource = model.DataSource()
        datasource.name = str(datasource_data['name'])
        datasource.id = int(datasource_data['id'])
        datasource.organization_id = str(datasource_data['organization_id'])
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
            raise Exception("The region with UN_CODE = {} does not exist in the database".format(reg_code))
        else:
            return region.id

    def find_country_id(self, country_code):
        """Get the Country ID using its ISO3"""
        country = self.session.query(model.Country)\
                .filter(model.Country.iso3 == country_code)\
                .first()
        if country is None:
            raise Exception("The country with ISO3 = {} does not exist in the database".format(country_code))
        else:
            return country.id


"""
class APIHelper(object):
    def __init__(self):
        self.api_url = "http://localhost:80/api"

    def check_datasource(self, datasource_name):
        r = requests.get('{}/datasources'.format(self.api_url))
        # The data comes in JSON format
        datasources = r.json()
        # Find the JSON object with the required name
        datasource = next((dat for dat in datasources\
                if str(dat['name']) == datasource_name), None)
        # Return the JSON object as a Datasource object
        if datasource is None:
            return None
        else:
            return self._make_datasource(datasource)

    def _make_datasource(self, datasource_data):
        datasource = model.DataSource()
        datasource.name = str(datasource_data['name'])
        datasource.id = int(datasource_data['id'])
        datasource.organization_id = str(datasource_data['organization_id'])
        return datasource

    def check_indicator_starred(self, indicator_id):
        r = requests.get('{}/indicators/{}'.format(self.api_url, indicator_id))
        #We may ask for an indicator that does not exist in the database, so
        #if it exists we return its starred value, and if it does not exist
        #(KeyError) we return False because it is being inserted in the DB for
        #the first time
        try:
            return r.json()["starred"]
        except KeyError:
            return False

    def find_region_id(self, reg_code):
        r = requests.get("{}/regions/{}".format(self.api_url, reg_code))
        try:
            return r.json()["id"]
        except KeyError:
            # The region does not exist on the database.
            # This dataset has invalid data
            raise Exception("The region with UN_CODE = {} does not exist in "\
                    "the database".format(reg_code))
        
    def find_country_id(self, country_code):
        r = requests.get("{}/countries/{}".format(self.api_url, country_code))
        try:
            return r.json()["id"]
        except KeyError:
            # The country does not exist on the database.
            # This dataset has invalid data
            raise Exception("The country with ISO3 = {} does not exist in "\
                    "the database".format(country_code))
"""