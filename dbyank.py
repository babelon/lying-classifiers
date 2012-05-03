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

t_count = 0
d_count = 0
sizeOfSmallerSet = 0

for fragment in fragments.find():
    if fragment["truth"]:
        t_count += 1
    else:
        d_count += 1

print "t_count: " + format(t_count)
print "d_count: " + format(d_count)

if t_count > d_count:
    sizeOfSmallerSet = d_count
else:
    sizeOfSmallerSet = t_count

print "smaller: " + format(sizeOfSmallerSet)

t_file_count = 0
d_file_count = 0

counter = 0

for fragment in fragments.find():

    entity = entities.find_one({"_id" : fragment["entity"]})
    entityName =  entity["name"].replace(" ", "-")
    entityType = entity["etype"]
    author = people.find_one({"_id" : fragment["author"]})
    authorName = author["first_name"] + "-" + author["last_name"]
    rating = format(fragment["rating"])

    overLimit = False
    counter += 1
    print " "
    print counter

    if fragment["truth"]:
        prefix = "t_"
        t_file_count += 1
        print "true " + format(t_file_count)
        if t_file_count > sizeOfSmallerSet:
            overLimit = True
    else:
        prefix = "d_"
        d_file_count += 1
        print "deceptive " + format(d_file_count)
        if d_file_count > sizeOfSmallerSet:
            overLimit = True
    # if not overLimit:
    if True:
        print "writing file"
        filename = prefix + "r" + rating + "_" + entityName + "_" + authorName + "_" + str(fragment["_id"])
        path = "./" + sys.argv[1] + "/" + entityType + "/" + filename
        out = codecs.open(path, "w", "utf-8")
        txt = fragment["text"]
        tokenizedTxt = " ".join(tk.tokenize(txt))
        out.write(tokenizedTxt)
