__author__ = 'guillermo'
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Sequence, create_engine, \
    ForeignKey
from sqlalchemy.orm import relationship, backref


engine = create_engine('sqlite:///:memory:', echo=False)
Base = declarative_base()


class Value(Base):
    __tablename__ = 'values'
    id = Column(Integer, Sequence('value_id_seq'), primary_key=True)
    # observation_id = Column(Integer, ForeignKey('observations.id'))
    value = Column(String(20))

    # observation = relationship("models.observation.Observation")

    def __repr__(self):
        return "<Value(value='%s')>" % self.value

Base.metadata.create_all(engine)