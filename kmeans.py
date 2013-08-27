'''
Created on 29-Jul-2013

@author: rajuc
'''
import numpy as np
from scipy.cluster.vq import vq, kmeans
import src.git.util.mysqldatabase as db
from scipy.sparse import *
from scipy import *
from math import log
from sklearn import metrics
from sklearn.cluster import KMeans
from time import time

def getRepos():
    sql = 'select id, language from repository order by id ASC'
    con = db.getDBConnection()
    rows=db.executeSQL(con, sql);
    repoList = []
    global repoLangMap
    for row in rows:
        repoList.append(row[0])
        repoLangMap[row[0]] = row[1]
    return repoList

def getCleanKeywords():
    con = db.getDBConnection()
    sql = 'select word, df from clean_keywords1 where df>5'
    cleanWordRows = db.executeSQL(con, sql)
    counter =0
    wordDFMap ={}
    for row in cleanWordRows:
        word = row[0]
        df = row[1]
        wordDFMap[word] = str(counter)+":"+str(df)
        counter = counter+1
    return wordDFMap
   
def preapreData():
    con = db.getDBConnection()
    rowCount =0
    global repoLangMap    
    for repoId in repoList:
        lang = repoLangMap[int(repoId)]
        if lang!='' and lang is not None:
            langIndex=langMap[lang]
            S[rowCount, langIndex] = 10 
        sql2 = 'select word, tf from keywords1 where repo_id= '+ str(repoId)
        #print sql2
        res = db.executeSQL(con, sql2)
        #print len(res), repoId
        
        for row in res:
            word = row[0]
            tf = int(row[1])
            if word in wordDFMap:
                val=wordDFMap[word]
                index = int(val.split(":")[0])
                df = int(val.split(":")[1])
                #print tf * math.log(float(noOfRepos/df)), tf, df, noOfRepos
                print rowCount, index
                if index >6000:
                    print '<====== something is wrong =======>'
                S[rowCount, index] = tf * math.log(float(noOfRepos/df))
           
        rowCount = rowCount + 1

def getLanguage():
    con = db.getDBConnection()
    sql = 'select distinct language from repository'
    res = db.executeSQL(con, sql)
    global noOfWords
    global langMap
    index=noOfWords
    print 'languages index' + str(index)
    for row in res:
        lang = row[0]
        if lang !='':
            print lang
            langMap[lang] = index
            index += 1

t2 = time()        
repoLangMap = {}
langMap = {}
repoList=getRepos()
wordDFMap=getCleanKeywords()
noOfWords=len(wordDFMap)
getLanguage()
 
noOfRepos = len(repoList)
noOfKeyWords = len(wordDFMap) + len(langMap)  
print noOfRepos, noOfKeyWords
S = dok_matrix((noOfRepos,noOfKeyWords), dtype=float32)
print 'time taken for preparing data::' + str(time()-t2)
preapreData() 
t3 = time()
print 'time taken for preparing data::' + str(t3-t2)
t0 = time()
#km=KMeans(n_clusters=1000, init='k-means++', max_iter=100, n_init=10,
#                verbose=1, n_jobs=-2)

#output=km.predict(S.toarray)
#np.ndarray.tofile(output,'/home/raju/Work/clusteroutput')
#print output


# computing K-Means with K = 2 (2 clusters)
print 'shape of array', S.get_shape()
centroids,_ = kmeans(S.toarray(),100)
np.ndarray.tofile(centroids,'/home/raju/Work/newclustercentroids_100')
print centroids

# assign each sample to a cluster
idx,_ = vq(S.toarray(),centroids)
np.ndarray.tofile(idx,'/home/raju/Work/newclusteroutput2_1000')
print idx

t1 = time()
print 'kmeans time::' + str(t1-t0)

