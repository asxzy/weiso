from se.view_utils import *
from django.shortcuts import get_object_or_404
from sina.models import *
from django.conf import settings
from django.http import Http404
from similarity import *

import sys, os
sys.path.append("/usr/local/lib/python2.7/site-packages")
import lucene, math
import time

from java.io import File
from org.apache.lucene.analysis.cn.smart import SmartChineseAnalyzer
from org.apache.lucene.index import DirectoryReader
from org.apache.lucene.queryparser.classic import QueryParser
from org.apache.lucene.search import IndexSearcher
from org.apache.lucene.store import SimpleFSDirectory
from org.apache.lucene.util import Version

from pymongo import MongoClient



VM_ENV = lucene.initVM(vmargs=['-Djava.awt.headless=true'])

@render_as_template('index.html')
def index(request):
    return {}


@render_as_template('SpammedIndexTable.html')
def index(request):
    return {}

@render_as_template('search.html')
def search(request):
    query = request.GET.get('q', None)
    page = int(request.GET.get('page', 1))
    perPage = 5
    nodes = []
    usage = {}
    usage["time"] = time.time()

    if not query:
        count = 0
        nodes = []
        keywords = []
    else:
        #conn = ReplicaSetConnection('localhost', replicaSet='jlu')
        conn = MongoClient('localhost')
        db = conn.sina
        #db.read_preference = ReadPreference.SECONDARY
        CACHE = db.cache
        keywords = query.split(' ')
        cache = CACHE.find_one({"query":keywords,"page":page})
        if cache == None:
            print "query cache not found"
            VM_ENV.attachCurrentThread()
            fsDir = SimpleFSDirectory(File(settings.ROOT_DIR+'/index'))
            searcher = IndexSearcher(DirectoryReader.open(fsDir))

            analyzer = SmartChineseAnalyzer(Version.LUCENE_CURRENT)
            parser = QueryParser(Version.LUCENE_CURRENT, 'text', analyzer)
            parser.setDefaultOperator(QueryParser.Operator.AND)
            lucene_query = parser.parse(query)

            scoreDocs = searcher.search(lucene_query, 3000000).scoreDocs


            ids = []

            for scoreDoc in scoreDocs:
                doc = searcher.doc(scoreDoc.doc)
                for field in doc.getFields():
                    ids.append(field.stringValue())
            print "got ids from lucene",len(ids)

            ids = [int(x) for x in ids]
            NODES = conn.sina.nodes
            count = 0
            for n in NODES.find({"node_id":{"$in":ids}}).sort("in_degree",-1).skip((page-1)*perPage):
                count += 1
                print "doing",n["node_id"],count,"/",perPage
                n["js"] = similarity(n["node_id"],topk=10)
                nodes.append(n)
                if len(nodes) == perPage:
                    break
            count = len(ids)
            CACHE.insert({"query":keywords,"page":page,"cache":nodes,"count":len(ids)})
            usage["isCache"] = False
        else:
            print "found query cache"
            usage["isCache"] = True
            nodes = cache["cache"]
            count = cache["count"]
        pagenav = {}
        if page == 1:
            pagenav["has_pre"] = None
        else:
            pagenav["has_pre"] = page - 1
        if page > count/perPage:
            pagenav["has_next"] = None
        else:
            pagenav["has_next"] = page + 1
        pagenav["page"] = page
        usage["time"] = time.time() - usage["time"]

    return {
        'q' : request.GET.get('q', ''),
        'keywords' : keywords,
        'nodes' : nodes,
        'count' : count,
        'page' : pagenav,
        'usage' : usage,
    }


@render_as_template('node.html')
def view_node(request, node_id):
    node_id = int(node_id)
    usage = {}
    usage["time"] = time.time()
    #conn = ReplicaSetConnection('localhost', replicaSet='jlu')
    conn = MongoClient('localhost')
    db = conn.sina
    #db.read_preference = ReadPreference.SECONDARY
    CACHE = db.cache
    NODES = db.nodes
    EDGES = db.edges
    nodes = NODES.find_one({"node_id":node_id})
    if nodes == None:
        nodes = EDGES.find_one({"to":node_id})
        if nodes == None:
            raise Http404
        else:
            nodes["node_id"] = node_id
            nodes["screen_name"] = "User_"+str(nodes["node_id"])
            nodes["description"] = ""
    res = CACHE.find_one({"node_id":node_id})
    if res != None:
        nodes["js"] = res["cache"]
        usage["isCache"] = True
    else:
        nodes["js"] = similarity(nodes["node_id"])
    usage["time"] = time.time() - usage["time"]
    return {
        'n' : nodes,
        'usage': usage,
    }
