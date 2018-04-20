import mysql.connector
from mysql.connector import errorcode
from auth import *

try:
	cnx = mysql.connector.connect(user=authUser, password=authPassword, host=authHost, database=authDatabase)
except mysql.connector.Error as err:
	if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
		print("Something is wrong with your user name or password")
	elif err.errno == errorcode.ER_BAD_DB_ERROR:
		print("Database does not exist")
	else:
		print(err)
else:
	curA = cnx.cursor(buffered=True)
	query = ("INSERT INTO subreddits VALUES (%s)")
	data = ('/r/deepfriedmemes',)
	curA.execute(query, data)
	cnx.commit()
	cnx.close()