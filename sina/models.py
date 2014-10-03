from django.db import models
from django.contrib import admin
#from jaccard import *
from minhash import *


class Node(models.Model):
    #nid = models.AutoField(primary_key = True)
    node_id = models.BigIntegerField()
    screen_name = models.CharField(max_length = 30)
    description = models.CharField(max_length = 255)
    #rank_value = models.FloatField(default = 0)
    in_degree = models.IntegerField()
    out_degree = models.IntegerField()

    def getjs(self):
        return jaccard(self.nid)[:10]

    def getjss(self):
        return jaccard(self.nid)

    def getms(self):
        print self
        return minhash(self.node_id,topk = 10)

    def getmss(self):
        return minhash(self.node_id)

    def __unicode__(self):
        return '%s(%d)' % (self.screen_name, self.node_id)


