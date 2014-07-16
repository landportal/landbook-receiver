# -*- coding: utf-8 -*-


def create_database():
    from app import db

    def _store_topics(session):
        session.add_all(MetadataPopulator.get_topics())
        session.flush()

    def _store_languages(session):
        session.add_all(MetadataPopulator.get_languages())
        session.flush()

    def _store_countries(session):
        def _get_regionid_by_name(regname):
            import model.models as models
            region = session.query(models.RegionTranslation). \
                filter(models.RegionTranslation.name == regname).first()
            return region.region_id if region is not None else None

        countries = MetadataPopulator.get_countries()
        for country in countries:
            country.is_part_of_id = _get_regionid_by_name(country.is_part_of_id)
            session.add(country)
        session.flush()
        return countries

    def _store_regions(session):
        global_reg = MetadataPopulator.get_global_region()
        session.add(global_reg)
        session.flush()
        # The continents are part of the global region
        regions = MetadataPopulator.get_regions()
        for reg in regions:
            reg.is_part_of_id = global_reg.id
        session.add_all(regions)
        session.flush()
        return regions

    session = db.session
    try:
        db.create_all()
        _store_languages(session)
        _store_regions(session)
        _store_countries(session)
        _store_topics(session)
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()

class MetadataPopulator(object):
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
    def get_countries():
        from countries.country_reader import CountryReader
        import config
        return CountryReader().get_countries(config.COUNTRY_LIST_FILE)

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
        top1.add_translation(models.TopicTranslation(lang_code='en', name=u"Climate change"))
        top1.add_translation(models.TopicTranslation(lang_code='es', name=u"Cambio climático"))
        top1.add_translation(models.TopicTranslation(lang_code='fr', name=u"Changement climatique"))
        top2 = models.Topic(id='GEOGRAPH_SOCIO')
        top2.add_translation(models.TopicTranslation(lang_code='en', name=u"Geographic and Socioeconomic"))
        top2.add_translation(models.TopicTranslation(lang_code='es', name=u"Geográfico y socioeconómico"))
        top2.add_translation(models.TopicTranslation(lang_code='fr', name=u"Géographique et socio-économique"))
        top3 = models.Topic(id='LAND_USE')
        top3.add_translation(models.TopicTranslation(lang_code='en', name=u"Land use, agriculture and investment"))
        top3.add_translation(models.TopicTranslation(lang_code='es', name=u"Uso de la tierra, agricultura e inversión"))
        top3.add_translation(models.TopicTranslation(lang_code='fr', name=u"L'utilisation des terres, de l'agriculture et de l'investissement"))
        top4 = models.Topic(id='LAND_GENDER')
        top4.add_translation(models.TopicTranslation(lang_code='en', name=u"Land and Gender"))
        top4.add_translation(models.TopicTranslation(lang_code='es', name=u"Tierra y género"))
        top4.add_translation(models.TopicTranslation(lang_code='fr', name=u"Terrain et le sexe"))
        top5 = models.Topic(id='LAND_TENURE')
        top5.add_translation(models.TopicTranslation(lang_code='en', name=u"Land Tenure"))
        top5.add_translation(models.TopicTranslation(lang_code='es', name=u"Propiedad de la tierra"))
        top5.add_translation(models.TopicTranslation(lang_code='fr', name=u"Foncière"))
        top6 = models.Topic(id='FSECURITY_HUNGER')
        top6.add_translation(models.TopicTranslation(lang_code='en', name=u"Food, Security and Hunger"))
        top6.add_translation(models.TopicTranslation(lang_code='es', name=u"Alimento, seguridad y hambre"))
        top6.add_translation(models.TopicTranslation(lang_code='fr', name=u"Alimentaire, de la sécurité et de la faim"))

        topics = [top1, top2, top3, top4, top5, top6]
        return topics

if __name__ == '__main__':
    create_database()
