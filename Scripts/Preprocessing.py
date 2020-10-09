# -*- coding: utf-8 -*-
"""

@author: nikhi
"""


from Grid import *
from RoadUtils import *
import networkx as nx


path_to_Graph = '../Cache/Graph.pkl'
G=None

def model_data(filepath):
    data={}
    file = filepath
    with open(file,'r') as csvFile:
        reader = csv.reader(csvFile)
        col = next(reader)
        print("Modeling data...")
        for row in reader:
            key = row[0]+'::'+row[1]
            if data.get(key)==None:
                data[key]={}
                #data[key]['route']=row[2]
                data[key]['feed'] = []
            route = row[2]
            data[key]['route']=route
            ts = row[6]
            lat = row[3]
            long = row[4]
            if len(data[key]['feed'])>0:
                if ts!=data[key]['feed'][-1][2]:
                    dp = [lat,long,ts]
                    data[key]['feed'].append(dp)
            else:
                dp = [lat,long,ts]
                data[key]['feed'].append(dp)
        print("Data modeled in dictionary form!!")
        return data
def load_bus_dict(df,grid,lenvec,edgelist):
    print('Preprocessing Bus info..')
    bus_dict={}
    i=0
    lenvec = len(df.keys())
    for key in df.keys():
        if i%10==0:
            print(i,"/",lenvec)
        i+=1
        for feed in df[key]['feed']:
            point  = Point(float(feed[0]),float(feed[1]))
            node,edge = grid.map_to_node(point)
            if bus_dict.get(key)==None:
                bus_dict[key]={}
                bus_dict[key]['feed']=[]
                bus_dict[key]['route']=df[key]['route']
            if node!='None':
                dp = feed+[node,edge]
                bus_dict[key]['feed'].append(dp)   
    return bus_dict

def getNeighbours(rid,neighbours):
    if neighbours[rid]==None:
        return None
    nei = []
    for n in neighbours[rid].keys():
        nei.append(n)
    return nei
def check_if_road_exist(rid,data):
    if data.get(rid)==None:
        return False
    return True
def get_neighbours_with_Data(data,rid):
    neighbours=[]
    if one_hop_neighbours.get(rid)==None:
        return []
    nei = one_hop_neighbours[rid]
    
    for n in nei:
        if n in list(data.keys()):
            neighbours.append(n)
    return neighbours
def getBusVector(rid,data):
    arr =[]
    for i in range(len(data[rid])):
        arr.append(data[rid][i])
    return arr
def convertDatatoNumpy(bv):
    bvv={}
    for key in bv.keys():
        bvv[key] = np.array(getBusVector(key,bv))
    return bvv
def get_one_hop_neighbours(rid,neighbours):
    nei = getNeighbours(rid,neighbours)
    on=set()
    for n in nei:
        on.add(n)    
        nn = getNeighbours(n,neighbours)
        for n1 in nn:
            if n1!=rid:
                on.add(n1)
    return list(on)
def getOneHopNei(neighbour_nodes):
    one_hop_neighbours={}
    for key in neighbour_nodes.keys():
        one_hop_neighbours[key] = get_one_hop_neighbours(key,neighbour_nodes)
    return neighbour_nodes
    
def getNewFeed(path,iPoint,dpoint,speed,iTime,lTime,distV):
    newFeed = []
    #print(len(path),'    ',len(distV))
    for i in range(1,len(path)-1):
        n1=path[i]
        t=math.floor(distV[i-1]/speed)
        nf=[n1[1],n1[0],iTime+t,n1,getEdge(path[i],path[i-1])] + [distV[i-1],speed]
        newFeed.append(nf) 
        iTime+=t
    return newFeed
    
def recomputeFeed(feed,grid,Edgedistance):
    i=1
    pa=set()
    newfeed=[]
    if len(feed)<1:
        return []
    newfeed.append(feed[0]+[0.0,0.0])
    while i < len(feed):
        prevNode = feed[i-1][-2]
        currentNode = feed[i][-2]
        if nx.has_path(G,prevNode,currentNode)==False:
            G.add_edge(prevNode,currentNode)
        else:
            prevPoint = Point(float(feed[i-1][0]),float(feed[i-1][1]))
            currPoint = Point(float(feed[i][0]),float(feed[i][1]))
            distance = grid.getDistance(prevPoint,currPoint)
            tdiff=int(feed[i][2]) - int(feed[i-1][2])
            sp = distance/tdiff
            p = nx.shortest_path(G,prevNode,currentNode)
            if len(p)<=2:
                nf=feed[i]+[distance,sp]
                newfeed.append(nf)
            else:
                tdistance,distV = getTotalDistance(p,Edgedistance,prevPoint,currPoint,grid)
                speed = tdistance/tdiff
                if tdistance>2*distance and speed>70:
                    nf=feed[i]+[distance,sp]
                    newfeed.append(nf)
                else:
                    newFeed = getNewFeed(p,prevPoint,currPoint,speed,int(feed[i-1][2]),int(feed[i][2]),distV)
                    newfeed+=newFeed
                    nf = feed[i]+[Edgedistance[feed[i][-1]],speed]
                    newfeed.append(nf)
            i+=1        
    return newfeed
def completejourneys(busdict,grid,EdgeDistance):
    busdictNew = {}
    for key in busdict.keys():
        busdictNew[key]={}
        busdictNew[key]['route'] = busdict[key]['route']
        busdictNew[key]['feed']= recomputeFeed(busdict[key]['feed'],grid,EdgeDistance)
        print(key)
        
    return busdictNew
def load_Graph(path_to_graph):
	return loadfile(path_to_graph)
def getneighbournodes(nl):
    neighbour_nodes={}
    for key in nl.keys():
        nei = nl[key][1]
        for n in range(len(nei)):
            for i in range(n,len(nei)):
                if nei[n]!=nei[i]:
                    if neighbour_nodes.get(nei[n])==None:
                        neighbour_nodes[nei[n]]={}
                    if neighbour_nodes.get(nei[i])==None:
                        neighbour_nodes[nei[i]]={}
                    if neighbour_nodes[nei[i]].get(nei[n])==None:
                        neighbour_nodes[nei[i]][nei[n]]=-1
                    if neighbour_nodes[nei[n]].get(nei[i])==None:
                        neighbour_nodes[nei[n]][nei[i]]=-1
    return neighbour_nodes
def mergeData(li,nei,data,start,p):
    for n in nei:
        li.append(data[n][start:start+p])
    return li
def Lookup(data,start,p,road_id,n):
    data_matrix = []
    d = data[road_id][start:start+p]
    target = data[road_id][start+p]
    data_matrix.append(d)
    nei = get_neighbours_with_Data(data,road_id)
    if len(nei)>=n:
        nei=nei[:n-1]
        data_matrix = mergeData(data_matrix,nei,data,start,p)
    elif len(nei)<n-1:
        data_matrix = mergeData(data_matrix,nei,data,start,p)
        rem = n-1-len(nei)
        for i in range(rem):
            zeroes = [ 0 for i in range(start,start+p,1)]
            zeroes = np.array(zeroes)
            data_matrix.append(zeroes)
    else:
        data_matrix = mergeData(data_matrix,nei,data,start,p)
    return np.array(data_matrix),target
def preprocess(filepath,newGrid,EdgeDistance): #file path to csv, Grid object, EdgeDistance in meters for every edge in graph
	global G
	data  = model_data(filepath)
	G = load_Graph(path_to_graph)
	busdict = load_bus_dict1(data,newGrid,0,None)
	bdnew = completejourneys(busdict,newGrid,EdgeDistance)
	print("Processed")
	return bdnew

