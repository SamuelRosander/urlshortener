import psycopg2
from psycopg2 import pool
from os import environ
import db_config

# Build a connection string from the variables
conn_string = "host={0} user={1} dbname={2} password={3} sslmode={4}".format(db_config.host, db_config.user, db_config.dbname, db_config.password, db_config.sslmode)

postgreSQL_pool = psycopg2.pool.SimpleConnectionPool(1, 20,conn_string)
if (postgreSQL_pool):
    print("Connection pool created successfully")

# Use getconn() to get a connection from the connection pool
conn = postgreSQL_pool.getconn()

cursor = conn.cursor()

# Drop previous table of same name if one exists
cursor.execute("DROP TABLE IF EXISTS shorturls;")
print("Finished dropping table (if existed)")

# Create a table
cursor.execute("CREATE TABLE shorturls (id serial primary key, long_link text, short_link text);")
print("Finished creating table")

# Create a index
cursor.execute("CREATE INDEX idx_shorturls_id ON shorturls(id);")
print("Finished creating index")

# Insert some data into the table
cursor.execute("INSERT INTO shorturls  (long_link,short_link) VALUES (%s, %s);", ("long1","short1"))
cursor.execute("INSERT INTO shorturls  (long_link,short_link) VALUES (%s, %s);", ("long2","short2"))
print("Inserted 2 rows of data")

# Clean up
conn.commit()
cursor.close()
conn.close()