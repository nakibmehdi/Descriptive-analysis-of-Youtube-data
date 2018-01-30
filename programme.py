"""
copyright © 2018 - N@kib
"""


from flask import Flask, redirect, url_for, request,render_template
import youtubeCommentAnalys as yca


app = Flask(__name__)

@app.route("/",methods=["GET","POST"]) #Default 
def index():
	return render_template('home.html')


@app.route("/video",methods=["GET"])
def video():

	videoid =  request.args.get('v') #Get videoID from GET Method
	word = request.args.get("word") #Get videoID from GET Method
	word1 = request.args.get("word1") #Get first word for conditional probability from GET Method
	word2 = request.args.get("word2") #Get second word for conditional probabilit from GET Method

	#Check exsesting of VideoID
	if(videoid == None):
		return redirect("/")


	proba = ""
	stat= ""
	df = yca.loadComments(videoid)
	try:
		f = df["sexe"].value_counts()["female"] / df["sexe"].count() * 100
	except:
		f=0
	try:
		m = df["sexe"].value_counts()["male"] / df["sexe"].count() * 100
	except:
		m=0
	try:
		n = df["sexe"].value_counts()["neutral"] / df["sexe"].count() * 100
	except:
		n = 0
	try:
		sp = df["sentiments"].value_counts()["positive"]
	except:
		sp=0
	try:
		sn = df["sentiments"].value_counts()["negative"]
	except:
		sn=0
	try:
		s = df["sentiments"].value_counts()["neutral"]
	except:
		s = 0
	if(word != None and word != ""):
		stat = yca.termFrequency(word,df["textDisplay"])
		
	elif (word1 != None and word2 != None and word1 != "" and word2 != ""):
		proba = yca.conditionalProbability(word1,word2,df["textDisplay"])


	freq = yca.topFrequency(df["textDisplay"])
	
	return render_template('dashboard.html', word1=word1,word2=word2,freq=freq,comment=df,idvideo=videoid,stat=stat,proba=proba,f=f,n=n,m=m,sp=sp,sn=sn,s=s)


if __name__ == "__main__":
	app.run(debug=True)