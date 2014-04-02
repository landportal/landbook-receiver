from app import app
import create_db
import countries.country_reader

if __name__ == '__main__':
    """
    reader = countries.country_reader.CountryReader()
    regions = reader.get_regions('countries/country_list.xlsx')
    for item in regions.values():
        print item
    """
    #First create the DataBase
    #create_db.create_database()
    #Run the app
    app.run(debug=True)

