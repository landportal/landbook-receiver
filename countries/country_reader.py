import xlrd
import os
from model import models


class CountryReader(object):
    #ROW INDEX
    FIRST_ROW = 1
    LAST_ROW = 248

    #COLUMN INDEX (starts in 0)
    #FIELDS ORDERED BY PRIORITY
    #ISO-3
    ISO3_ADMIN = 3
    ISO3_FAO = 4
    #ISO-2
    ISO2_ADMIN = 27
    #NAME-EN
    NAME_EN_FAO_S = 6
    NAME_EN_FAO = 5
    NAME_EN_ADMIN = 2
    NAME_EN_ADMIN_LONG = 11
    #NAME-ES
    NAME_ES_FAO_S = 8
    NAME_ES_FAO = 7
    #NAME-FR
    NAME_FR_FAO_S = 10
    NAME_FR_FAO = 9
    #UN_CODE
    UN_CODE = 30
    #REGIONS
    REGION_EN = 38


    def get_countries(self, file_path):
        """ Return a list of all Landportal countries
        """
        countries = self._get_all_countries(file_path)
        return countries

    def _get_all_countries(self, path):
    	basepath = os.path.dirname(__file__)
    	filepath = os.path.abspath(os.path.join(basepath, "..", path)) # NOTE. In order to keep compatibility, no more changes are done. Maybe it should be move the filename to the constructor
        country_file = xlrd.open_workbook(filepath,
            encoding_override='latin-1').sheet_by_index(0)
        countries = []
        for row in range(self.FIRST_ROW, self.LAST_ROW + 1):
            countries.append(self.parse_country(country_file.row(row)))
        return countries

    def parse_country(self, country_data):
        iso2 = self._parse_iso2(country_data)
        iso3 = self._parse_iso3(country_data)
        fao_uri = 'http://www.fao.org/countryprofiles/index/en/?iso3=' + iso3
        un_code = None
        if not self._is_blank_value(country_data[self.UN_CODE].value):
            un_code = int(country_data[self.UN_CODE].value)
        country = models.Country(iso2=iso2, iso3=iso3, fao_URI=fao_uri,
                                 un_code=un_code)
        #Parse country name translations
        name_en = self._parse_name_en(country_data)
        name_fr = self._parse_name_fr(country_data)
        name_es = self._parse_name_es(country_data)
        country.add_translation(
            models.RegionTranslation(lang_code='en', name=name_en))
        country.add_translation(
            models.RegionTranslation(lang_code='fr', name=name_fr))
        country.add_translation(
            models.RegionTranslation(lang_code='es', name=name_es))
        # Add region
        reg_name = country_data[self.REGION_EN].value
        country.is_part_of_id = reg_name
        return country

    def _parse_iso2(self, country_data):
        iso2_admin = country_data[self.ISO2_ADMIN].value

        if not self._is_blank_value(iso2_admin):
            return iso2_admin
        else:
            return None

    def _parse_iso3(self, country_data):
        iso3_admin = country_data[self.ISO3_ADMIN].value
        iso3_fao = country_data[self.ISO3_FAO].value

        if not self._is_blank_value(iso3_admin):
            return iso3_admin
        elif not self._is_blank_value(iso3_fao):
            return iso3_fao
        else:
            return None

    def _parse_name_en(self, country_data):
        """Return english country name
        """
        name_en_fao_s = country_data[self.NAME_EN_FAO_S].value
        name_en_fao = country_data[self.NAME_EN_FAO].value
        name_en_admin = country_data[self.NAME_EN_ADMIN].value
        name_en_admin_long = country_data[self.NAME_EN_ADMIN_LONG].value

        if not self._is_blank_value(name_en_fao_s):
            return name_en_fao_s
        elif not self._is_blank_value(name_en_fao):
            return name_en_fao
        elif not self._is_blank_value(name_en_admin):
            return name_en_admin
        else:
            return name_en_admin_long

    def _parse_name_es(self, country_data):
        """Return spanish country name. It may be an empty string
        """
        name_es_fao_s = country_data[self.NAME_ES_FAO_S].value
        name_es_fao = country_data[self.NAME_ES_FAO].value

        if not self._is_blank_value(name_es_fao_s):
            return name_es_fao_s
        else:
            return name_es_fao

    def _parse_name_fr(self, country_data):
        """Return french country name. It may be an empty string
        """
        name_fr_fao_s = country_data[self.NAME_FR_FAO_S].value
        name_fr_fao = country_data[self.NAME_FR_FAO].value

        if not self._is_blank_value(name_fr_fao_s):
            return name_fr_fao_s
        else:
            return name_fr_fao

    @staticmethod
    def _is_blank_value(value):
        return value is None or value == '' or value == -99 or value == '-99'


if __name__ == '__main__':
    basepath = os.path.dirname(__file__)
    filepath = os.path.abspath(os.path.join(basepath, "country_list.xlsx"))
    CountryReader().get_countries(filepath)
