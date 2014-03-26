import xlrd
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

    def get_countries(self, file_path):
        """ Return a list of all Landportal countries
        """
        countries = self._get_all_countries(file_path)
        return countries

    def get_country_names(self, file_path):
        """Return a list of all country names in multiple languages.
        """
        country_names = self._get_all_country_names(file_path)
        return country_names

    def _get_all_country_names(self, path):
        country_file = xlrd.open_workbook(path, encoding_override='latin-1').sheet_by_index(0)
        country_names = []
        for row in range(self.FIRST_ROW, self.LAST_ROW + 1):
            country_names.append(self._parse_name_en(country_file.row(row)))
            country_names.append(self._parse_name_es(country_file.row(row)))
            country_names.append(self._parse_name_fr(country_file.row(row)))
        return country_names

    def _get_all_countries(self, path):
        country_file = xlrd.open_workbook(path, encoding_override='latin-1').sheet_by_index(0)
        countries = []
        for row in range(self.FIRST_ROW, self.LAST_ROW + 1):
            countries.append(self._parse_country(country_file.row(row)))
        return countries

    def _parse_country(self, country_data):
        iso2 = self._parse_iso2(country_data)
        iso3 = self._parse_iso3(country_data)
        fao_URI = 'http://landportal.info/ontology/country/' + iso3

        return models.Country(name='', iso2=iso2, iso3=iso3, fao_URI=fao_URI)


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
        """Parse english country name, return a Translation object
        """
        name_en_fao_s = country_data[self.NAME_EN_FAO_S].value
        name_en_fao = country_data[self.NAME_EN_FAO].value
        name_en_admin = country_data[self.NAME_EN_ADMIN].value
        name_en_admin_long = country_data[self.NAME_EN_ADMIN_LONG].value

        name = ''
        if not self._is_blank_value(name_en_fao_s):
            name = name_en_fao_s
        elif not self._is_blank_value(name_en_fao):
            name = name_en_fao
        elif not self._is_blank_value(name_en_admin):
            name = name_en_admin
        elif not self._is_blank_value(name_en_admin_long):
            name = name_en_admin_long
        return models.Translation(lang_code='en', item_id=self._parse_iso3(country_data), name=name)

    def _parse_name_es(self, country_data):
        """Parse spanish country name, return a Translation object
        """
        name_es_fao_s = country_data[self.NAME_ES_FAO_S].value
        name_es_fao = country_data[self.NAME_ES_FAO].value

        name = ''
        if not self._is_blank_value(name_es_fao_s):
            name = name_es_fao_s
        elif not self._is_blank_value(name_es_fao):
            name = name_es_fao
        return models.Translation(lang_code='es', item_id=self._parse_iso3(country_data), name=name)

    def _parse_name_fr(self, country_data):
        """Parse french country name, return a Translation object
        """
        name_fr_fao_s = country_data[self.NAME_FR_FAO_S].value
        name_fr_fao = country_data[self.NAME_FR_FAO].value

        name = ''
        if not self._is_blank_value(name_fr_fao_s):
            name = name_fr_fao_s
        elif not self._is_blank_value(name_fr_fao):
            name = name_fr_fao
        return models.Translation(lang_code='fr', item_id=self._parse_iso3(country_data), name=name)

    @staticmethod
    def _is_blank_value(value):
        return value is None or value == '' or value == -99 or value == '-99'

if __name__ == '__main__':
    CountryReader().get_countries('country_list.xlsx')
