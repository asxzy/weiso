#!/usr/bin/env python
import os, re, sys, lucene
import io
import pymongo
from subprocess import *
from time import *

from java.io import File
from org.apache.lucene.analysis.miscellaneous import LimitTokenCountAnalyzer
from org.apache.lucene.analysis.cn.smart import SmartChineseAnalyzer
from org.apache.lucene.index import IndexWriter, IndexWriterConfig
from org.apache.lucene.document import Document, Field, StringField, TextField
from org.apache.lucene.store import SimpleFSDirectory
from org.apache.lucene.util import Version


print "connected to pymongo"
conn = pymongo.Connection()
db = conn.sina

# init lucene
INDEX_DIR = 'index'
lucene.initVM(vmargs=['-Djava.awt.headless=true'])
print "init lucene"
directory = SimpleFSDirectory(File(INDEX_DIR))
analyzer = SmartChineseAnalyzer(Version.LUCENE_CURRENT)
analyzer = LimitTokenCountAnalyzer(analyzer, 10000)
config = IndexWriterConfig(Version.LUCENE_CURRENT, analyzer)
writer = IndexWriter(directory, config)


print 'doing index'
count = 0
for node in db.nodes.find({},{"node_id","screen_name","description"}):
    count += 1
    if count % 100000 == 0:
        writer.commit()
        print count
    doc = Document()
    string = str(node["node_id"]) + ' '
    try:
        string += node["screen_name"] + ' '
    except KeyError:
        string += ''
    try:
        string += node["description"] + ' '
    except KeyError:
        string += ''
    doc.add(Field("text", string , TextField.TYPE_NOT_STORED))
    doc.add(Field("id", str(node["node_id"]), StringField.TYPE_STORED))
    writer.addDocument(doc)
writer.commit()

writer.close()
