
import webbrowser, configparser
from requests_oauthlib import OAuth1Session
import tweepy, npyscreen, sys
import time, threading

__version__ = "1.0.0"

class MainApp(npyscreen.NPSAppManaged):
	def __init__(self):
		npyscreen.NPSAppManaged.__init__(self)
		self.auth = None
		self.api = None
	def onStart(self):
		self.addForm("MAIN", TimeLineList)
		self.addForm("LOGIN", LoginForm)
		self.addForm("TWEET", TweetWriter)
	def isAuthed(self):
		if self.auth:
			return True
		else:
			return False
	def authINI(self):
		config = configparser.ConfigParser()
		config.read('~/.zwitter.conf.ini')
		if not 'Consumer' in config:
			return False
		if not ('key' in config['Consumer'] and 'secret' in config['Consumer']):
			return False
		if not 'AccessToken' in config:
			return False
		if not ('key' in config['AccessToken'] and 'secret' in config['AccessToken']):
			return False
		ck = config['Consumer']['key']
		cs = config['Consumer']['secret']
		atk = config['AccessToken']['key']
		ats = config['AccessToken']['secret']
		try:
			self.auth = tweepy.OAuthHandler(ck, cs)
			self.auth.set_access_token(atk, ats)
			self.auth.apply_auth()
			self.api = tweepy.API(self.auth)
		except tweepy.TweepError:
			return False
		return True
	def getAuthURL(self):
		config = configparser.ConfigParser()
		config.read('~/.zwitter.conf.ini')
		if not 'Consumer' in config:
			return None
		if not ('key' in config['Consumer'] and 'secret' in config['Consumer']):
			return None
		ck = config['Consumer']['key']
		cs = config['Consumer']['secret']
		try:
			self.auth = tweepy.OAuthHandler(ck, cs)
			self.auth.apply_auth()
			return self.auth.get_authorization_url()
		except tweepy.TweepError:
			return None
	def authTweepy(self, pincode):
		try:
			token = self.auth.get_access_token(verifier=pincode)
			self.api = tweepy.API(self.auth)
			config = configparser.ConfigParser()
			config['Consumer'] = { 'key':self.auth.consumer_key.decode("utf-8"),
								'secret':self.auth.consumer_secret.decode("utf-8") }
			config['AccessToken'] = { 'key':self.auth.access_token,
								'secret':self.auth.access_token_secret }
			with open('config.ini', 'w') as f:
				config.write(f)
		except tweepy.TweepError:
			return False
		return True
	def getTimeline(self):
		if not self.api:
			return None
		statuses = self.api.home_timeline(count=300)
		return list(map(lambda s: "%s - %s(@%s) : %s" % (s.id, s.user.name, s.user.screen_name, s.text), statuses))
	def getStatus(self, sid):
		if not self.api:
			return None
		try:
			status = self.api.get_status(sid)
		except tweepy.TweepError:
			status = None
		return status
	def updateStatus(self, text, rid=None):
		if self.api:
			self.api.update_status(text, rid)
	def retweet(self, sid):
		if self.api:
			try:
				self.api.retweet(sid)
			except tweepy.TweepError:
				return False
			return True

class LoginForm(npyscreen.ActionFormV2):
	def create(self):
		self.name = "Autentication"
		self.wgGuide = self.add(npyscreen.MultiLineEdit, max_height=5, rely=5)
		self.wgGuide.value = """
I will try to start a browser to visit the following Twitter page
if a browser will not start, copy the URL to your browser
and retrieve the pincode to be used
in the next step to obtaining an Authentication Token :"""
		self.wgGuide.editable = False
		self.wgURL = self.add(npyscreen.FixedText)
		self.wgURL.value = ""
		self.wgPin = self.add(npyscreen.TitleText, name = "Pincode :")
	def init(self):
		url = self.parentApp.getAuthURL()
		if url:
			self.wgURL.value = url
			self.urlsuccess = True
		else:
			self.wgGuide.value = """
Getting Authoriztion URL Failed!
Check ~/.zwitter.conf.ini that you wrote right Consumer Key and Secret"""
			self.urlsuccess = False

		if self.urlsuccess:
			webbrowser.open(url)
		self.DISPLAY()
	def on_cancel(self):
		sys.exit(0)
	def on_ok(self):
		if self.urlsuccess:
			if self.parentApp.authTweepy(self.wgPin.value):
				self.parentApp.switchFormPrevious()
				self.parentApp.getForm("MAIN").updateList()
			else:
				self.wgGuide.value = """
Authorization Failed!
Check that you wrote right Pincode"""
		else:
			sys.exit(0)

class Tweets(npyscreen.MultiLineAction):
	def __init__(self, *args, **keywords):
		super(Tweets, self).__init__(*args, **keywords)
		self.add_handlers({
			"^T": self.tweet,
			"^R": self.refresh,
			"^D": self.exit
			})
	def actionHighlighted(self, act_on_this, keypress):
		self.parent.parentApp.getForm('TWEET').value = act_on_this.split()[0]
		self.parent.parentApp.switchForm('TWEET')
	def tweet(self, *args, **keywords):
		self.parent.parentApp.getForm('TWEET').value = None
		self.parent.parentApp.switchForm('TWEET')
	def refresh(self, *args, **keywords):
		self.parent.updateList()
	def exit(self, *args, **keywords):
		sys.exit(0)

class TimeLineList(npyscreen.FormMutt):
	MAIN_WIDGET_CLASS = Tweets
	def beforeEditing(self):
		self.wCommand.value = "Ctrl-T to Tweet, Ctrl-R to Refresh, Ctrl-D to Exit"
		self.updateList()
	def updateList(self):
		if self.parentApp.isAuthed():
			self.wMain.values = self.parentApp.getTimeline()
			self.wMain.display()
		else:
			if self.parentApp.authINI():
				self.updateList()
			else:
				self.parentApp.switchForm("LOGIN")
				self.parentApp.getForm("LOGIN").init()
				self.parentApp.getForm("LOGIN").edit()

class TweetWriter(npyscreen.ActionForm):
	def create(self):
		self.value = None
		self.wgId = self.add(npyscreen.TitleText, name = "ID :")
		self.wgId.editable = False
		self.wgUser = self.add(npyscreen.TitleText, name = "User :")
		self.wgUser.editable = False
		self.wgTweet = self.add(npyscreen.MultiLineEdit, max_height=10, rely=9)
		self.wgReply = self.add(npyscreen.TitleText, name = "Reply To :")
		self.wgRetweet = self.add(npyscreen.TitleText, name = "Retweet :")
		self.wgRetweet.editable = False
		self.wgReplyJumpGuide = self.add(npyscreen.FixedText)
		self.wgReplyJumpGuide.value = "Ctrl-G to jump to reply tweet"
		self.wgRetweetGuide = self.add(npyscreen.FixedText)
		self.wgRetweetGuide.value = "Ctrl-R to retweet this"
		self.wgReplyGuide = self.add(npyscreen.FixedText)
		self.wgReplyGuide.value = "Ctrl-F to reply"
		self.add_handlers({
			"^G": self.goReply,
			"^R": self.retweet,
			"^F": self.reply
			})
	def beforeEditing(self):
		if self.value:
			status = self.parentApp.getStatus(self.value)
			self.name = "Detail"
			self.statusId = self.value
			self.wgId.value = '%s'%self.statusId
			self.wgUser.value = '%s(@%s)' % (status.user.name, status.user.screen_name)
			self.wgUser.hidden = False
			self.wgTweet.value = status.text
			self.wgTweet.editable = False
			if status.in_reply_to_status_id:
				self.wgReply.value = '%s' % status.in_reply_to_status_id
				self.wgReply.hidden = False
				self.wgReply.editable = False
				self.wgReplyJumpGuide.hidden = False
			else:
				self.wgReply.hidden = True
				self.wgReplyJumpGuide.hidden = True
			self.wgRetweet.value = '%s' % status.retweet_count
			self.wgRetweet.hidden = False
			self.wgRetweetGuide.value = "Ctrl-R to retweet this"
			self.wgRetweetGuide.hidden = False
			self.wgReplyGuide.hidden = False
		else:
			self.name = "New Tweet"
			self.statusId = ''
			self.wgId.hidden = True
			self.wgUser.hidden = True
			self.wgTweet.value = ''
			self.wgTweet.editable = True
			self.wgReply.value = ''
			self.wgReply.hidden = False
			self.wgReply.editable = True
			self.wgReplyJumpGuide.hidden = True
			self.wgRetweet.value = ''
			self.wgRetweet.hidden = True
			self.wgRetweetGuide.hidden = True
			self.wgReplyGuide.hidden = True
		self.wgId.update()
		self.wgUser.update()
		self.wgTweet.update()
		self.wgReply.update()
		self.wgReplyJumpGuide.update()
		self.wgRetweet.update()
		self.wgRetweetGuide.update()
		self.wgReplyGuide.update()
	def on_ok(self):
		if not self.statusId:
			if not self.wgReply.value:
				self.parentApp.updateStatus(self.wgTweet.value)
			else:
				if self.parentApp.getStatus(int(self.wgReply.value)):
					self.parentApp.updateStatus(self.wgTweet.value,
							int(self.wgReply.value))
			self.parentApp.getForm('LIST').updateList()
		self.parentApp.switchFormPrevious()
	def on_cancel(self):
		self.parentApp.switchFormPrevious()
	def goReply(self, *args, **keywords):
		if self.statusId:
			if self.wgReply.value:
				self.value = self.wgReply.value
				self.beforeEditing()
	def retweet(self, *args, **keywords):
		if self.statusId:
			if self.parentApp.retweet(self.statusId):
				self.wgRetweetGuide.value = "Retweeted!"
			else:
				self.wgRetweetGuide.value = "Retweet Failed"
			self.wgRetweetGuide.update()
	def reply(self, *args, **keywords):
		if self.statusId:
			sid = self.statusId
			self.value = None
			self.beforeEditing()
			self.name = "Reply"
			self.wgTweet.value = "@%s "%self.parentApp.getStatus(sid).user.screen_name
			self.wgReply.value = '%s'%sid

def main():
	app = MainApp()
	app.run()

