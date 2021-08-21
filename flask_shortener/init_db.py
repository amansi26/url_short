# This is to connect to database.db file, that holds all the application data
import sqlite3

connection = sqlite3.connect('database.db')

# Execute the schema.sql multiple comaand in one go using excecutescript()
with open('schema.sql') as f:
    connection.executescript(f.read())

connection.commit()
connection.close()
