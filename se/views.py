from se.view_utils import *
from sina.models import *


@render_as_template('index.html')
def index(request):
	return {}


@render_as_template('SpammedIndexTable.html')
def SpammedIndexTable(request):
	return {}

@render_as_template('about.html')
def about(request):
	return {}


@render_as_template('search.html')
def search(request):
	return {
		'node_count' : 1185072,#Node.objects.count(),
		'edge_count' : 38055283,#Edge.objects.count(),
	}


@render_as_template('node_data.html')
def view_node(request):
	return {
		'nodes' : Node.objects.all()[:50]
	}


@render_as_template('edge_data.html')
def view_edge(request):
	return {
		'edges' : Edge.objects.all()[:50]
	}
