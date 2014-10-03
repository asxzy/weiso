from django.conf.urls import patterns, include, url
from django.contrib import admin

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^about$', 'se.views.about'),
    url(r'^search$', 'sina.views.search'),
    url(r'^view_node-(?P<node_id>\d+)$', 'sina.views.view_node'),
    url(r'^SpammedIndexTable$', 'se.views.SpammedIndexTable'),
    url(r'$', 'se.views.index'),
)
