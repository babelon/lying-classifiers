#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pymongo import Connection
import codecs
import sys
import tok

tk = tok.Tokenizer()

#connection = Connection('ec2-184-169-148-202.us-west-1.compute.amazonaws.com', 27017)
connection = Connection('184.169.148.202', 27017)
db = connection.lietome
fragments = db.fragments
entities = db.entities
people = db.people
votes = db.votes

def printStatsForPeople():
    for person in people.find():
        print " "
        print "==================================="
        print person["first_name"] + " " + person["last_name"]
        print "==================================="
        
        votesCast = 0
        for vote in votes.find():
            if vote["voter"] == person["_id"]:
                votesCast += 1
            fragmentForVote = fragments.find_one({"_id" : vote["fragment"]})
            voter = people.find_one({"_id" : vote["voter"]})
            authorOfFragment = fragmentForVote["author"]
            if authorOfFragment == person["_id"]:
                if (not fragmentForVote["truth"]) and vote["truth"]:
                    print "\tfooled " + format(voter["first_name"])
        print "-----------------------"
        print "\tcast " + format(votesCast) + " votes"
        
def printPeople():
    for person in people.find():
        print person["first_name"] + " " + person["last_name"]
        #print person["_id"]
        #idStr = "ObjectId(" + person["_id"] + ")"
        for fragment in fragments.find({ "author" : person["_id"] }):
            print "\t" + format(fragment["_id"])

def printEntities():
    for fragment in fragments.find():
        entity = entities.find_one({"_id" : fragment["entity"]})
        print entity["name"]
        print entity["etype"]

def printVotePatterns():
    for fragment in fragments.find(): # hopelessly inefficient; should be inverted
        entity = entities.find_one({"_id" : fragment["entity"]})
        author = people.find_one({"_id" : fragment["author"]})
        print author["first_name"] + "'s " + format(fragment["truth"]).lower() + " review of " + entity["name"] + ":"
        correctGuesses = 0
        incorrectGuesses = 0
        for vote in votes.find():
            if vote["fragment"] == fragment["_id"]:
                if vote["truth"] == fragment["truth"]:
                    correctGuesses += 1
                else:
                    incorrectGuesses += 1
                    totalGuesses = correctGuesses + incorrectGuesses
        if totalGuesses > 0:
            percent = 100.0 * correctGuesses / totalGuesses
            print "\t" + format(percent)[0:5] + "%\t" + format(correctGuesses) + "/" + format(totalGuesses)
        else:
            percent = 0

def defaultBehavior():
    printVotePatterns()

if __name__ == '__main__' :
    defaultBehavior()

#printVotePatterns()
#printStatsForPeople()
                
#for fragment in fragments.find():
#    if fragment["truth"]:
#        prefix = "t_"
#    else:
#        prefix = "d_"
#    filename = prefix + str(fragment["_id"])
#    path = "./" + sys.argv[1] + "/" + filename
#    out = codecs.open(path, "w", "utf-8")
#    txt = fragment["text"]
#    tokenizedTxt = " ".join(tk.tokenize(txt))
#    out.write(tokenizedTxt)
