#!/usr/bin/env python
import MySQLdb
import sys
import hashlib
import heapq
import numpy


def getsalt(k = 100):
    conn = MySQLdb.connect(host="137.207.234.149", port=3306,user='asxzy',passwd="asxzy",db="weibo", charset='utf8')
    cur = conn.cursor()
    cur.execute("SELECT `sid`,`salt` from `salt` ORDER BY `sid` LIMIT "+str(k))
    val = []
    for salt in cur.fetchall():
        val.append(salt)
    conn.close()
    return val

def minhash(array,salt):
    hashs = []
    for s in salt:
        m = None
        for a in array:
            tmp = int(hashlib.md5(str(a)+str(s[1])).hexdigest()[8:-8],16)
            if m == None or tmp < m:
                m = tmp
        hashs.append(m)
    return hashs

def jaccard(query_node):
    conn = MySQLdb.connect(host="137.207.234.149", port=3306,user='asxzy',passwd="asxzy",db="weibo", charset='utf8')
    cur = conn.cursor()
    salt = getsalt()
    cur.execute("SELECT DISTINCT l.`nid`,n.`screen_name`,n.`node_id` from `lsh` l JOIN `node` n ON l.`nid` = n.`nid` WHERE l.`lsh` IN (SELECT `lsh` from `lsh` l WHERE l.`nid` = '"+str(query_node)+"') AND l.`nid` != '"+str(query_node)+"'")
    nodes = [(x[0],x[1],x[2]) for x in cur.fetchall()]

    cur.execute("SELECT `from` from `edge` WHERE `to` = '"+str(query_node)+"'")
    s1 = [x[0] for x in cur.fetchall()]
    res_js = []
    for node in nodes:
        #sql = "SELECT `from` from `edge` WHERE `to` = '"+str(node)+"'"
        sql = "SELECT `from` from `edge` WHERE `to` = '"+str(node[0])+"'"
        cur.execute(sql)
        s2 = [x[0] for x in cur.fetchall()]

        '''jaccard similarity'''
        JS = {}.fromkeys(s1+s2).keys()
        n1 = len(s1)+len(s2)-len(JS)
        try:
            js = n1 / float(len(s1) + len(s2) - n1)
        except ZeroDivisionError:
            js = 0
        #res_js.append((str(node[1]).encode("utf8","ignore"),js))
        if node[1] == None:
            res_js.append((node[0],'User_'+str(node[2]),node[2],js))
        else:
            res_js.append((node[0],node[1],node[2],js))
    cur.close()
    res_js.sort(key=lambda x : -x[3])
    conn.close()
    return res_js


if __name__ == "__main__":
    js = jaccard(sys.argv[1])
