from flask import Flask, request
""", redirect"""
import os, twilio.twiml, praw
import newrelic.agent
newrelic.agent.initialize('newrelic.ini')
app = Flask(__name__)
r=praw.Reddit('reddit sms parser (j12coder)')
def check_subreddit(body):
	sp=body.split(" ")
	if len(sp)<2:
		return 'Sorry, it seems like you didn\'t type the message right. Here\'s an example: LearnPython 2'	
	elif len(sp)==2:
		return ht(sp)
	else:
		return pst(sp)

def pst(sp):
	subreddit=sp[0]
	post=sp[1]
	num=sp[2]
	try:
		num=int(num)
	except ValueError:
		return 'Sorry, it seems like you didn\'t type the message right. Here\'s an example: LearnPython post 2'
	if post !='post':
		return 'Sorry, it seems like you didn\'t type the message right. Here\'s an example: LearnPython post 2'
	if num>5:
		return 'Uh oh. This could jam up the system; how about limiting it to the 5th post?'
	elif num<=0:
		return 'Well, here are the 0 results you wanted!'
	if subreddit=="random":
		return get_post(r.get_subreddit(subreddit),num)
	subs=r.search_reddit_names(subreddit)
	if len(subs)>0:
		for sub in subs:
			if sub.display_name.lower()==subreddit:
				return get_post(sub,num)
		return 'Sorry, looks like I couldn\'t find that subreddit. Did you maybe mean reddit.com/r/%s? Or, the sub could be inactive. Maybe it moved to a different name?'%subs[0].display_name
	else:
		return 'Sorry, no subreddit found by that name. The sub could be inactive, maybe it migarted to a different name?'


def ht(sp):
	subreddit=sp[0]
	num=sp[1]
	try:
		num=int(num)
	except ValueError:
		return 'Sorry, it seems like you didn\'t type the message right. Here\'s an example: LearnPython 2'
	if num>3:
		return 'Hold on there, that\'s a lot of data! Try keeping it down to no more than 3 posts at a time.'
	if subreddit=="random":
		return get_posts(r.get_subreddit(subreddit),num)
	subs=r.search_reddit_names(subreddit)
	if len(subs)>0:
		for sub in subs:
			if sub.display_name.lower()==subreddit:
				return get_posts(sub,num)
		return 'Sorry, looks like I couldn\'t find that subreddit. Did you maybe mean reddit.com/r/%s? Or, the sub could be inactive. Maybe it moved to a different name?'%subs[0].display_name
	else:
		return 'Sorry, no subreddit found by that name. The sub could be inactive, maybe it migarted to a different name?'

		
def safe(s):
	return str(s.encode("ascii", errors='ignore'))
def get_post(sub,num):
	sumstr=""
	p=list(sub.get_hot(limit=num))[-1]
	if p.is_self:
		sumstr+="%s\nby %s %s pts %d coms\n\n%s\n"%(safe(p.title), p.author, p.ups, len(p.comments),safe(p.selftext))
	else:
		sumstr+="%s\nby %s %s pts %d coms\n"%(safe(p.title), p.author, p.ups, len(p.comments))	
	sumstr+="\n%s\n\n"%str(p.short_link.replace("http://",""))
	return sumstr
def get_posts(sub,num):
	sumstr="Hot posts on reddit.com/r/%s:\n\n"%sub.display_name
	new_posts=sub.get_hot(limit=num)
	for p in new_posts:
		p.title=safe(p.title)
		if p.title>45:
			p.title=p.title[:43]+"..."
		sumstr+="%s\nby %s %s pts %d coms\n"%(p.title, p.author, p.ups, len(p.comments))
		sumstr+="%s\n\n"%str(p.short_link.replace("http://",""))
	return sumstr

@app.route("/", methods=['GET', 'POST'])
def hello_monkey():
	msg=request.values.get('Body','Empty message?').lower()
	resp = twilio.twiml.Response()
	if msg=='wat' or msg=='what' or msg=='about' or msg=='help me' or msg=='hi' or msg=='hello':
		resp.message("bit.ly/1pI0K9B SMS Reddit parser. \n Txt subreddit name and # of results you want. Ex: science 3 . Put post before # to get back specific post Ex: ruby post 2")
	elif msg=="thanks" or msg=="thx" or msg=="thanx":
		resp.message("No problem! Let me know your opinion at hi@isaacmoldofsky.com!")
	elif msg=="this rocks" or msg=="this is great" or msg=="great":
		resp.message("Thanks! Let me know your opinion at hi@isaacmoldofsky.com!")
	else:
		resp.message(check_subreddit(msg))
	return str(resp)
if __name__ == "__main__":
	port = int(os.environ.get('PORT', 5000))
	app.run(host='0.0.0.0', port=port)
