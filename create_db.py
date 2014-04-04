
def create_database():
    from app import db
    from model import models

    # Create DB Schema
    db.create_all()
    session = db.session
    # Create language list
    session.add_all(DatabasePopulator.get_languages())
    session.commit()
    # Create region list
    session.add_all(DatabasePopulator.get_regions())
    session.commit()
    # Create country list
    regions = session.query(models.Region).all()
    session.add_all(DatabasePopulator.get_countries(regions))
    session.commit()
    # Create topic list
    session.add_all(DatabasePopulator.get_topics())
    session.commit()


class DatabasePopulator(object):

    @staticmethod
    def get_languages():
        from model import models
        languages = [
            models.Language(name='Spanish', lang_code='es'),
            models.Language(name='English', lang_code='en'),
            models.Language(name='French', lang_code='fr'),
        ]
        return languages

    @staticmethod
    def get_countries(regions):
        from countries.country_reader import CountryReader
        return CountryReader().get_countries('countries/country_list.xlsx', regions)

    @staticmethod
    def get_regions():
        from model import models
        reg1 = models.Region(un_code='002')
        reg1.add_translation(models.RegionTranslation(lang_code='en', name='Africa'))
        reg1.add_translation(models.RegionTranslation(lang_code='es', name='Africa'))
        reg1.add_translation(models.RegionTranslation(lang_code='fr', name='Afrique'))
        reg2 = models.Region(un_code='019')
        reg2.add_translation(models.RegionTranslation(lang_code='en', name='Americas'))
        reg2.add_translation(models.RegionTranslation(lang_code='es', name='America'))
        reg2.add_translation(models.RegionTranslation(lang_code='fr', name='Amerique'))
        reg3 = models.Region(un_code='150')
        reg3.add_translation(models.RegionTranslation(lang_code='en', name='Europe'))
        reg3.add_translation(models.RegionTranslation(lang_code='es', name='Europa'))
        reg3.add_translation(models.RegionTranslation(lang_code='fr', name='Europe'))
        reg4 = models.Region(un_code='009')
        reg4.add_translation(models.RegionTranslation(lang_code='en', name='Oceania'))
        reg4.add_translation(models.RegionTranslation(lang_code='es', name='Oceania'))
        reg4.add_translation(models.RegionTranslation(lang_code='fr', name='Oceanie'))
        reg5 = models.Region(un_code='142')
        reg5.add_translation(models.RegionTranslation(lang_code='en', name='Asia'))
        reg5.add_translation(models.RegionTranslation(lang_code='es', name='Asia'))
        reg5.add_translation(models.RegionTranslation(lang_code='fr', name='Asia'))
        return [reg1, reg2, reg3, reg4, reg5]

    @staticmethod
    def get_topics():
        from model import models
        top1 = models.Topic(id='TOP1', name='TOPIC_CLIMATE_CHANGE')
        top1.add_translation(models.TopicTranslation(lang_code='en', name='Climate change'))
        top2 = models.Topic(id='TOP2', name='TOPIC_COUNTRY_DATA')
        top2.add_translation(models.TopicTranslation(lang_code='en', name='Country data'))
        top3 = models.Topic(id='TOP3', name='TOPIC_FOOD_SEC_AND_HUNGER')
        top3.add_translation(models.TopicTranslation(lang_code='en', name='Food security and hunger'))
        top4 = models.Topic(id='TOP4', name='TOPIC_LAND_AND_GENDER')
        top4.add_translation(models.TopicTranslation(lang_code='en', name='Land and gender'))
        top5 = models.Topic(id='TOP5', name='TOPIC_LAND_TENURE')
        top5.add_translation(models.TopicTranslation(lang_code='en', name='Land ternure'))
        top6 = models.Topic(id='TOP6', name='TOPIC_SOCIO_ECONOMIC_AND_POVERTY')
        top6.add_translation(models.TopicTranslation(lang_code='en', name='Socio economic and poverty'))
        top7 = models.Topic(id='TOP7', name='TOPIC_USAGE_AND_INVESTMENT')
        top7.add_translation(models.TopicTranslation(lang_code='en', name='Usage and investment'))
        top99 = models.Topic(id='TOP99', name='TOPIC_TEMPORAL')
        top99.add_translation(models.TopicTranslation(lang_code='en', name='Temporal'))

        topics = [top1, top2, top3, top4, top5, top6, top7, top99]
        return topics

if __name__ == '__main__':
    create_database()