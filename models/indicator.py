__author__ = 'guillermo'

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Sequence
from sqlalchemy import create_engine

engine = create_engine('sqlite:///:memory:', echo=False)
Base = declarative_base()


class Indicator(Base):
    __tablename__ = 'indicators'
    id = Column(Integer, Sequence('indicator_id_seq'), primary_key=True)
    name = Column(String(20))
    description = Column(String(20))
    measure_unit = Column(String(20))

    def __repr__(self):
        return "<Indicator(name='%s', description='%s', measure_unit='%s')>" \
               % (self.name, self.description, self.measure_unit)

Base.metadata.create_all(engine)