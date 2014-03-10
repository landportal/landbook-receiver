__author__ = 'guillermo'

from landparser import parse_nodes_content
from sqlalchemy.orm import sessionmaker
from models import engine, Observation, Indicator

if __name__ == "__main__":
    Session = sessionmaker(bind=engine)
    session = Session()
    session.add_all(parse_nodes_content())

    for o, i in session.query(Observation, Indicator). \
            filter(Observation.indicator_ref == Indicator.id_source).all():

        #TODO Construct a new collection of observations with indicators
        print o.id_source + ' indicator:' + i.name

    session.commit()

    # print "***** INDICATORS *****"
    # for row in session.query(Indicator, Indicator.id).all():
    #     print row.Indicator, row.id
    #
    # print "***** OBSERVATIONS *****"
    # for row in session.query(Observation, Observation.id).all():
    #     print row.Observation, row.id
