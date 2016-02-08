#!/usr/bin/env pypy
import sys
import hashlib
import heapq
import random
import io
#from pymongo import ReplicaSetConnection
#from pymongo import ReadPreference
from pymongo import MongoClient
import pymongo

conn = MongoClient('localhost', replicaSet='jlu')
db = conn.sina
#db.read_preference = ReadPreference.SECONDARY

def hash():
    nodes = {}
    with io.open("/Volumes/Data/asxzy/datasets/weibo/weibo.celebrity",encoding="utf-8") as f:
        for line in f:
            nodes[int(line.split()[0])] = True
#    nodes = {}
    with io.open("/Volumes/Data/asxzy/datasets/weibo/weibo.10000",encoding="utf-8") as f:
        next(f)
        for line in f:
            nodes[int(line.split()[0])] = True
    count = 0
    for node in nodes:
        similarity(node)
        count += 1
        print count,len(nodes)

def similarity(query_node,topk = False):
    CACHE = db.cache
    def buildhash(nid,k=400):
        hashs = []
        cur = db.edges.find({"to":nid})
        edges = []
        for edge in cur:
            edges.append(edge["from"])
        record = {}
        record["node_id"] = nid
        if len(edges) > k:
            random.shuffle(edges)
        record["hash"] = [int(x) for x in edges[:k]]
        db.hashs.insert(record)

    query_node = int(query_node)
    res = CACHE.find_one({"node_id":query_node})
    if res != None:
        print "found cache of",query_node
        if topk != False and type(topk) == int:
            return res["cache"][:topk]
        else:
            return res["cache"]
    print "cache not found for ",query_node ,"trying top10k"
    JS = db.js
    NODES = db.nodes
    js = []
    for record in JS.find({"n1":query_node}):
        node = NODES.find_one({"node_id":record["n2"]})
        if node == None:
            node = {}
            node["node_id"] = record["n2"]
            node["screen_name"] = "User_"+str(record["n2"])
        js.append((node["node_id"],node["screen_name"],record["js"]))
    for record in JS.find({"n2":query_node}):
        node = NODES.find_one({"node_id":record["n1"]})
        if node == None:
            node = {}
            node["node_id"] = record["n2"]
            node["screen_name"] = "User_"+str(record["n2"])
        js.append((node["node_id"],node["screen_name"],record["js"]))
    if len(js) > 0:
        print "found in top 10k"
        js.sort(key=lambda x : -x[2])
        record = {}
        record["node_id"] = query_node
        record["cache"] = js
        CACHE.insert(record)
        if topk != False and type(topk) == int:
            return js[:topk]
        else:
            return js
    print "top10k not found"

    EDGES = db.edges
    HASHS = db.hashs
    neighbors = []
    for node in EDGES.find({"to":query_node},{"from":1}):
        neighbors.append(node["from"])
    similar = []
    for node in EDGES.find({"from":{"$in":neighbors}},{"to":1}):
        if node["to"] == query_node:
            continue
        similar.append(node["to"])
    nodes = []
    if topk != False and type(topk) == int:
        for n in NODES.find({"node_id":{"$in":similar}}).sort("in_degree",-1).limit(topk):
            node = {}
            node["node_id"] = n["node_id"]
            node["in_degree"] = n["in_degree"]
            node["out_degree"] = n["out_degree"]
            try:
                node["screen_name"] = n["screen_name"]
            except:
                node["screen_name"] = "User_"+str(node["node_id"])
            nodes.append(node)
    else:
        for n in NODES.find({"node_id":{"$in":similar}}):
            node = {}
            node["node_id"] = n["node_id"]
            node["in_degree"] = n["in_degree"]
            node["out_degree"] = n["out_degree"]
            try:
                node["screen_name"] = n["screen_name"]
            except:
                node["screen_name"] = "User_"+str(node["node_id"])
            nodes.append(node)
    print "there are ",len(nodes),"nodes"
    res_ms = []
    try:
        m1 = HASHS.find_one({"node_id":query_node},{"hash":1})["hash"]
    except:
        buildhash(query_node)
        HASHS.read_preference = ReadPreference.PRIMARY
        m1 = HASHS.find_one({"node_id":query_node},{"hash":1})["hash"]
        HASHS.read_preference = ReadPreference.SECONDARY
    for node in nodes:
        try:
            m2 = HASHS.find_one({"node_id":node["node_id"]},{"hash":1})["hash"]
        except:
            buildhash(node["node_id"])
            HASHS.read_preference = ReadPreference.PRIMARY
            m2 = HASHS.find_one({"node_id":node["node_id"]},{"hash":1})["hash"]
            HASHS.read_preference = ReadPreference.SECONDARY
        '''jaccard similarity'''
        JS = {}.fromkeys(m1+m2).keys()
        n1 = len(m1)+len(m2)-len(JS)
        try:
            ms = n1 / float(len(m1) + len(m2) - n1)
        except ZeroDivisionError:
            ms = 0
        if ms > 0 or topk != False:
            res_ms.append((node["node_id"],node["screen_name"],ms))
    res_ms.sort(key=lambda x : -x[2])
    if topk != False and type(topk) == int:
        return res_ms[:topk]
    else:
        record = {}
        record["node_id"] = query_node
        record["cache"] = res_ms
        CACHE.insert(record)
        return res_ms


if __name__ == "__main__":
    hash()
