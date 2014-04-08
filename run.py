from app import app
import create_db
import countries.country_reader

if __name__ == '__main__':
    #First create the DataBase
    #create_db.create_database()
    #Run the app
    app.run(debug=True)

