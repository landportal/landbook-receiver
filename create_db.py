# -*- coding: utf-8 -*-


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
    global_reg = DatabasePopulator.get_global_region()
    session.add(global_reg)
    session.flush()
    regions = DatabasePopulator.get_regions()
    #All the regions are part of the global region
    for reg in regions:
        reg.is_part_of_id = global_reg.id
    session.add_all(regions)
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
    def get_global_region():
        from model import models
        global_reg = models.Region(un_code=001)
        global_reg.add_translation(models.RegionTranslation(lang_code='en', name=u'Global'))
        global_reg.add_translation(models.RegionTranslation(lang_code='es', name=u'Global'))
        global_reg.add_translation(models.RegionTranslation(lang_code='fr', name=u'Global'))
        return global_reg

    @staticmethod
    def get_regions():
        from model import models
        reg1 = models.Region(un_code=2)
        reg1.add_translation(models.RegionTranslation(lang_code='en', name=u'Africa'))
        reg1.add_translation(models.RegionTranslation(lang_code='es', name=u'África'))
        reg1.add_translation(models.RegionTranslation(lang_code='fr', name=u'Afrique'))
        reg2 = models.Region(un_code=19)
        reg2.add_translation(models.RegionTranslation(lang_code='en', name=u'Americas'))
        reg2.add_translation(models.RegionTranslation(lang_code='es', name=u'América'))
        reg2.add_translation(models.RegionTranslation(lang_code='fr', name=u'Amerique'))
        reg3 = models.Region(un_code=150)
        reg3.add_translation(models.RegionTranslation(lang_code='en', name=u'Europe'))
        reg3.add_translation(models.RegionTranslation(lang_code='es', name=u'Europa'))
        reg3.add_translation(models.RegionTranslation(lang_code='fr', name=u'Europe'))
        reg4 = models.Region(un_code=9)
        reg4.add_translation(models.RegionTranslation(lang_code='en', name=u'Oceania'))
        reg4.add_translation(models.RegionTranslation(lang_code='es', name=u'Oceanía'))
        reg4.add_translation(models.RegionTranslation(lang_code='fr', name=u'Oceanie'))
        reg5 = models.Region(un_code=142)
        reg5.add_translation(models.RegionTranslation(lang_code='en', name=u'Asia'))
        reg5.add_translation(models.RegionTranslation(lang_code='es', name=u'Asia'))
        reg5.add_translation(models.RegionTranslation(lang_code='fr', name=u'Asia'))
        return [reg1, reg2, reg3, reg4, reg5]

    @staticmethod
    def get_topics():
        from model import models
        top1 = models.Topic(id='CLIMATE_CHANGE')
        top1.add_translation(models.TopicTranslation(lang_code='en', name='Climate change'))
        top2 = models.Topic(id='GEOGRAPH_SOCIO')
        top2.add_translation(models.TopicTranslation(lang_code='en', name='Geograph Socio'))
        top3 = models.Topic(id='LAND_USE')
        top3.add_translation(models.TopicTranslation(lang_code='en', name='Land Use'))
        top4 = models.Topic(id='LAND_GENDER')
        top4.add_translation(models.TopicTranslation(lang_code='en', name='Land Gender'))
        top5 = models.Topic(id='LAND_TENURE')
        top5.add_translation(models.TopicTranslation(lang_code='en', name='Land Tenure'))
        top6 = models.Topic(id='FSECURITY_HUNGER')
        top6.add_translation(models.TopicTranslation(lang_code='en', name='F Security Hunger'))
        top7 = models.Topic(id='TEMP_TOPIC')
        top7.add_translation(models.TopicTranslation(lang_code='en', name='Temp Topic'))

        topics = [top1, top2, top3, top4, top5, top6, top7]
        return topics

if __name__ == '__main__':
    create_database()