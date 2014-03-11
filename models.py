"""
Created on 03/02/2014

@author: Herminio
"""
import sqlalchemy
from sqlalchemy.sql.schema import Column, ForeignKey, Sequence
from sqlalchemy.sql.sqltypes import Integer, String, TIMESTAMP, BOOLEAN
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from abc import abstractmethod

engine = sqlalchemy.create_engine('sqlite://', echo=False)
Base = declarative_base()

class User(Base):
    """
    User model object
    """
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    id_source = Column(String(255))
    ip = Column(String(50))
    timestamp = Column(TIMESTAMP)
    organization_id = Column(Integer, ForeignKey('organizations.id'))
    organization = relationship("Organization", backref="users")

    def __init__(self, id=None, id_source=None, ip=None, timestamp=None, organization_id=None):
        """
        Constructor for user model object
        """
        self.id = id
        self.id_source = id_source
        self.ip = ip
        self.timestamp = timestamp
        self.organization_id = organization_id


class Organization(Base):
    """
    classdocs
    """
    __tablename__ = "organizations"
    id = Column(Integer, primary_key=True)
    id_source = Column(String(255))
    name = Column(String(128))
    url = Column(String(255))
    is_part_of_id = Column(Integer, ForeignKey("organizations.id"))
    is_part_of = relationship("Organization", uselist=False, foreign_keys=is_part_of_id)

    def __init__(self, id_source=None, name=None, url=None, is_part_of=None):
        """
        Constructor
        """
        self.id_source = id_source
        self.name = name
        self.url = url
        self.is_part_of = is_part_of
        self.data_sources = []

    def add_data_source(self, data_source):
        self.data_sources.append(data_source)
        data_source.organization = self



class DataSource(Base):
    """
    classdocs
    """
    __tablename__ = "datasources"
    id = Column(Integer, primary_key=True)
    id_source = Column(String(255))
    name = Column(String(128))
    organization_id = Column(Integer, ForeignKey("organizations.id"))
    organization = relationship("Organization", backref="sources")

    def __init__(self, id=None, id_source=None, name=None, organization=None):
        """
        Constructor
        """
        self.id_source = id_source
        self.id = id
        self.name = name
        self.organization = organization
        self.datasets = []
        self.observations = []

    def add_dataset(self, dataset):
        self.datasets.append(dataset)
        dataset.source = self

    def add_observation(self, observation):
        self.observations.append(observation)
        observation.provider = self


class Dataset(Base):
    """
    classdocs
    """
    __tablename__ = 'datasets'
    id = Column(Integer, primary_key=True)
    id_source = Column(String(255))
    name = Column(String(60))
    sdmx_frequency = Column(Integer)
    datasource_id = Column(Integer, ForeignKey("datasources.id"))
    datasource = relationship("DataSource", backref="datasets")
    license_id = Column(Integer, ForeignKey("licenses.id"))
    license = relationship("License")

    def __init__(self, id=None, id_source=None, name=None, frequency=None, source=None):
        """
        Constructor
        """
        self.id = id
        self.id_source = id_source
        self.name = name
        self.frequency = frequency
        self.source = source
        self.slices = []

    def add_slice(self, data_slice):
        self.slices.append(data_slice)
        data_slice.dataset = self


class Slice(Base):
    """
    classdocs
    """
    __tablename__ = "slices"
    id = Column(Integer, primary_key=True)
    id_source = Column(String(255))
    indicator_id = Column(Integer, ForeignKey("indicators.id"))
    indicator = relationship("Indicator")
    dimension_id = Column(Integer, ForeignKey("dimensions.id"))
    dimension = relationship("Dimension")
    dataset_id = Column(Integer, ForeignKey("datasets.id"))
    dataset = relationship("Dataset", backref="slices")
    observation = relationship("Observation")

    def __init__(self, id=None, id_source=None, dimension=None, dataset=None, indicator=None):
        """
        Constructor
        """
        self.id_source = id_source
        self.dataset = dataset
        self.indicator = indicator
        self.id = id
        self.dimension = dimension
        self.observations = []

    def add_observation(self, observation):
        self.observations.append(observation)
        observation.data_slice = self


class Observation(Base):
    """
    classdocs
    """
    __tablename__ = "observations"
    id = Column(Integer, primary_key=True)
    id_source = Column(String(255))
    ref_time_id = Column(Integer, ForeignKey("times.id"))
    ref_time = relationship("Time", foreign_keys=ref_time_id, uselist=False)
    issued_id = Column(Integer, ForeignKey("instants.id"))
    issued = relationship("Instant", foreign_keys=issued_id, uselist=False)
    computation_id = Column(Integer, ForeignKey("computations.id"))
    computation = relationship("Computation", foreign_keys=computation_id)
    indicator_group_id = Column(Integer, ForeignKey("indicatorGroups.id"))
    indicator_group = relationship("IndicatorGroup", foreign_keys=indicator_group_id)
    value_id = Column(Integer, ForeignKey("values.id"))
    value = relationship("Value", foreign_keys=value_id, uselist=False)
    indicator_id = Column(Integer, ForeignKey("indicators.id"))
    indicator = relationship("Indicator", foreign_keys=indicator_id)
    dataset_id = Column(Integer, ForeignKey("datasets.id"))
    dataset = relationship("Dataset", foreign_keys=dataset_id, backref="observations")
    region_id = Column(Integer, ForeignKey("regions.id"))
    slice_id = Column(Integer, ForeignKey("slices.id"))


    def __init__(self, id=None, id_source=None, ref_time=None, issued=None,
                 computation=None, value=None, indicator=None, provider=None):
        """
        Constructor
        """
        self.id = id
        self.id_source = id_source
        self.ref_time = ref_time
        self.issued = issued
        self.computation = computation
        self.value = value
        self.indicator = indicator
        self.provider = provider

    def __str__(self):
        return "<Observation(id_source='%s', ref_time='%s', issued='%s', " \
               "computation='%s', value='%s', indicator='%s', provider='%s')>" % \
               (self.id_source, self.ref_time, self.issued, self.computation,
                self.value, self.indicator, self.provider)


class Indicator(Base):
    """
    classdocs
    """
    __tablename__ = "indicators"
    id = Column(Integer, Sequence('indicator_id_seq'), primary_key=True)
    id_source = Column(String(255))
    name = Column(String(50))
    description = Column(String(255))
    measurement_unit_id = Column(String(20), ForeignKey("measurementUnits.name"))
    measurement_unit = relationship("MeasurementUnit")
    dataset_id = Column(Integer, ForeignKey('datasets.id'))
    dataset = relationship("Dataset", backref="indicators")
    #compound_indicator_id = Column(Integer, ForeignKey("compoundIndicators.id")) #circular dependency
    type = Column(String(50))

    __mapper_args__ = {
        'polymorphic_identity': 'indicators',
        'polymorphic_on': type
    }

    def __init__(self, id_source, name, description, measurement_unit_id=0, dataset_id=0, compound_indicator_id=0):
        self.id_source = id_source
        self.name = name
        self.description = description
        self.measurement_unit_id = measurement_unit_id
        self.dataset_id = dataset_id
        self.compound_indicator_id = compound_indicator_id

    def __str__(self):
        return "<Indicator(id='%s', id_source='%s', name='%s', description='%s', " \
               "measurement_unit_id='%s', dataset_id='%s', type='%s')>" % \
               (self.id, self.id_source, self.name, self.description, self.measurement_unit_id,
                self.dataset_id, self.type)

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        if isinstance(other, Indicator):
            return self.id == other.id
        else:
            return False


class IndicatorGroup(Base):
    """
    classdocs
    """
    __tablename__ = "indicatorGroups"
    id = Column(Integer, primary_key=True)
    observations = relationship("Observation")

    __mapper_args__ = {
        'polymorphic_identity': 'indicatorGroups',
    }


class MeasurementUnit(Base):
    """
    classdocs
    """
    __tablename__ = "measurementUnits"
    name = Column(String(20), primary_key=True)

    def __init__(self, name=None):
        """
        Constructor
        """
        self.name = name

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        if isinstance(other, MeasurementUnit):
            return self.name == other.name
        else:
            return False


class License(Base):
    """
    classdocs
    """
    __tablename__ = "licenses"
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    description = Column(String(255))
    republish = Column(BOOLEAN)
    url = Column(String(128))

    def __init__(self, name=None, description=None, republish=None, url=None):
        """
        Constructor
        """
        self.name = name
        self.description = description
        self.republish = republish
        self.url = url


class Computation(Base):
    """
    classdocs
    """
    __tablename__ = "computations"
    id = Column(Integer, primary_key=True)
    uri = Column(String(60))

    def __init__(self, uri=None):
        """
        Constructor
        """
        self.uri = uri


class Value(Base):
    """
    classdocs
    """
    __tablename__ = "values"
    id = Column(Integer, primary_key=True)
    obs_status = Column(String(50))
    value_type = Column(String(50))
    value = Column(String(50))

    def __init__(self, obs_status=None):
        """
        Constructor
        """
        self.obs_status = obs_status


class IndicatorRelationship(Base):
    """
    classdocs
    """
    __tablename__ = "indicatorRelationships"
    id = Column(Integer, primary_key=True)
    source_id = Column(Integer, ForeignKey("indicators.id"))
    source = relationship("Indicator", foreign_keys=source_id)
    target_id = Column(Integer, ForeignKey("indicators.id"))
    target = relationship("Indicator", foreign_keys=target_id)
    type = Column(String(50))

    __mapper_args__ = {
        'polymorphic_identity': 'indicatorRelationships',
        'polymorphic_on': type
    }

    def __init__(self, source=None, target=None):
        """
        Constructor
        """
        self.source = source
        self.target = target


class IsPartOf(IndicatorRelationship):
    """
    classdocs
    """
    __tablename__ = "ispartof"
    id = Column(Integer, ForeignKey("indicatorRelationships.id"), primary_key=True)
    source_id = Column(Integer, ForeignKey("indicators.id"))
    target_id = Column(Integer, ForeignKey("indicators.id"))

    __mapper_args__ = {
        'polymorphic_identity': 'ispartof',
    }


    def __init__(self, source=None, target=None):
        """
        Constructor
        """
        super(IsPartOf, self).__init__(source, target)


class Becomes(IndicatorRelationship):
    """
    classdocs
    """
    __tablename__ = "becomes"
    id = Column(Integer, ForeignKey("indicatorRelationships.id"), primary_key=True)
    source_id = Column(Integer, ForeignKey("indicators.id"))
    target_id = Column(Integer, ForeignKey("indicators.id"))

    __mapper_args__ = {
        'polymorphic_identity': 'becomes',
    }

    def __init__(self, source=None, target=None):
        """
        Constructor
        """
        super(Becomes, self).__init__(source, target)


class Dimension(Base):
    """
    classdocs
    """
    __tablename__ = "dimensions"
    id = Column(Integer, primary_key=True)
    type = Column(String(50))

    __mapper_args__ = {
        'polymorphic_identity': 'dimensions',
        'polymorphic_on': type
    }

    @abstractmethod
    def get_dimension_string(self): pass


class Time(Dimension):
    """
    classdocs
    """
    __tablename__ = "times"
    id = Column(Integer, ForeignKey("dimensions.id"), primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity': 'times',
    }

    @abstractmethod
    def get_time_string(self): pass

    def get_dimension_string(self):
        return self.get_time_string()


class Instant(Time):
    """
    classdocs
    """
    __tablename__ = "instants"
    id = Column(Integer, ForeignKey("times.id"), primary_key=True)
    timestamp = Column(TIMESTAMP)

    __mapper_args__ = {
        'polymorphic_identity': 'instants',
    }

    def __init__(self, instant=None):
        """
        Constructor
        """
        self.instant = instant

    def get_time_string(self):
        return self.instant.strftime("%Y-%m-%dT%H:%M:%S")


class Interval(Time):
    """
    classdocs
    """
    __tablename__ = "intervals"
    id = Column(Integer, ForeignKey("times.id"), primary_key=True)
    start_time = Column(sqlalchemy.Time)
    end_time = Column(sqlalchemy.Time)

    __mapper_args__ = {
        'polymorphic_identity': 'intervals',
    }

    def __init__(self, start_time=None, end_time=None):
        """
        Constructor
        """
        self.start_time = start_time
        self.end_time = end_time

    def get_time_string(self):
        return str(self.start_time) + '-' + str(self.end_time)


class YearInterval(Interval):
    """
    classdocs
    """
    __tablename__ = "yearIntervals"
    id = Column(Integer, ForeignKey("intervals.id"), primary_key=True)
    start_time = Column(sqlalchemy.Time)
    end_time = Column(sqlalchemy.Time)
    year = Column(Integer)

    __mapper_args__ = {
        'polymorphic_identity': 'yearIntervals',
    }

    def __init__(self, start_time=None, end_time=None, year=None):
        """
        Constructor
        """
        super(YearInterval, self).__init__(start_time, end_time)
        self.year = year

    def get_time_string(self):
        return str(self.year)


class Region(Dimension):
    """
    classdocs
    """
    __tablename__ = "regions"
    id = Column(Integer, ForeignKey("dimensions.id"), primary_key=True)
    name = Column(String(128))
    is_part_of_id = Column(Integer, ForeignKey("regions.id"))
    is_part_of = relationship("Region", uselist=False, foreign_keys=is_part_of_id)
    observations = relationship("Observation")

    __mapper_args__ = {
        'polymorphic_identity': 'regions',
    }

    def __init__(self, name=None, is_part_of=None):
        """
        Constructor
        """
        self.name = name
        self.is_part_of = is_part_of
        self.observations = []

    def add_observation(self, observation):
        self.observations.append(observation)
        observation.region = self

    def get_dimension_string(self):
        return self.name


class Country(Region):
    """
    classdocs
    """
    __tablename__ = "countries"
    id = Column(Integer, ForeignKey("regions.id"), primary_key=True)
    faoURI = Column(String(128))
    iso2 = Column(String(10))
    iso3 = Column(String(10))
    name = Column(String(128))

    __mapper_args__ = {
        'polymorphic_identity': 'countries',
    }

    def __init__(self, name=None, iso2=None, iso3=None, fao_URI=None, is_part_of=None):
        """
        Constructor
        """
        super(Country, self).__init__(name, is_part_of)
        self.iso2 = iso2
        self.iso3 = iso3
        self.fao_URI = fao_URI

    def get_dimension_string(self):
        return self.iso3


class CompoundIndicator(Indicator):
    """
    classdocs
    """
    __tablename__ = "compoundIndicators"
    id = Column(Integer, ForeignKey("indicators.id"),
                primary_key=True)  #there should be a foreign, but there is not due to indicator_ref relationship
    indicator_id = Column(Integer)
    name = Column(String(50))
    description = Column(String(255))
    measurement_unit_id = Column(String(20), ForeignKey("measurementUnits.name"))
    dataset_id = Column(Integer, ForeignKey("datasets.id"))
    #indicator_refs = relationship("Indicator") #circular dependency
    indicator_ref_group_id = Column(Integer, ForeignKey("indicatorGroups.id"))
    indicator_ref_group = relationship("IndicatorGroup", foreign_keys=indicator_ref_group_id, uselist=False,
                                       backref="compound_indicator")

    __mapper_args__ = {
        'polymorphic_identity': 'compoundIndicators',
    }

Base.metadata.create_all(engine)