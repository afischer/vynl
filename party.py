import sqlite3
import os
import marshal as m
import time
##added a comment to test broken commits
def partyExists(key):
    try:
        conn = sqlite3.connect('parties.db')
        c = conn.cursor()
        n=len(c.execute("SELECT * FROM uniques WHERE url=?",(key,)))
        return n>0
    except:
        return False

def scrub(query):
    return "["+''.join(x for x in query if x.isalnum())+"]"

class Party:
    # Adds unique key to uniques database and creates a database with a name
    def __init__(self, key, dj=0):
        self.k = key #scrub(key)
        #print self.k
        self.db = 'parties.db'
        conn = sqlite3.connect('parties.db')
        c = conn.cursor()
        try:
            self.active= len(c.execute("SELECT (url) FROM uniques WHERE url=?",(self.k,)).fetchall())
        except:
            c.execute("CREATE TABLE uniques (url TEXT)")
            self.active= False
        #print self.active
        if (self.active):
            #print dj
            self.dj=c.execute("SELECT ip FROM djs WHERE party=?",(self.k,)).fetchall()[0][0]
            #print self.dj
            conn.close()
            return
        #print "why"
        #conn2=sqlite3.connect(self.db)
        #c2=conn2.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS songs (videoid TEXT, imgURL TEXT, upvotes REAL, downvotes REAL, name TEXT, artist TEXT, total REAL, upvoteip BLOB, downvoteip BLOB, timestamp REAL,played INTEGER, party TEXT)")
        conn.commit()
        self.addDJ(dj)
        c.execute("INSERT OR REPLACE INTO uniques (url) VALUES (?)", (self.k,))
        conn.commit()
        conn.close()
        self.dj=dj
        self.active=True
        #print "here"

    def addSong(self,vid,imgURL,title,artist):
        if self.active:
            #print "adding"
            conn=sqlite3.connect(self.db)
            x=m.dumps([])
            y=m.dumps([])
            args=(vid,imgURL,title,artist,x,y,self.k,)
            c=conn.cursor()
            try:
                c.execute("INSERT INTO songs (videoid,imgURL,name,artist,upvotes,downvotes,total,upvoteip,downvoteip,played,party) VALUES (?,?,?,?,0,0,0,?,?,0,?)",args)
            except Exception as e:
                #raise e
                L=c.execute("SELECT * FROM songs WHERE videoid=? AND played=1 AND party=? ",(vid,self.k,)).fetchall()
                if len(L)==0:
                    conn.close()
                    #print "in queue!"
                    return "The song is already in the queue!"
                c.execute("REPLACE INTO songs (videoid,imgURL,name,artist,upvotes,downvotes,total,upvoteip,downvoteip,played,party) VALUES (?,?,?,?,0,0,0,?,?,0,?)",args)
            conn.commit()
            conn.close()
        else:
            return "Party not active."

    def removeSong(self,vid):
        if self.active:
            conn=sqlite3.connect(self.db)
            c=conn.cursor()
            c.execute("DELETE FROM songs WHERE videoid=? AND party=?",(vid,self.k))
            conn.commit()
            conn.close()
        else:
            return "Party not active."

    def upVote(self,vid, ip):
        if self.active:
            conn=sqlite3.connect(self.db)
            c=conn.cursor()
            num=c.execute("SELECT upvotes,total,upvoteip, downvotes, downvoteip FROM songs WHERE videoid=? AND party=?",(vid,self.k,)).fetchone()
            x=m.loads(num[2])
            y=m.loads(num[4])
            if ip not in x:
                if ip in y:
                    x.append(ip)
                    y.remove(ip)
                    x=m.dumps(x)
                    y=m.dumps(y)
                    c.execute("UPDATE songs SET upvotes=?, total=?, upvoteip=?, downvotes=?, downvoteip=? WHERE videoid=? AND party=",(num[0]+1,num[1]+2,x, num[3]-1,y,vid,self.k,))
                else:
                    x.append(ip)
                    x=m.dumps(x)
                    c.execute("UPDATE songs SET upvotes=?, total=?, upvoteip=? WHERE videoid=? AND party=?",(num[0]+1,num[1]+1,x,vid,self.k,))
            elif ip in x:
                x.remove(ip)
                x=m.dumps(x)
                c.execute("UPDATE songs SET upvotes=?, total=?, upvoteip=? WHERE videoid=? AND party=?",(num[0]-1,num[1]-1,x,vid,self.k,))

            conn.commit()
            conn.close()
        else:
            return "Party not active."


    def downVote(self,vid, ip):
        if self.active:
            conn=sqlite3.connect(self.db)
            c=conn.cursor()
            num=c.execute("SELECT downvotes,total,downvoteip, upvotes, upvoteip FROM songs WHERE videoid=? AND party=?",(vid,self.k,)).fetchone()
            x=m.loads(num[2])
            y=m.loads(num[4])
            if ip not in x:
                if ip in y:
                    x.append(ip)
                    y.remove(ip)
                    x=m.dumps(x)
                    y=m.dumps(y)
                    c.execute("UPDATE songs SET downvotes=?, total=?, downvoteip=?, upvotes=?, upvoteip=? WHERE videoid=? AND party=?",(num[0]+1,num[1]-2,x, num[3]-1,y,vid,self.k,))
                    if (num[1]-2) <=-5:
                        conn.close()
                        self.removeSong(vid)
                        return
                else:
                    x.append(ip)
                    x=m.dumps(x)
                    c.execute("UPDATE songs SET downvotes=?, total=?, downvoteip=? WHERE videoid=? AND party=?",(num[0]+1,num[1]-1,x,vid,self.k,))
                    if (num[1]-1)<=-5:
                        conn.close()
                        #print "gonna remove"
                        self.removeSong(vid)
                        return
            elif ip in x:
                x.remove(ip)
                x=m.dumps(x)
                c.execute("UPDATE songs SET downvotes=?, total=?, downvoteip=? WHERE videoid=? AND party=?",(num[0]-1,num[1]+1,x,vid,self.k,))

            conn.commit()
            conn.close()
        else:
            return "Party not active."

    def end(self):
        if self.active:
            #os.system('rm "'+self.db+'"')
            self.active=False
            conn = sqlite3.connect('parties.db')
            c=conn.cursor()
            c.execute("DELETE FROM uniques WHERE url=?",(self.k,))
            c.execute("DELETE FROM songs WHERE party=?",(self.k,))
            if self.getPlaying():
                c.execute("DELETE FROM playing WHERE party=?",(self.k,))
            conn.commit()
            conn.close()


    def getOrdered(self,ip): #{title: STRING, artist:STRING, videoID: STRING, upvotes: int, downvotes: int}
        if self.active:
            ret=[]
            conn=sqlite3.connect(self.db)
            c=conn.cursor()
            it=c.execute("SELECT name,artist,videoid,imgURL, upvotes, downvotes,upvoteip,downvoteip FROM songs WHERE played=0 AND party=? ORDER BY total DESC",(self.k,)).fetchall()
            #print c.execute("SELECT party FROM songs").fetchall()
            conn.close()
            for x in it:
                ret.append({"songname":x[0],"songartist":x[1],"songID":str(x[2]),"albumarturl":str(x[3]),"upvotes":x[4],"downvotes":x[5],"upvoted":(ip in m.loads(x[6])), "downvoted":(ip in m.loads(x[7]))})
            return ret
        else:
            return "Party not active."

    def addDJ(self,dj):
        conn=sqlite3.connect(self.db)
        c=conn.cursor()
        try:
            c.execute("CREATE TABLE djs (party TEXT, ip TEXT)")
        except:
            pass
        c.execute("INSERT INTO djs(party, ip) VALUES (?,?)",(self.k,dj,))
        conn.commit()
        conn.close()
        #print "ayy"

    def getDJ(self):
        if self.active:
            return self.dj
        else:
            return "Party not active."


    def playSong(self,vid):
        if self.active:
            #print "playtime!"
            x=time.time()
            conn=sqlite3.connect(self.db)
            c=conn.cursor()
            try:
                c.execute("UPDATE playing SET played=1 WHERE party=?",(self.k,))
            except:
                c.execute("CREATE TABLE playing (videoid TEXT, imgURL TEXT, upvotes REAL, downvotes REAL, name TEXT, artist TEXT, total REAL, upvoteip BLOB, downvoteip BLOB, timestamp REAL,played INTEGER, party TEXT)")
            z=c.execute("SELECT videoid FROM playing WHERE party=?",(self.k,)).fetchall()
            if len(z)==1:
                z=z[0][0]
                final=len(c.execute("SELECT * FROM songs WHERE videoid=? AND party=?",(z,self.k,)).fetchall()) == 0
                if final:
                    c.execute("INSERT INTO songs SELECT * FROM playing WHERE party=?",(self.k,))
            c.execute("DELETE FROM playing WHERE party=?",(self.k,))
            c.execute("INSERT INTO playing SELECT * FROM songs WHERE videoid=? AND party=?",(vid,self.k,))
            c.execute("DELETE FROM songs WHERE videoid=? AND party=?",(vid,self.k,))
            c.execute("UPDATE playing SET timestamp=? WHERE videoid=? AND party=?", (x,vid,self.k,))
            conn.commit()
            conn.close()
        else:
            return "Party not active."

    def getPlayed(self):
        if self.active:
            ret=[]
            conn=sqlite3.connect(self.db)
            c=conn.cursor()
            it=c.execute("SELECT name,artist,videoid,imgURL FROM songs WHERE played=1 AND party=? ORDER BY timestamp ASC",(self.k,)).fetchall()
            conn.close()
            for x in it:
                #print x[0]
                ret.append({"songname":x[0],"songartist":x[1],"songID":str(x[2]),"albumarturl":str(x[3])})
            return ret
        else:
            return "Party not active."

    def getSongs(self):
        if self.active:
            conn=sqlite3.connect(self.db)
            c=conn.cursor()
            L=c.execute("SELECT videoid,imgURL,name,artist FROM " +self.k).fetchall()
            conn.close()
            return L
        else:
            return "Party not active."


    def getPlaying(self):
        if self.active:
            try:
                ret=[]
                conn=sqlite3.connect(self.db)
                c=conn.cursor()
                it=c.execute("SELECT name,artist,videoid,imgURL FROM playing WHERE party=?",(self.k,)).fetchall()
                conn.close()
                for x in it:
                    #print x[0]
                    ret.append({"songname":x[0],"songartist":x[1],"songID":str(x[2]),"albumarturl":str(x[3])})
                return ret
            except Exception as e:
                raise e
                return []
        else:
            return "Party not active."
