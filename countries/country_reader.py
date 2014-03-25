import xlrd
from model import models


class CountryReader(object):

    #FILE PATH
    FILE_PATH = 'countries/country_list.xlsx'

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

    def get_countries(self):
        """ Return a list of all Landportal countries
        """
        countries = self._get_all_countries(self.FILE_PATH)
        return countries

    def _get_all_countries(self, path):
        country_file = xlrd.open_workbook(path, encoding_override='latin-1').sheet_by_index(0)
        countries = []
        for row in range(self.FIRST_ROW, self.LAST_ROW + 1):
            countries.append(self._parse_country(country_file.row(row)))
        return countries

    def _parse_country(self, country_row):
        iso2 = self._parse_iso2(country_row)
        iso3 = self._parse_iso3(country_row)
        faoURI = 'http://landportal.info/ontology/country/' + iso3
        name = self._parse_name(country_row)

        return models.Country(name=name, iso2=iso2, iso3=iso3, fao_URI=faoURI)

    def _parse_iso2(self, country_row):
        if not self._is_blank_value(country_row[self.ISO2_ADMIN].value):
            return str(country_row[self.ISO2_ADMIN].value)
        else:
            return None

    def _parse_iso3(self, country_row):
        iso3 = country_row[self.ISO3_ADMIN].value
        if self._is_blank_value(iso3):
            iso3 = country_row[self.ISO3_FAO].value
        return str(iso3)

    def _parse_name(self, country_row):
        if not self._is_blank_value(country_row[self.NAME_EN_FAO_S].value):
            return country_row[self.NAME_EN_FAO_S].value
        elif not self._is_blank_value(country_row[self.NAME_EN_FAO].value):
            return country_row[self.NAME_EN_FAO].value
        elif not self._is_blank_value(country_row[self.NAME_EN_ADMIN].value):
            return country_row[self.NAME_EN_ADMIN].value
        else:
            return country_row[self.NAME_EN_ADMIN_LONG].value

    @staticmethod
    def _is_blank_value(value):
        return value is None or value == '' or value == -99 or value == '-99'
