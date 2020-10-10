import pickle
from RoadUtils import loadfile
import networkx as nx
path_to_RGRAPH = '../Cache/RGRAPHS.pkl'

def loadRouteGraph(path):
    fileP = loadfile(path)
    return fileP
def getGraphForRoute(route,routefile):
    return routefile[route]
def getNodesForRoute(route,routefile):
    g = getGraphForRoute(route,routefile)
    return list(g.nodes())
def getEdgesForRoute(route,routefile):
    g = getGraphForRoute(route,routefile)
    return list(g.edges())
def getRouteGraph():
    return loadRouteGraph(path_to_RGRAPH)    