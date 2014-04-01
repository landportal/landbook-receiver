from app import app
import countries.country_reader

if __name__ == '__main__':
    #app.run(debug=True)
    reader = countries.country_reader.CountryReader()
    regions = reader.get_regions('countries/country_list.xlsx')
    for item in regions.values():
        print item
