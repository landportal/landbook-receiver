from app import db
from countries import country_reader


if __name__ == '__main__':
    # Create DB Schema
    db.create_all()
    # Create list of the Landportal Countries
    country_list = country_reader.CountryReader().get_countries('countries/country_list.xlsx')
    # Store countries in the DB
    session = db.session
    session.add_all(country_list)
    session.commit()
