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

players = dict()
statements = dict()
statementsAuthentic = dict()
statementsDeceptive = dict()

GUESSED_CORRECTLY = "guessed_correctly"
GUESSED_INCORRECTLY = "guessed_incorrectly"

VOTES_CAST = "votes_cast"
FOOLED = "fooled"
FOOLED_BY = "fooled_by"
THWARTED = "thwarted"
THWARTED_BY = "thwarted_by"
CORRECT_GUESSES = "correct_guesses"
INCORRECT_GUESSES = "incorrect_guesses"
CORRECT_GUESSES_FOR_TRUTHS = "correct_guesses_for_truths"
CORRECT_GUESSES_FOR_LIES = "correct_guesses_for_lies"
INCORRECT_GUESSES_FOR_TRUTHS = "incorrect_guesses_for_truths"
INCORRECT_GUESSES_FOR_LIES = "incorrect_guesses_for_lies"


def truthDescription(truthValue):
    if truthValue:
        return "authentic"
    return "deceptive"

#
# should be doable recursively with typing...
#

def descriptionOfEntity(id):
    entity = entityWithID(id)
    rstr =  "the " + entity["etype"] + " '" + entity["name"] + "'"
    if "location" in entity:
        rstr += " in " + entity["location"]
    return rstr

def descriptionOfFragment(id, includeText):
    fragment = fragmentWithID(id)
    author = personWithID(fragment["author"])
    authorName = fullNameForPerson(author)
    #entityName = entityWithID(fragment["entity"])["name"]        
    # assume it's a review
    desc = authorName + "'s " + truthDescription(fragment["truth"]) + " " + format(fragment["rating"]) + "-star review of " + descriptionOfEntity(fragment["entity"])
    if includeText:
        desc += ":\n" + fragment["text"]
    return desc
    

def fragmentWithID(id):
    return fragments.find_one({"_id" : id})

def personWithID(id):
    return people.find_one({"_id" : id})

def entityWithID(id):
    return entities.find_one({"_id" : id})

def voteWithID(id):
    return votes.find_one({"_id" : id})

def fullNameForPerson(person):
    return person["first_name"] + " " + person["last_name"]

def initPlayer(playerID):
    players[playerID] = dict()
    players[playerID][VOTES_CAST] = 0
    players[playerID][FOOLED] = dict()
    players[playerID][FOOLED_BY] = dict()
    players[playerID][THWARTED] = dict()
    players[playerID][THWARTED_BY] = dict()
    players[playerID][CORRECT_GUESSES] = []
    players[playerID][CORRECT_GUESSES_FOR_TRUTHS] = []
    players[playerID][CORRECT_GUESSES_FOR_LIES] = []
    players[playerID][INCORRECT_GUESSES] = []
    players[playerID][INCORRECT_GUESSES_FOR_TRUTHS] = []
    players[playerID][INCORRECT_GUESSES_FOR_LIES] = []
    
def XedNTimesString(x, n):
    if n == 0:
        return "never " + x
    else:
        suffix = ""
        if n == 1:
            suffix = " once"
        elif n == 2:
            suffix = " twice"
        else:
            suffix = " " + format(n) + " times"
        return x + suffix

            

def buildStructs():
    for vote in votes.find():
        voterID = vote["voter"]
        if voterID not in players:
            initPlayer(voterID)
        players[voterID][VOTES_CAST] += 1
        fragmentForVote = fragmentWithID(vote["fragment"])
        fragmentID = vote["fragment"]
        authorOfFragment = fragmentForVote["author"]
        if authorOfFragment not in players:
            initPlayer(authorOfFragment)
        if fragmentID not in statements:
            statements[fragmentID] = dict()
            statementsAuthentic[fragmentID] = dict() #!
            statementsDeceptive[fragmentID] = dict() #!
            statements[fragmentID]["truth"] = fragmentForVote["truth"]
            if fragmentForVote["truth"]:
                statements[fragmentID][GUESSED_CORRECTLY] = []
                statements[fragmentID][GUESSED_INCORRECTLY] = []
                statementsAuthentic[fragmentID][GUESSED_CORRECTLY] = [] #!
                statementsAuthentic[fragmentID][GUESSED_INCORRECTLY] = [] #!
            else:
                statements[fragmentID][THWARTED_BY] = []
                statements[fragmentID][FOOLED] = []
                statementsDeceptive[fragmentID][THWARTED_BY] = [] #!
                statementsDeceptive[fragmentID][FOOLED] = [] #!
        if fragmentForVote["truth"]:
            if vote["truth"]:
                key = GUESSED_CORRECTLY
            else:
                key = GUESSED_INCORRECTLY
        else:
            if vote["truth"]:
                key = FOOLED
            else:
                key = THWARTED_BY
        
        statements[fragmentID][key].append(voterID)
        if fragmentForVote["truth"]: # TO-DO: rewrite, with sub-dictionarys
            statementsAuthentic[fragmentID][key].append(voterID)
        else:
            statementsDeceptive[fragmentID][key].append(voterID)

        if vote["truth"] == fragmentForVote["truth"]:
            players[voterID][CORRECT_GUESSES].append(fragmentForVote["_id"])
            if not vote["truth"]:
                gt = CORRECT_GUESSES_FOR_LIES
                if authorOfFragment not in players[voterID][THWARTED]:
                    players[voterID][THWARTED][authorOfFragment] = 0
                players[voterID][THWARTED][authorOfFragment] += 1
                if voterID not in players[authorOfFragment][THWARTED_BY]:
                    players[authorOfFragment][THWARTED_BY][voterID] = 0
                players[authorOfFragment][THWARTED_BY][voterID] += 1
            else:
                gt = CORRECT_GUESSES_FOR_TRUTHS
            players[voterID][gt].append(fragmentForVote["_id"])
        else:
            players[voterID][INCORRECT_GUESSES].append(fragmentForVote["_id"])
            if not vote["truth"]:
                gt = INCORRECT_GUESSES_FOR_LIES
                if authorOfFragment not in players[voterID][FOOLED_BY]:
                    players[voterID][FOOLED_BY][authorOfFragment] = 0
                players[voterID][FOOLED_BY][authorOfFragment] += 1
                if voterID not in players[authorOfFragment][FOOLED]:
                    players[authorOfFragment][FOOLED][voterID] = 0
                players[authorOfFragment][FOOLED][voterID] += 1
            else:
                gt = INCORRECT_GUESSES_FOR_TRUTHS
            players[voterID][gt].append(fragmentForVote["_id"])
                #
                #
        

        voter = personWithID(voterID)


def printPlayerStats():
    for playerID in players:
        player = players[playerID]
        playerOb = personWithID(playerID)
        print ""
        print fullNameForPerson(playerOb) + " (" + playerOb["email"] + ")"
        thwartCount = len(player[THWARTED])
        fooledByCount = len(player[FOOLED_BY])
        incorrectGuessCount = len(player[INCORRECT_GUESSES])
        correctGuessCount = len(player[CORRECT_GUESSES])
        print "\tcast " + format(player[VOTES_CAST]) + " votes " #+ "(" + format(thwartCount + fooledByCount) + " for fake statements),"

        print "\t" + XedNTimesString("guessed correctly", correctGuessCount) + " and " + XedNTimesString("guessed incorrectly", incorrectGuessCount)        
        for foolee in player[FOOLED]:
            print "\t" + XedNTimesString( "fooled " + fullNameForPerson(personWithID(foolee)), player[FOOLED][foolee])
        for fooler in player[FOOLED_BY]:
            print "\t" + XedNTimesString( "was fooled by " + fullNameForPerson(personWithID(fooler)), player[FOOLED_BY][fooler])
            '''
            if fooler in players:
                if playerID in players[fooler][FOOLED_BY]:
                    print "\t\tbut [] fooled " + personWithID(fooler)["first_name"] + " " + format(players[fooler][FOOLED_BY][playerID]) + " time(s)"
            '''
            
def printStatementStats():
    for statementID in statements:
        print ""
        print descriptionOfFragment(statementID, False)
        statement = statements[statementID]
        if statement["truth"]:
            for personID in statement[GUESSED_CORRECTLY]:
                print "\t was correctly identified as authentic by " + fullNameForPerson(personWithID(personID))
            for personID in statement[GUESSED_INCORRECTLY]:
                print "\t was incorrectly classified as deceptive by " + fullNameForPerson(personWithID(personID))
        else:
            for personID in statement[FOOLED]:
                print "\t fooled " + fullNameForPerson(personWithID(personID))
            for personID in statement[THWARTED_BY]:
                print "\t was thwarted by " + fullNameForPerson(personWithID(personID))
        
    '''
    for statementID in statementsAuthentic:
        print ""
        print descriptionOfFragment(statementID, False)
        statement = statementsAuthentic[statementID]
        #for personID in statement[GUESSED_CORRECTLY]:
        #    print "\t was correctly identified as authentic by " + fullNameForPerson(personWithID(personID))
        #for personID in statement[GUESSED_INCORRECTLY]:
        #   print "\t was incorrectly classified as deceptive by " + fullNameForPerson(personWithID(personID))
    for statementID in statementsDeceptive:
        print ""
        print descriptionOfFragment(statementID, False)
        statement = statementsDeceptive[statementID]
        for personID in statement[FOOLED]:
            print "\t fooled " + fullNameForPerson(personWithID(personID))
        for personID in statement[THWARTED_BY]:
            print "\t was thwarted by " + fullNameForPerson(personWithID(personID))
    '''
            

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
            #fragmentForVote = fragments.find_one({"_id" : vote["fragment"]})
            fragmentForVote = fragmentWithID(vote["fragment"])
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
    buildStructs()
    #printPlayerStats()
    printStatementStats()
    #printStatsForPeople()
    #printVotePatterns()

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
