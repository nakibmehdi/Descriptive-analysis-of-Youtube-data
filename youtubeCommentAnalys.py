"""
copyright © 2018 - N@kib
"""

import nltk
from nltk.util import ngrams
import os.path
import requests
import math
import pandas as pd
from chicksexer import predict_gender
import unidecode
from textblob import TextBlob
import collections

def usernameClean(text):
    bad_chars = ('~+-!#()*;<=>?[\]^_`{|}1234567890')
    return unidecode.unidecode(''.join(c for c in text if c not in bad_chars))

def genderDetector(name): #English Only (Arabic not supported)
    try:
        return predict_gender(usernameClean(name),return_proba=False)
    except Exception:
        pass
    return  "neutral"

def sentimentsDetector(text): #English Only (Arabic not supported)
    sentiment = ""
    analysis = TextBlob(text)
    if float(analysis.sentiment.polarity) >0:
        sentiment = 'positive'
    elif float(analysis.sentiment.polarity) <0:
        sentiment = 'negative'
    else:
        sentiment = 'neutral'
    return sentiment

def loadComments(idVideo):
    if os.path.exists("youtubeComment/"+idVideo+'.csv'):
        return pd.read_csv("youtubeComment/"+idVideo+".csv")
    else:
        return downloadComments(idVideo)
        
def downloadComments(idVideo):
    key = 'My_API_KEY' #change This 
    textFormat = 'plainText'
    part = 'snippet'
    maxResult = '100'
    order = 'time'
    nextToken = ''

    commentids = []
    authornames = []
    likecounts = []
    totalreplycounts = []
    textDisplays = []
    textOriginals = []
    publishedAts = []
    canReplays = []

    nbcom = 0;
    while (True):
        try:
            response = requests.get("https://www.googleapis.com/youtube/v3/commentThreads?&key="+key+"&part="+part+"&videoId="+idVideo +"&maxResults="+maxResult+"&order="+order+"&pageToken="+nextToken)
        except:
            continue
        data  = response.json() #kind - etag - ?nextPageToken

        if 'error' in data:
            print(data)
            break
            
        for item in data['items']: #kind - etag - id(comment) 
            nbcom += 1
            snippet = item["snippet"] # totalReplyCount - videoid - canReplay - ispublic
            toplevelcomment = snippet['topLevelComment'] #kind - etag - id (comment)
            content = toplevelcomment['snippet'] # authorDisplayName - authorProfileImageUrl - authorChannelUrl - textDisplay - 
                # textOriginal - canRate - viewerRating - likeCount - publishedAt - updatedAt
                #element
            commentid = toplevelcomment['id']
            authorname = content['authorDisplayName']
            likecount = content['likeCount']
            totalreplycount = snippet['totalReplyCount']
            textDisplay = content['textDisplay']
            textOriginal = content['textOriginal']
            publishedAt = content['publishedAt']
            canReplay = snippet['canReply']
                    
                    #lists
            commentids.append(commentid)
            authornames.append(authorname)
            likecounts.append(likecount)
            totalreplycounts.append(totalreplycount)
            textDisplays.append(textDisplay)
            textOriginals.append(textOriginal)
            publishedAts.append(publishedAt)
            canReplays.append(canReplay)
            
        print('In Progress ' , nbcom , ' comments....')

        if 'nextPageToken' in data:
            nextToken = data['nextPageToken']
        else:
            print('Done : ',nbcom , ' comments collected in total')
            print('')
            break


    mydata = {'CommentID' : commentids, 'AuthoDisplayName' : authornames, 'LikeCount': likecounts, 'TotalReplyCount': totalreplycounts,'canReplay' :canReplays, 'publishedAt': publishedAts,'textOriginal' : textOriginals,'textDisplay' : textDisplays}
    df = pd.DataFrame(mydata)

    df['sexe'] = df['AuthoDisplayName'].apply(genderDetector)
    df['sentiments'] = df['textDisplay'].apply(sentimentsDetector)

    df.to_csv("youtubeComment/"+idVideo+".csv")
    df.to_json("youtubeComment/"+idVideo+".json")
    print('comments are saved (CSV) in : /youtubeComment/',idVideo,'.csv')
    print('comments are saved (JSON) in : /youtubeComment/',idVideo,'.json')
    print('Done!')
    return df;

def termFrequency (text,ser):
    textTokens = nltk.word_tokenize(text)
    nbWord = len(textTokens)
    nb = 0
    nbc = 0
    pres = False
    for comment in ser: 
        
        tokens = nltk.word_tokenize(str(comment))
        listSentence = list(ngrams(tokens, nbWord))
        for element in listSentence:
            if(tuple(textTokens) == element):
                pres = True
                nb = nb+1
        if (pres == True):
            nbc += 1
            pres = False

    nbcomments = len(ser)
    return (nb,nbc,nbc/nbcomments,text)

def termFrequency2 (text,ser):
    nb = 0
    for comment in ser:
        nb += comment.count(text)
    return nb

def conditionalProbability(mot1,mot2,ser):
    nbmot1 = 0 
    nbmot1mot2 = 0
    nbmot2 = 0

    for comment in ser:
        if(mot1.lower() in str(comment).lower()):
            nbmot1 += 1
            if(mot2.lower() in str(comment).lower()):
                nbmot1mot2 += 1
        else:
             if(mot2.lower() in str(comment).lower()):
                nbmot2 += 1

    p_mot1 = nbmot1 / len(ser) 
    p_Nmot1 = 1 - p_mot1
    p_mot1mot2 = p_mot1 * (nbmot1mot2/nbmot1)
    p_Nmot1mot2 = p_Nmot1 * (nbmot2 / (len(ser)-nbmot1))
    return p_mot1mot2 / (p_mot1mot2 + p_Nmot1mot2)
   
def popularComments(df):
    df=df.sort_values(by="LikeCount", ascending=False) 
    new_df = df.head(10)
    return new_df

def topFrequency(ser):
    wordcount = {}
    stopwords = set(line.strip() for line in open('stopword.txt'))
    stopwords = stopwords.union(set(['mr','mrs','one','two','said',"/><br"," ",""]))
    for com in ser:
        for word in str(com).lower().split():
            word = word.replace(".","")
            word = word.replace(",","")
            word = word.replace(":","")
            word = word.replace("\"","")
            word = word.replace("!","")
            word = word.replace("â€œ","")
            word = word.replace("â€˜","")
            word = word.replace("*","")
            if word not in stopwords:
                if word not in wordcount:
                    wordcount[word] = 1
                else:
                    wordcount[word] += 1
    wordcount = collections.Counter(wordcount)
    return wordcount.most_common(10)


