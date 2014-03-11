__author__ = 'guillermo'

import landparser
#from sqlalchemy.orm import sessionmaker
import sqlalchemy
import sqlalchemy.orm
from landportal_model.models import engine, License

if __name__ == "__main__":
    Session = sqlalchemy.orm.sessionmaker(bind=engine)
    session = Session()
    instances = landparser.parse_nodes_content()
    session.add(instances)
    session.commit()

    for lic in session.query(License).all():
        print lic.name