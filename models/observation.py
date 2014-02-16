__author__ = 'guillermo'

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Sequence, create_engine, \
    ForeignKey
from sqlalchemy.orm import relationship, backref


engine = create_engine('sqlite:///:memory:', echo=False)
Base = declarative_base()


class Observation(Base):
    __tablename__ = 'observations'
    id = Column(Integer, Sequence('observation_id_seq'), primary_key=True)
    issued = Column(String(20))
    computation = Column(String(20))
    country = Column(String(20))
    relatedObs = Column(String(20))
    relatedProperty = Column(String(20))
    time = Column(String(20))
    indicator = Column(String(20))
    # values = relationship('Value',
    #                       order_by='Value.id',
    #                       backref='observation')

    def __repr__(self):
        return "<Observation(issued='%s', computation='%s', " \
               "country='%s', relatedObs='%s', relatedProperty='%s'" \
               "time='%s', indicator='%s')>" % (self.issued,
               self.computation, self.country, self.relatedObs,
               self.relatedProperty, self.time, self.indicator)

Base.metadata.create_all(engine)