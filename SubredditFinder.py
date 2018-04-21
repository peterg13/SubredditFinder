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
#name:string - url:string - subscribers:int - nsfw:int - description:string

#Global Variables
cursor = ''
reddit = ''

class TestWindow(BoxLayout):
	pass

class TestApp(App):
	event = ''

	def build(self):
		self.load_kv('window.kv')
		return TestWindow()

	def scan(self, *args):
		global cursor, reddit
		threading.Thread(target = scanReddit(cursor, reddit)).start()
	def stopScan(self):
		pass

def main():
	global cursor
	global reddit
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
		cursor = cnx.cursor(buffered=True)	
		cnx.autocommit = True;
		reddit = praw.Reddit(client_id=redditClientID, client_secret=redditClientSecret, user_agent=redditUserAgent)
		
		TestApp().run()

		cnx.close()

def scanReddit(cursor, reddit):
	#for i in range(10):
	while True:
		query, data = createQueryFromRandomSubreddit(reddit)
		print('another one added')
		cursor.execute(query, data)

def createQueryFromRandomSubreddit(reddit):
	nsfwSearch = False;
	if random.randint(0, 1) == 0:
		nsfwSearch = True;
	subreddit = reddit.random_subreddit(nsfwSearch)
	query = "INSERT INTO subreddits SELECT %s, %s, %s, %s, %s WHERE NOT EXISTS (SELECT * FROM subreddits WHERE name = %s)"
	data = (subreddit.display_name, generateURL(subreddit.url), subreddit.subscribers, getNSFWBit(subreddit.over18), 
		 getShortDesription(subreddit.public_description), subreddit.display_name)
	return query, data

def generateURL(shortURL):
	return "https://www.reddit.com" + shortURL

def getNSFWBit(nsfwBool):
	if nsfwBool == True:
		return 1
	else:
		return 0

def getShortDesription(longDescription):
	shortDescription = ""
	for char in longDescription:
		if char == '\n':
			break
		else:
			shortDescription = shortDescription + char
	return shortDescription




#runs the main function
if __name__== "__main__":
  main()
