# -*- coding: utf-8 -*-
"""
@author: nikhi
"""

from RoadUtils import *
import math
import csv
from RoadDFS import *

def validateNeighbour(cellid,splitsize,size,offset):
    newCellID = cellid+offset 
    if newCellID<0 or newCellID>=size:
        return False
    elif cellid%splitsize==0 and newCellID%splitsize == splitsize-1:
        return False
    elif (cellid+1)%splitsize==0 and newCellID%splitsize==0:
        return False
    return True
class BoundingBox:
    # This Bounding box is used to hold the four coordinates. 
    def __init__(self,min_x,min_y,max_x,max_y):
        self.min_x=min_x
        self.min_y=min_y
        self.max_x=max_x
        self.max_y=max_y
class LineSegment:
    def __init__(self,point1,point2):
        self.point1 = point1
        self.point2 = point2
    
class Grid:
    def __init__(self,box=None,split_size=0):
        if box != None:
            self.min_lat=box.min_x
            self.min_long=box.min_y
            self.max_lat=box.max_x
            self.max_long=box.max_y
        self.split =split_size
        self.size= self.split**2
        self.Nodes = None
        roads=None
    def latitude_step_size(self):
        return (self.max_lat - self.min_lat)/self.split
    def longitude_step_size(self):
        return (self.max_long - self.min_long)/self.split
    def hashPoint(self,point):
        latstep = self.latitude_step_size()
        longstep = self.longitude_step_size()
        latdiff = point.x-self.min_lat
        longdiff = point.y-self.min_long
        row = math.floor(latdiff/latstep)
        #print(row)
        col = math.floor(longdiff/longstep)
        cell_id = row * self.split + col
        return row,col,cell_id
    def get_cell_cordinates(self,cell_id):
        latStep = self.latitude_step_size()
        longStep= self.longitude_step_size()
        col = cell_id%self.split
        row = (cell_id-col)/self.split
        latitude1 = self.min_lat+ row *latStep
        longitude1= self.min_long + col * longStep
        return latitude1,longitude1
    def get_cell_lines(self,cell_id):
        lat,long = self.get_cell_cordinates(cell_id)
        lgsize = self.longitude_step_size()
        lasize = self.latitude_step_size()
        p1 = Point(lat,long)
        p3 = Point(lat+lasize,long)
        p4 = Point(lat+lasize,long+lgsize)
        p2 = Point(lat,long+lgsize)
        e1 = LineSegment(p1,p2)
        e2 = LineSegment(p1,p3)
        e3 = LineSegment(p2,p4)
        e4 = LineSegment(p3,p4)
        return e1,e2,e3,e4
    def plot_cell(self,cell_id):
        latstep = self.latitude_step_size()
        longstep= self.longitude_step_size()
        lat,long = self.get_cell_cordinates(cell_id)
        x=[]
        y=[]
        x.append(lat)
        y.append(long)
        x.append(lat+latstep)
        y.append(long)
        x.append(lat+latstep)
        y.append(long+longstep)
        x.append(lat)
        y.append(long+longstep)
        x.append(lat)
        y.append(long)
        plt.plot(x,y)
    def plot_cell_edges(self,cell_id,edges):
        latstep = self.latitude_step_size()
        longstep= self.longitude_step_size()
        lat,long = self.get_cell_cordinates(cell_id)
        x=[]
        y=[]
        x.append(lat)
        y.append(long)
        x.append(lat+latstep)
        y.append(long)
        x.append(lat+latstep)
        y.append(long+longstep)
        x.append(lat)
        y.append(long+longstep)
        x.append(lat)
        y.append(long)
        plt.plot(x,y)
        for e in edges:
            xx1 = e[0]
            xx2 = e[1]
            xxn1 =[]
            yyn1 =[]
            xxn1.append(xx1[1])
            yyn1.append(xx1[0])
            
            xxn1.append(xx2[1])
            yyn1.append(xx2[0])
            plt.plot(xxn1,yyn1)
    
    def validate_location(self,point):
        lat= point.y
        lon = point.x
        if (lat<self.min_lat or lat>self.max_lat) or (lon<self.min_long or lon>self.max_long):
            return False
        return True
    def defineGrid(self):
        x = self.road.getDistance(Point(self.min_long, self.min_lat),Point(self.min_long+self.longitude_step_size(), self.min_lat))
        y = self.road.getDistance(Point(self.min_long, self.min_lat),Point(self.min_long, self.min_lat+self.longitude_step_size()))
        print("================================================================================")
        print("Cell Dimensions:")
        print(x,"meters","X",y,"meters")
        print("Area of the cell: ",x*y,"meter sq")
        totalArea = x*y*self.size/(1000*1000)
        print("Total Area(in sq Km):",totalArea)
        print("Total Number of cells:",self.size)
        print("================================================================================")
    def plot_path(self,path):
        #This plot the path on OSM.
        x=[]
        y=[]
        for p in path:
            x.append(p[0])
            y.append(p[1])
        fig = plt.figure()
        plt.plot(x,y)
        mplleaflet.show(fig=fig)
    def loadNodes(self,graph):
        #This function loads the road network graph in the main grid.
        #self.road=loadRoad("RoadsNew.pkl")
        roadNodes={}
        for node in list(graph.nodes()):
            point = Point(node[1],node[0])
            _,_,cell_id=self.hashPoint(point)
            if roadNodes.get(cell_id)==None:
                roadNodes[cell_id]=[]
            roadNodes[cell_id].append(node)
        self.Nodes=roadNodes
        self.Edges={}
        for e in list(graph.edges()):
            if self.Edges.get(e[0])==None:
                self.Edges[e[0]]=[]
            if self.Edges.get(e[1])==None:
                self.Edges[e[1]]=[]
            self.Edges[e[0]].append(e)
            self.Edges[e[1]].append(e)
        #self.node_road = load_pickle(ROADNODE_PATH)
        print('loading road annotated graph ... ')
        self.EDGE_LIST,self.NODE_LIST = get_annotated_Graph(graph)
        
        
    def getShortestpath(self,source,target):
        graph = self.road.graph
        path = nx.shortest_path(graph,source,target)
        return path
    def getTotalDistance(self,path):
        totaldistance=0
        for i in range(len(path)-1):
            e1 = (path[i],path[i+1])
            e2 = (path[i+1],path[i])
            if self.road.EdgeDistance.get(e1)==None:
                e1 = e2
            totaldistance+=self.road.EdgeDistance[e1]
        return totaldistance
    def getDistanceNodes(self,node1,node2):
        path = self.getShortestpath(node1,node2)
        #print(len(path))
        return self.getTotalDistance(path)    
    def getShortestpath(self,source,target):
        graph = self.road.graph
        path = nx.shortest_path(graph,source,target)
        return path
    def getNeighbourNodes(self,cell_id):
        #this function returns the neighbour nodes if there is no node in the hashed cell.
        nodes = []
        new_cell_id=0
        offsets = [1,-1,self.split,-1*self.split,-1*self.split+1,-1*self.split-1,self.split+1,self.split-1]
        for offset in offsets:
                new_cell_id = cell_id+offset
                if (new_cell_id<0 or new_cell_id>=self.size) or ((cell_id%self.size!=0 and new_cell_id%self.size==0) or(cell_id%self.size==0 and new_cell_id%self.size!=0)):
                    pass
                elif self.Nodes.get(new_cell_id)!=None:
                    nodes +=self.Nodes[new_cell_id]
        return nodes
    def getNeighbourCell(self,cell_id):
        #this function returns the neighbour nodes if there is no node in the hashed cell.
        nodes = []
        new_cell_id=0
        offsets = [1,-1,self.split,-1*self.split,-1*self.split+1,-1*self.split-1,self.split+1,self.split-1]
        for offset in offsets:
                new_cell_id = cell_id+offset
#                print(new_cell_id)
#                 if (new_cell_id<0 or new_cell_id>=self.size) or ((cell_id%self.split!=self.split-1 and new_cell_id%self.split==0) or(cell_id%self.split==0 and new_cell_id%self.split==self.split-1)):
#                     pass
                if validateNeighbour(cell_id,self.split,self.size,offset):
                    nodes.append(new_cell_id)
        return nodes
    def map_to_node(self,point):
        # Function returns the node where the point is mapped to nearest node.
        _,_,cell_id = self.hashPoint(point)
        #print("*******************************************************************************")
        #print(cell_id)
        if self.Nodes.get(cell_id)==None:
            nodes = self.getNeighbourNodes(cell_id)
        else:
            nodes = self.Nodes[cell_id]+self.getNeighbourNodes(cell_id)
        if len(nodes)<=0:
            return 'None','None'
        mindistance=99999999
        minEdge=None
        minNode=None
        #if nodes==None:
            #print("Yess")
        for node in nodes:
            edges = self.Edges[node]
            for edge in edges:
                e1 = [edge[0][1],edge[0][0]]
                e2 = [edge[1][1],edge[1][0]]
                p = [point.x,point.y]
                dist = getLineDistance(e1,e2,p)
                #print("CellID:",cell_id,"   Node:",node,"  Edge:",edge,"  Distance: ",dist, "  Point:(",point.x,",",point.y,")")
                if dist<mindistance:
                    
                    mindistance = dist
                    minEdge=edge
        
        e1 = Point(minEdge[0][0],minEdge[0][1])
        e2 = Point(minEdge[1][0],minEdge[1][1])

        dis1 = self.getDistance(e1,point)
        dis2 = self.getDistance(e2,point)
        if dis1>dis2:
            minNode=minEdge[1]
        else:
            minNode=minEdge[0]
        if minNode!=None:
        	return minNode,minEdge
        return 'None','None'

    def load_stops(self,path_to_stops):
        path = path_to_stops
        data=[]
        self.stops={}
        with open(path,'rt') as f:
            da = csv.reader(f)
            for row in da:
                data.append(row)
        data=data[1:]
        for row in data:
            #print(row)
            stop_id = row[0]
            detail=row[2]
            latitude = float(row[3])
            longitude= float(row[4])
            point=Point(longitude,latitude)
            stop=Stop(stop_id,detail,point)
            _,_,cell_id=self.hash(point)
            #print("Cell_id:",cell_id)
        
            node=self.map_to_node(point)
            if node==None:
                stop.define_nearest_node(None,None)
            else:
                distance=self.road.getDistance(point,Point(node[0],node[1]))
                stop.define_nearest_node(node,distance)
            self.stops[cell_id]=stop
            
    def map_to_road(self,node,edge,here=False):
        result =None
        result = self.node_road[node]
        idList =self.EDGE_LIST[edge]
        
        ids = idList[0]
        
        if here ==True:
            result = result[0][1]
        else:
            result = ids
        return result
    def getDistance(self,point1,point2):
        radius=6371000 #meters
        dlat = math.radians(point2.x)-math.radians(point1.x)
        dlong = math.radians(point2.y)-math.radians(point1.y)
        a = math.sin(dlat/2) * math.sin(dlat/2) + math.cos(math.radians(point1.x)) * math.cos(math.radians(point2.x)) * math.sin(dlong/2) * math.sin(dlong/2)
        c = 2 * math.atan2(math.sqrt(a),math.sqrt(1-a))
        dist = float(radius * c)
        return dist# distance in meters
class Point: 
    def __init__(self, x, y): 
        self.x = x 
        self.y = y 
  
# Given three colinear points p, q, r, the function checks if  
# point q lies on line segment 'pr'  
def onSegment(p, q, r): 
    if ( (q.x <= max(p.x, r.x)) and (q.x >= min(p.x, r.x)) and 
           (q.y <= max(p.y, r.y)) and (q.y >= min(p.y, r.y))): 
        return True
    return False
  
def orientation(p, q, r): 
    # to find the orientation of an ordered triplet (p,q,r) 
    # function returns the following values: 
    # 0 : Colinear points 
    # 1 : Clockwise points 
    # 2 : Counterclockwise 
      
    # See https://www.geeksforgeeks.org/orientation-3-ordered-points/amp/  
    # for details of below formula.  
      
    val = (float(q.y - p.y) * (r.x - q.x)) - (float(q.x - p.x) * (r.y - q.y)) 
    if (val > 0): 
          
        # Clockwise orientation 
        return 1
    elif (val < 0): 
          
        # Counterclockwise orientation 
        return 2
    else: 
          
        # Colinear orientation 
        return 0
  
# The main function that returns true if  
# the line segment 'p1q1' and 'p2q2' intersect. 
def checkIntersection(line1,line2):
    return doIntersect(line1.point1,line1.point2,line2.point1,line2.point2)
def doIntersect(p1,q1,p2,q2): 
      
    # Find the 4 orientations required for  
    # the general and special cases 
    o1 = orientation(p1, q1, p2) 
    o2 = orientation(p1, q1, q2) 
    o3 = orientation(p2, q2, p1) 
    o4 = orientation(p2, q2, q1) 
  
    # General case 
    if ((o1 != o2) and (o3 != o4)): 
        return True
  
    # Special Cases 
  
    # p1 , q1 and p2 are colinear and p2 lies on segment p1q1 
    if ((o1 == 0) and onSegment(p1, p2, q1)): 
        return True
  
    # p1 , q1 and q2 are colinear and q2 lies on segment p1q1 
    if ((o2 == 0) and onSegment(p1, q2, q1)): 
        return True
  
    # p2 , q2 and p1 are colinear and p1 lies on segment p2q2 
    if ((o3 == 0) and onSegment(p2, p1, q2)): 
        return True
  
    # p2 , q2 and q1 are colinear and q1 lies on segment p2q2 
    if ((o4 == 0) and onSegment(p2, q1, q2)): 
        return True
  
    # If none of the cases 
    return False
def load_bus_dict1(df,grid,lenvec,edgelist):
    print('loading bus info....')
    
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
