import praw
import random
import threading
import mysql.connector
from mysql.connector import errorcode
from auth import *
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Label
from kivy.clock import Clock

#SQL Layout
#name:string - url:string - subscribers:int - nsfw:int - description:longtext

#Global Variables
cursor = ''
reddit = ''
scanCondition = 1

#the GUI window that opens
class TestWindow(BoxLayout):
	pass

#all the code and functions for the GUI
class TestApp(App):
	#launches the window
	def build(self):
		self.load_kv('window.kv')
		return TestWindow()

	#when the scan button is called, resets the scan condition and creates a new thread to start scanning
	def scan(self, *args):
		global scanCondition
		scanCondition = 1
		#launches scan thread
		ScanThread()

	#sets the scan condition to 0, which the thread will recignize and stop scanning
	def stopScan(self):
		global scanCondition
		scanCondition = 0

#here we define the thread that will scan through reddit.
class ScanThread(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
		self.start()
	
	#when the thread runs it will call the scan reddit function
	def run(self):
		global cursor, reddit
		scanReddit(cursor, reddit)

#here we define the main function that controls this program.  It will initiate the SQL server connection, and if succesful will generate a coonnection to reddit (saved as 'reddit' globally) and will then run the GUI
def main():
	global cursor
	global reddit
	#will try too generate a connection to the SQL server (hardcoded at the moment).  If an error is thrown it will catch and print out the error.
	try:
		cnx = mysql.connector.connect(user=authUser, password=authPassword, host=authHost, database=authDatabase)
	except mysql.connector.error as err:
		if err.errno == errorcode.er_access_denied_error:
			print("something is wrong with your user name or password")
		elif err.errno == errorcode.er_bad_db_error:
			print("database does not exist")
		else:
			print(err)
	else:
		#generates a cursor which allows us to query the SQL server
		cursor = cnx.cursor(buffered=True)	
		#turns on auto commit so that we do not need to call commit every time we query (however this means we can only make one query at a time)
		cnx.autocommit = True;
		#generates the connection to reddit so we can make API calls
		reddit = praw.Reddit(client_id=redditClientID, client_secret=redditClientSecret, user_agent=redditUserAgent)
		
		#initiates the GUI
		TestApp().run()

		#closes the SQL connection when the program is finished
		cnx.close()

#this function is called by a thread which will scan reddit indefintely and store it in the SQL databse.  Generates the query by calling createQueryFromRandomSubreddit and sends this query to SQL by calling cursor.execute
#This method will end once scanCondition is set to 0
def scanReddit(cursor, reddit):
	global scanCondition
	while scanCondition == 1:
		query, data = createQueryFromRandomSubreddit(reddit)
		print('another subreddit added')
		cursor.execute(query, data)

#generates the query to be sent to our SQL server.  Returns 2 values. query: the query part of the text such as "SELECT * FROM" and "WHERE" etc.  data: the value portion of the query such as 'subreddits' and column values
#since we have to declare if the search will result in a NSFW or SFW subreddit I used a random value (0 or 1) to decide the search so that we can get a broad range of subreddits
#the query generated will only input a new row if the subreddit does NOT already exist in the table
def createQueryFromRandomSubreddit(reddit):
	#generates random value to decide if search is SFW or NSFW
	nsfwSearch = False;
	if random.randint(0, 1) == 0:
		nsfwSearch = True;
	#uses reddit API to get random subreddit
	subreddit = reddit.random_subreddit(nsfwSearch)
	#the frame of the query being called.  Will check to make sure the new row is not already in the table
	query = "INSERT INTO subreddits SELECT %s, %s, %s, %s, %s WHERE NOT EXISTS (SELECT * FROM subreddits WHERE name = %s)"
	data = (subreddit.display_name, generateURL(subreddit.url), subreddit.subscribers, getNSFWInt(subreddit.over18), 
		 getShortDesription(subreddit.public_description), subreddit.display_name)
	return query, data

#simply adds the full web url to the short version of the url provided by the API
def generateURL(shortURL):
	return "https://www.reddit.com" + shortURL

#takes in a bool and returns an int. True = 1 and False = 0
def getNSFWInt(nsfwBool):
	if nsfwBool == True:
		return 1
	else:
		return 0

#sometimes reddit descriptions can be rather long and can go beyond a description.  This method removes all characters past the \n character.  In practice this should shorten long descriptions, however in some cases may cause some of the actual description to be lost
def getShortDesription(longDescription):
	shortDescription = ""
	for char in longDescription:
		if char == '\n':
			break
		else:
			shortDescription = shortDescription + char
	return shortDescription


#everything below this line is the actual code that is ran when the file runs
#-----------------------------------------------------------------------------------------#

#runs the main function
if __name__== "__main__":
	main()
