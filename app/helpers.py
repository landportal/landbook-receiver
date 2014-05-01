import parser
import model.models as model
import datetime
import app
#from memory_profiler import profile


class IndicatorSQLService(object):
    def __init__(self, content):
        self._parser = parser.Parser(content)
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


class ObservationSQLService(object):
    def __init__(self, content):
        self._parser = parser.Parser(content)
        self._dbhelper = DBHelper()

    #@profile
    def get_observations(self):
        return (self._enrich_observation(obs) for obs
                in self._parser.get_observations())

    def _enrich_observation(self, obs):
        if obs.region_code is not None:
            obs.region_id = self._dbhelper.find_region_id(obs.region_code)
        elif obs.country_code is not None:
            obs.region_id = self._dbhelper.find_country_id(obs.country_code)
        return obs


class MetadataSQLService(object):
    """Provides access to the dataset metadata
    """
    def __init__(self, content):
        self._parser = parser.Parser(content)
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


class SliceSQLService(object):
    def __init__(self, content):
        self._parser = parser.Parser(content)
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
