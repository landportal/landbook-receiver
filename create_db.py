class DatabasePopulator(object):
    @staticmethod
    def get_languages():
        from model.models import Language
        languages = [
            Language(name='Spanish', lang_code='es'),
            Language(name='English', lang_code='en'),
            Language(name='French', lang_code='fr'),
        ]
        return languages

    @staticmethod
    def get_countries():
        from countries.country_reader import CountryReader
        return CountryReader().get_countries('countries/country_list.xlsx')

    @staticmethod
    def get_translations():
        from countries.country_reader import CountryReader
        return CountryReader().get_country_names('countries/country_list.xlsx')

if __name__ == '__main__':
    from app import db
    # Create DB Schema
    db.create_all()
    session = db.session
    # Create language list
    session.add_all(DatabasePopulator.get_languages())
    session.commit()
    # Create country list
    # Store countries in the DB
    session.add_all(DatabasePopulator.get_countries())
    session.commit()
    session.add_all(DatabasePopulator.get_translations())
    session.commit()
