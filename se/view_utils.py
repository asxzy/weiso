#coding=utf-8
from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response, redirect
import json

def render_as_template(template):
    '''
    将结果渲染至模板
    '''
    def _deco(func):
        def __deco(*args, **kwargs):
            request = args[0]
            ret = func(*args, **kwargs)
            if ret == None:
                ret = {}
            return render_to_response(template, ret,
            context_instance = RequestContext(request))
        return __deco
    return _deco


def render_as_json(func):
    '''
    将结果渲染至JSON字符串
    '''
    def _deco(*args, **kwargs):
        request = args[0]
        ret = func(*args, **kwargs)
        if ret == None:
            ret = {}
        return HttpResponse(json.dumps(ret))
    return _deco
