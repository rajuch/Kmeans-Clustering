'''
Created on 25-Jul-2013

@author: rajuc
'''
import os, sys
import gzip
import re
import MySQLdb as mdb
import src.git.util.mysqldatabase as db
import src.git.util.util as util
from json import JSONDecoder


FLAGS = re.VERBOSE | re.MULTILINE | re.DOTALL
WHITESPACE = re.compile(r'[ \t\n\r]*', FLAGS)
repoIdCounter=1

def parseJson(s, conn):
    """
    Parses the json file and calls populate method for inserting the data into the 'repository' table
    input: s- json string
    conn- database connection
    """
    try:
        _w=WHITESPACE.match
        decoder = JSONDecoder()
        s_len = len(s)
        end = 0
        while end != s_len:
            obj, end = decoder.raw_decode(s, idx=_w(s, end).end())
            end = _w(s, end).end()
            refType =''
            if obj['type'] == 'CreateEvent':
                try:
                    refType = obj['payload']['ref_type']
                except Exception as e:
                    print e
                if refType == 'repository':
                    populateRepoTable(obj, conn)
    except Exception as e:
        #print 'Error in line:'+str(sys.exc_traceback.tb_lineno)
        print sys.exc_traceback.tb_lineno 
        pass

def populateRepoTable(obj, conn): 
    """
    Inserts the data into the table
    input: obj- json object
    conn- database connection
    """
    try:
        cursor = conn.cursor()

        user = obj['actor']
        if type(user) == dict:
            user = user['login']
        loginName = ''
        repoUrl =''
        repoName = ''
        repoId =0
        language =''
        repoDesc =''
        global repoIdCounter
        try:    
            loginName = obj['actor_attributes']['login']
        except Exception as e:
            try:
                loginName = obj['actor']['login']
            except Exception as e:
                print e, sys.exc_traceback.tb_lineno 
            print e, sys.exc_traceback.tb_lineno 
            pass
        try:    
            repoId = obj['repository']['id']
        except Exception as e:
            try:    
                repoId = obj['repo']['id']
            except Exception as e:
                pass
            print e, sys.exc_traceback.tb_lineno 
            pass
        try:
            repoUrl = obj['url']
        except Exception as e:
            print e, sys.exc_traceback.tb_lineno 
            pass    
        try:
            repoName = obj['repository']['name']
            
            if '/' in repoName:
                repoUrl = 'https://github.com/' + repoName
                repoName = repoName.split("/")[1]
        except Exception as e:
            try:
                repoName = obj['repo']['name']
                if '/' in repoName:
                    repoUrl = 'https://github.com/' + repoName
                    repoName = repoName.split("/")[1]
            except Exception as e:
                pass
            print e, sys.exc_traceback.tb_lineno 
            pass
        
        if repoUrl=='':
            if loginName!='' and repoName!='':
                repoUrl = 'https://github.com/' + loginName+"/"+repoName
        
        try:
            repoDesc = obj['repository']['description']
        except Exception as e:
            try:
                repoDesc = obj['repo']['description']
            except Exception as e:
                try:
                    repoDesc = obj['payload']['description']
                except Exception as e:
                    print e
            print e, sys.exc_traceback.tb_lineno 
            pass
        try:
            createdAt = obj['created_at']
        except Exception as e:
            try:
                createdAt = obj['repo']['created_at']
            except Exception as e:
                pass
            print e, sys.exc_traceback.tb_lineno 
            pass
        print 'desc::' + repoDesc
        
        
        if not util.emptyString(repoDesc):
            sql = "INSERT INTO repository VALUES ("+str(repoIdCounter)+",'"+repoName+"','"+mdb.escape_string(repoUrl)+"','"+repoDesc+"','"+loginName+"','"+language +"',"+ str(util.getFloatTime(createdAt))+")"
            print sql
            try:
                cursor.execute(sql)
                conn.commit()
                repoIdCounter = repoIdCounter+1
            except Exception as e:
                print e
            
    except Exception as e:
        print 'Error in line:'
        print e
        pass

def updateRepoLanguage():
    """
    update the language of the repository
    """
    try:
        conn = mdb.connect(host="localhost",user="root",passwd="root",db="github")
        clusterdb = mdb.connect(host="localhost",user="root",passwd="root",db="github_cluster")
        cursor = clusterdb.cursor()
        sql ='select distinct url from repository'
        rows=db.executeSQL(clusterdb, sql)
        for row in rows:
            url = row[0]
            sql2 = 'select repo_language from AllEvents where repo_url ="' + url+'" order by repo_language desc limit 1'
            langRows=db.executeSQL(conn,sql2)
            for row in langRows:
                lang = row[0]
                sql3 = 'update repository set language = "' + lang + '" where url="'+ url +'"'
                print sql3
                try:
                    cursor.execute(sql3)
                    clusterdb.commit()
                except Exception as e:
                    print e
            
    except Exception as e:
        print e

def readFiles():
    """
    read json files and process it
    """
    conn= db.getDBConnection()   
    for zippedFile in os.listdir("."):
        print zippedFile
        try:
            f = gzip.open(zippedFile, 'rb')
            file_content = f.read()
            parseJson(file_content, conn)
        except Exception as e:
            print 'Error in line:'+str(sys.exc_traceback.tb_lineno)
            pass
        finally:
            f.close() 

#Entry point
path = "/home/raju/Work/githubdata/GitHubTrends/2012data/April"        
os.chdir(path)
readFiles() 
updateRepoLanguage()     