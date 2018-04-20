import praw
import mysql.connector
from mysql.connector import errorcode
from auth import *
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Label


class TestWindow(BoxLayout):
	pass

class TestApp(App):
	def build(self):
		self.load_kv('window.kv')
		return TestWindow()

TestApp().run()



#reddit = praw.Reddit(client_id=redditClientID,
#                     client_secret=redditClientSecret,
#                     user_agent=redditUserAgent)

#subreddit = reddit.random_subreddit(False)
#print(subreddit.display_name)
#print(subreddit.public_description)
#print(subreddit.subscribers)
#print(subreddit.url)
#print(subreddit.over18)

#try:
#	cnx = mysql.connector.connect(user=authuser, password=authpassword, host=authhost, database=authdatabase)
#except mysql.connector.error as err:
#	if err.errno == errorcode.er_access_denied_error:
#		print("something is wrong with your user name or password")
#	elif err.errno == errorcode.er_bad_db_error:
#		print("database does not exist")
#	else:
#		print(err)
#else:
#	cura = cnx.cursor(buffered=true)
#	query = ("insert into subreddits values (%s)")
#	data = ('/r/deepfriedmemes',)
#	cura.execute(query, data)
#	cnx.commit()
#	cnx.close()