# LANDPORTAL-RECEIVER  CONFIGURATION  FILE

# Put here all the IPs which can send requests to the receiver.
# If this list is empty, ALL REQUESTS WILL BE ACCEPTED
ALLOWED_IPS = [
    "127.0.0.1",
]

# Those are the database configuration parameters.  Change them
# according to your configuration.  You may need to restart the
# receiver
MYSQL_URL = "localhost"
MYSQL_PORT = "3306"
MYSQL_DATABASE = "landportal"
MYSQL_USER = "root"
MYSQL_PASSWORD = "root"
DBA_USER = "dba"
DBA_PASSWORD = "root"