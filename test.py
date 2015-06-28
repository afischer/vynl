#-*- coding: utf-8 -*-
import party,os

#try:
x=party.Party("hey","195.196.1.1")
song= "xxx5"
#print song
song2="yyy5"
song3="fff5"
song4="qqqqq"
song5="asdf"
x.addSong(song,"exampleimage","name","channelman")
x.addSong(song2,"exampleimage","name2","channelwhat")
x.addSong(song3,"exampleimage","name3","channelwho")
x.addSong(song4,"exampleimage","name4","itstaytay")
x.addSong(song5,"exampleimage","name5","asdf")
x.addSong(song5,"exampleimage","name5","asdf")
#x.playSong(song)
x.removeSong(song5)
x.addSong(song5,"exampleimage","name5","asdf")
#x.addSong(song,"exampleimage","name","channelman")
#for i in xrange(20):
#	x.upVote(song,"199")
for i in xrange(11):
	x.downVote(song,"167")
for i in xrange(13):
	x.upVote(song2,"189")
for i in xrange(20):
	x.downVote(song3,"155")
for i in xrange(30):
	x.downVote(song4,"155")
for i in xrange(50):
	x.upVote(song4,"155")
x.playSong(song4)
x.playSong(song5)
print x.getPlaying()
y=party.Party("hey")
print y.getDJ()
print y.getOrdered("167")
print x.getPlayed()
x.addSong(song4,"exampleimage","name4","itstaytay")
print x.getPlayed()
print y.getOrdered("167")
x.end()
#except:
#	os.system("rm uniques.db;rm hey.db")
