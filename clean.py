#!/usr/bin/env python
import sys
import hashlib
import heapq
import random
import io
from pymongo import ReplicaSetConnection
from pymongo import ReadPreference
from pymongo import MongoClient
import pymongo
#conn = ReplicaSetConnection('localhost', replicaSet='jlu')
#db.read_preference = ReadPreference.SECONDARY
conn = pymongo.Connection()
db = conn.sina
def cleanquerycache():
    print db.cache.find().count()
    count = 0
    for n in db.cache.find({},{"_id":1}):
        count += 1
        if count % 100 == 0:
            print count
        db.cache.remove({"_id":n["_id"]})
    print db.cache.find({"query":{"$exists":1}}).count()

if __name__ == "__main__":
    cleanquerycache()
