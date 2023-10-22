from os import environ

host = environ.get("DBURL")
dbname = "citus"
user = "citus"
password = environ.get("DBPASSWORD")
sslmode = "require"