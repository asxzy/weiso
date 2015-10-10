#!/usr/bin/env python
import pymongo
import sys
import hashlib
import heapq
import random
import io

def hash():
    #conn = pymongo.Connection()
    conn = pymongo.MongoClient("/tmp/mongodb-27017.sock")
    db = conn.sina
    def buildhash(nid,k=400):
        hashs = []
        edges = []
        for edge in db.edges.find({"to":nid}):
            edges.append(edge["from"])
        #for edge in cur:
         #   hashs.append(hashlib.md5(str(edge["from"])).hexdigest()[8:-8])
        record = {}
        record["node_id"] = nid
        #record["hash"] = heapq.nsmallest(k,hashs)
        if len(edges) > k:
            random.shuffle(edges)
        record["hash"] = [int(x) for x in edges[:k]]
        db.hashs.insert(record)
    nodes = []
    with io.open("/Users/asxzy/datasets/weibo.nodelist") as f:
        for line in f:
            nodes.append(int(line.split()[0]))
    count = 0
    for node in nodes:
        if db.edges.find_one({"to":node}) != None:
            if db.hashs.find_one({"node_id":node}) == None:
                buildhash(node)
            count += 1
            if count % 1000 == 0:
                print count,len(nodes)



def minhash(query_node,topk = False):
    #conn = pymongo.Connection()
    conn = pymongo.MongoClient("/tmp/mongodb-27017.sock")
    db = conn.sina
    CACHE = db.cache
    #CACHE.drop()
    #db.hashs.drop()
    def buildhash(nid,k=400):
        hashs = []
        cur = db.edges.find({"to":nid})
        edges = []
        for edge in cur:
            edges.append(edge["from"])
        #for edge in cur:
         #   hashs.append(hashlib.md5(str(edge["from"])).hexdigest()[8:-8])
        record = {}
        record["node_id"] = nid
        #record["hash"] = heapq.nsmallest(k,hashs)
        if len(edges) > k:
            random.shuffle(edges)
        record["hash"] = [int(x) for x in edges[:k]]
        db.hashs.insert(record)

    query_node = int(query_node)
    res = CACHE.find_one({"node_id":query_node})
    if res != None:
        if topk != False and type(topk) == int:
            return res["cache"][:topk]
        else:
            return res["cache"]
    EDGES = db.edges
    NODES = db.nodes
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
            try:
                node["description"] = n["description"]
            except:
                node["description"] = ""
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
            try:
                node["description"] = n["description"]
            except:
                node["description"] = ""
            nodes.append(node)
    print "there are ",len(nodes),"nodes"
    res_ms = []
    try:
        m1 = HASHS.find_one({"node_id":query_node},{"hash":1})["hash"]
    except:
        buildhash(query_node)
        m1 = HASHS.find_one({"node_id":query_node},{"hash":1})["hash"]
    print len(m1),EDGES.find({"to":query_node}).count()
    count = 0
    for node in nodes:
        count += 1
        try:
            m2 = HASHS.find_one({"node_id":node["node_id"]},{"hash":1})["hash"]
        except:
            buildhash(node["node_id"])
            print "buildhash"
            m2 = HASHS.find_one({"node_id":node["node_id"]},{"hash":1})["hash"]
        print len(m2),count,len(nodes)
        '''jaccard similarity'''
        JS = {}.fromkeys(m1+m2).keys()
        n1 = len(m1)+len(m2)-len(JS)
        try:
            ms = n1 / float(len(m1) + len(m2) - n1)
        except ZeroDivisionError:
            ms = 0
        if ms > 0 or topk != False:
            res_ms.append((node["node_id"],node["screen_name"],node["description"],ms))
    res_ms.sort(key=lambda x : -x[3])
    if topk != False and type(topk) == int:
        return res_ms[:topk]
    else:
        record = {}
        record["node_id"] = query_node
        record["cache"] = res_ms
        CACHE.insert(record)
        return res_ms


if __name__ == "__main__":
    #ms = minhash(sys.argv[1])
    #hash()
    conn = pymongo.MongoClient("/tmp/mongodb-27017.sock")
    db = conn.sina
    nodes = []
    #with io.open("/Users/asxzy/datasets/weibo.nodelist") as f:
    with io.open(sys.argv[1]) as f:
        for line in f:
            nodes.append(int(line.split()[0]))
    count = 0
    for node in nodes:
        count += 1
        minhash(node)
        if count % 1000 == 0:
            print count,len(nodes)

