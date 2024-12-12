import mysql.connector

dataBase = mysql.connector.connect(
    host = 'localhost',
    user = 'root',
    passwd = 'theplanetisflat'
)

#preparing cursor object
cursorObject = dataBase.cursor()

#creating a database
cursorObject.execute("CREATE DATABASE myblog")

print("Ohh Yeah!! All Done!")