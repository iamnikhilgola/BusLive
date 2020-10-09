import csv
import networkx as nx

from shapely.geometry import shape
import fiona 
import itertools
from shapely.ops import unary_union

path_to_nodes = '../../Roads/Graph/Vertices.csv'
path_to_edges = '../../Roads/Graph/Edges.csv'
path_to_shape_file=''
def loadNodes():
	nodes={}
	with open(path_to_nodes) as csvfile:
	    readCSV = csv.reader(csvfile, delimiter=',')
	    for row in readCSV:
		_id = int(row[0])
		lat = float(row[1])
		longi = float(row[2])
		nodes[_id] = (longi,lat)
	return nodes
def loadEdges(nodes):
	edges={}
	with open(path_to_edges) as csvfile:
	    readCSV = csv.reader(csvfile, delimiter=',')
	    for row in readCSV:
		_id = int(row[0])
		fnode = int(row[1])
		tnode = int(row[2])
		length = float(row[3])
		edges[_id] = [(nodes[fnode],nodes[tnode]),length]
	return edges
def createGraphFromCSV():
	nodes = loadNodes()
	edges = loadEdges(nodes)
	G = nx.Graph()
	for k in edges.keys():
		ele = edges[k]
		e = ele[0]
		G.add_egde(e[0],e[1])
	return G,nodes,edges

def createShapeFileGraph():
	print('loading shapefiles...')
	geoms =[shape(feature['geometry']) for feature in fiona.open(path_to_shape_file)]
	print('performing unions on close points..')
	res = unary_union(geoms)
	print('Generating graph...')
	G = nx.Graph()
	for line in res:
		for seg_start, seg_end in zip(list(line.coords),list(line.coords)[1:]):
			G.add_edge(seg_start, seg_end) 
	print('Successfully generated graph')
	return G