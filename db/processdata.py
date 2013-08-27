'''
Created on 25-Jul-2013

@author: rajuc
'''

import src.git.util.mysqldatabase as db
import re
import src.git.util.util as util
from nltk.stem import WordNetLemmatizer


def getdata():
    """
    retrieves the data from repository table
    removes the special characters and stop words and does the stemming(using nltk package)
    """
    conn=db.getDBConnection()
    cursor = conn.cursor()
    global stopWordSet
    sql = "select id, description from repository"
    rows = db.executeSQL(conn, sql)
    counter=1
    wnl = WordNetLemmatizer()
    for row in rows:
        id = row[0]
        desc= row[1]
        #print desc
        if desc is not None:
            desc=desc.replace('-',' ').replace(',',' ').replace('/',' ').replace('.',' ').replace('_',' ')
            desc = desc.lower()
            desc = re.sub('[^a-z0-9 ]','',desc)
            keywords = desc.split(" ")
            for word in keywords:
                #word = porter.stem(word.strip())
                word=wnl.lemmatize(word.strip())
                if word not in stopWordSet:
                    sql1 = "insert into keywords1 values("+str(counter)+",'"+word+"',"+str(id)+ ',' + str(0) + ")"
                    print sql1
                    cursor.execute(sql1)
                    conn.commit()
                    counter = counter+1

def cleanKeyWords():
    """
    inserts the distinct words and occurence into the table
    """
    conn = db.getDBConnection()
    cursor = conn.cursor()
    sql = "select word from keywords1"
    rows= db.executeSQL(conn, sql)
    wordMap = {} 
    for row in rows:
        word = row[0]
        if word in wordMap:
            count=wordMap.get(word)
            wordMap[word] = count+1
        else:
            wordMap[word] = 1
    counter = 1
    for key in wordMap.keys():
        if (util.emptyString(key) ==0):
            sql1="insert into clean_keywords1 values ("+str(counter)+",'"+key+"',"+str(wordMap[key])+","+str(0)+")"
            print sql1
            cursor.execute(sql1)
            conn.commit()
            counter = counter+1
            
def calculateTFIDF():
    """
    calculates the term frequency- inverse document frequency and stores in the table
    """
    conn = db.getDBConnection()
    cursor = conn.cursor()
    sql = "select word from clean_keywords1"
    print sql
    rows = db.executeSQL(conn, sql)
    wordTFMap = {}
    wordDFMap = {}
    for row in rows:
        word=row[0]
        sql1 = "select repo_id from keywords1 where word='"+word+"'"
        print sql1
        res=db.executeSQL(conn, sql1)
        for row1 in res:
            repoId = row1[0]
            key = word + ':'+ str(repoId)
            if key in wordTFMap:
                tfCount = wordTFMap[key]
                wordTFMap[key] = tfCount+1
            else:
                wordTFMap[key] = 1
                if word in wordDFMap:
                    dfCount = wordDFMap[word]
                    wordDFMap[word] = dfCount+1
                else:
                    wordDFMap[word] =1
    
    for key in wordDFMap.keys():
        sql = 'update clean_keywords1 set df='+str(wordDFMap[key]) + " where word='"+key+"'"
        print sql
        cursor.execute(sql)
        conn.commit() 
        
    for key in wordTFMap.keys():
        row=key.split(":")
        sql = 'update keywords1 set tf='+str(wordTFMap[key])+" where word='"+row[0]+"' and repo_id="+str(row[1])
        print sql
        cursor.execute(sql)
        conn.commit()            

def loadStopWords():
    f=open("/home/raju/Work/githubdata/GitHubTrends/stopwords","r")
    stopWords=f.read()
    stopWords=stopWords.split("\n")
    global stopWordSet
    for word in stopWords:
        stopWordSet.add(word.strip())

#Entrypoint
stopWordSet = set()
getdata()
cleanKeyWords()
calculateTFIDF()
