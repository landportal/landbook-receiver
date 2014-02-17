__author__ = 'guillermo'


from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Sequence, create_engine, \
    ForeignKey
from sqlalchemy.orm import relationship


engine = create_engine('sqlite:///:memory:', echo=False)
Base = declarative_base()


class Observation(Base):
    __tablename__ = 'observations'
    id = Column(Integer, Sequence('observation_id_seq'), primary_key=True)
    id_source = Column(String(10))
    issued = Column(String(20))
    computation = Column(String(20))
    obs_status = Column(String(20))
    indicator_ref = Column(String(20))
    time = Column(String(20))

    country = relationship('Country', uselist=False, backref='observation')

    indicator = relationship('Indicator', uselist=False, backref='observation')

    values = relationship('Value', order_by='Value.id', backref='observation')

    def __repr__(self):
        return "<Observation(id_source='%s', issued='%s', computation='%s', " \
               "time='%s', indicator_ref='%s', country='%s', indicator='%s')>" % \
               (self.id_source, self.issued, self.computation, self.time,
                self.indicator_ref, self.country, self.indicator)


class Country(Base):
    __tablename__ = 'countries'
    id = Column(Integer, Sequence('country_id_seq'), primary_key=True)
    iso_code3 = Column(String(10))
    observation_id = Column(Integer, ForeignKey('observations.id'))

    def __repr__(self):
        return "<Country(iso_code3='%s')>" % self.iso_code3

class Indicator(Base):
    __tablename__ = 'indicators'
    id = Column(Integer, Sequence('indicator_id_seq'), primary_key=True)
    id_source = Column(String(10))
    name = Column(String(20))
    description = Column(String(20))
    measure_unit = Column(String(20))
    observation_id = Column(Integer, ForeignKey('observations.id'))

    def __repr__(self):
        return "<Indicator(id_source='%s', name='%s', description='%s', " \
               "measure_unit='%s')>" \
               % (self.id_source, self.name, self.description,
                  self.measure_unit)


class Value(Base):
    __tablename__ = 'values'
    id = Column(Integer, Sequence('value_id_seq'), primary_key=True)
    observation_id = Column(Integer, ForeignKey('observations.id'))
    value = Column(String(20))

    def __repr__(self):
        return "<Value(value='%s')>" % self.value

class Time(Base):
    __tablename__ = 'times'
    id = Column(Integer, Sequence('time_id_seq'), primary_key=True)
    observation_id = Column(Integer, ForeignKey('observations.id'))
    timestamp = Column(String(20))
    start_time = Column(String(10))
    end_time = Column(String(10))

    def __repr__(self):
        return "<Value(value='%s')>" % self.value

Base.metadata.create_all(engine)