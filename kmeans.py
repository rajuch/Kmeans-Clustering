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
    """
    retrieve the repository ids, languages from the database
    """
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
    """
    retrieve the words, document frequency>5 from the database
    """
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
    """
    prepares the sparse matrix for kmeans
    """
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
                print rowCount, index
                S[rowCount, index] = tf * math.log(float(noOfRepos/df))
           
        rowCount = rowCount + 1

def getLanguage():
    """
    retireves the distinct languages from the database
    """
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

def decodeClusterOutput(path,fileName):
    """
    decodes the cluster output(binary format) and writes to the new file
    input: fileName - cluster output file name
    """
    repoList=getRepos()
    a=np.fromfile(path+fileName,dtype=np.int64)
    count=0
    clusterMap ={}
    f = open(path+'newoutput_100','w')
    for key in a:
        if key in clusterMap:
            indexes= clusterMap[key] 
            clusterMap[key] = indexes + ":" + str(count) 
        else :
            clusterMap[key] = str(count)
        count +=1

    for key in clusterMap.keys():
        indexes = clusterMap[key]
        arr = indexes.split(":")
        string =''
        for val in arr:
            if string =='':
                string= str(repoList[int(val)])
            else:
                string= string + ","+str(repoList[int(val)])
        print string
        f.write(string)
        f.write('\n')
    f.close()


"""
variables declaration
"""
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
#initialize the sparse matrix with the size of repositories and keywords
S = dok_matrix((noOfRepos,noOfKeyWords), dtype=float32)
print 'time taken for preparing data::' + str(time()-t2)
preapreData() 
t3 = time()
print 'time taken for preparing data::' + str(t3-t2)
t0 = time()

path = '/home/raju/Work/Cluster/'
clusterCentroidsFile = 'newclustercentroids_100'
clusterOutputFile = 'newclusteroutput2_1000'

# computing K-Means with K = 100 (100 clusters)
print 'shape of array', S.get_shape()
centroids,_ = kmeans(S.toarray(),100)
np.ndarray.tofile(centroids,path+clusterCentroidsFile)
print centroids

# assign each sample to a cluster
idx,_ = vq(S.toarray(),centroids)
np.ndarray.tofile(idx,path+clusterOutputFile)
print idx

decodeClusterOutput(path,clusterOutputFile)
t1 = time()
print 'kmeans time::' + str(t1-t0)

