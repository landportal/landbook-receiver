__author__ = 'guillermo'

import landparser
#from sqlalchemy.orm import sessionmaker
import sqlalchemy
import sqlalchemy.orm
from models import engine, Observation, Indicator, MeasurementUnit

if __name__ == "__main__":
    Session = sqlalchemy.orm.sessionmaker(bind=engine)
    session = Session()
    instances = landparser.parse_nodes_content()
    session.add_all(instances)
    session.commit()