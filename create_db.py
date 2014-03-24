'''
Created on 10/02/2014

@author: Herminio
'''
from app import db




if __name__ == '__main__':
    from model import models
    # Create DB Schema
    db.create_all()
    # Create list of the Landportal Countries
    countries = [
        models.Country(name='Spain', iso2='ES', iso3='ESP', fao_URI='http://landportal.info/ontology/country/ESP'),
        models.Country(name='England', iso2='EN', iso3='ENG', fao_URI='http://landportal.info/ontology/country/ENG'),
            ]
    # Store countries in the DB
    session = db.session
    session.add_all(countries)
    session.commit()
