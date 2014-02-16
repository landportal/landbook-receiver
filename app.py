__author__ = 'guillermo'

from parser import parse_nodes_content, parse_nodes_attrib
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.observation import Observation, engine as obs_engine



if __name__ == "__main__":
    observation_session = sessionmaker(bind=obs_engine)
    session = observation_session()
    session.add_all(parse_nodes_attrib())
    # print session.new
    session.commit()

    print "***** ALL OBSERVATIONS ROWS *****"
    for row in session.query(Observation, Observation.id).all():
        print row.Observation, row.id
