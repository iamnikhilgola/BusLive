#Necessary header files
from google.transit import gtfs_realtime_pb2
from google.protobuf.json_format import MessageToDict
from google.protobuf.json_format import MessageToJson
from math import sin, cos, sqrt, atan2, radians
import urllib.request
import requests
import csv
import os
import pandas as pd
from collections import OrderedDict
import datetime
import time

sleepTime = 5	      #Time to wait for next iteration
key='None'        #Enter Key realtime key here
 
roadFile="updatedRoadInfo.csv"
#count=0;
def entityCheck(feed):
    if(feed.entity):
        return True
    return False

def getResponse():
    response = ''
    while response == '':
        try:
            response = requests.get('https://otd.delhi.gov.in/api/realtime/VehiclePositions.pb?key='+key)
            #break
        except:
            print("Connection refused by the server..")
            print("Let me sleep for 5 seconds")
            print("ZZzzzz...")
            time.sleep(5)
            print("Was a nice sleep, now let me continue...")
            continue
    return response

def getFeed():
    try:
        feed = gtfs_realtime_pb2.FeedMessage()
        response=getResponse()       
        feed.ParseFromString(response.content)
        return feed
    except:
        return getFeed()

def getDataFrame(dict_obj):
    collector = []
    counter=0
    #print(dict_obj['entity'])
    for block in dict_obj['entity']:
        counter += 1
        row = OrderedDict()
        row['vehicle_id'] = block['id']
        row['trip_id'] = block['vehicle']['trip'].get('tripId','')
        row['route_id'] = block['vehicle']['trip'].get('routeId','')
        try:
            row['latitude'] = block['vehicle']['position'].get('latitude','')
            row['longitude'] = block['vehicle']['position'].get('longitude','')
            row['speed'] = block['vehicle']['position'].get('speed','')
        except:
           print("Error in Fetching some values") 
        row['timestamp'] = block['vehicle'].get('timestamp','')
        fTime = block['vehicle']['trip'].get('startTime','')
        fDate = block['vehicle']['trip'].get('startDate','')
        #row['road_id']=getRoadID(points,row['latitude'],row['longitude'])
        #row['vehicle_id'] = block['vehicle']['vehicle'].get('id','')
        #row['label'] = block['vehicle']['vehicle'].get('label','')
        collector.append(row)
    df = pd.DataFrame(collector)
    #print(df)
    return df,fTime,fDate

def getDynamicFileName(timestamp):
    date = timestamp[8:10]
    month= timestamp[5:7]
    return date+"_"+month

def getFrame():
    entityFlag=False
    while entityFlag!=True:
        feed=getFeed()
        entityFlag=entityCheck(feed)
        print("Entity Present : ",entityFlag)
        if entityFlag ==False:
            time.sleep(5)
        
    dict_obj = MessageToDict(feed)
    frame,ftime,fdate=getDataFrame(dict_obj)
    #print("frame is ",frame)
    frame['humantime'] = frame.apply( lambda row: datetime.datetime.fromtimestamp(int(row['timestamp'])),axis=1 )
    feedtime = int(dict_obj['header']['timestamp'])
    frame['feed_time'] = datetime.datetime.fromtimestamp(feedtime)
    frame['startTime'] = ftime
    frame['startDate'] = fdate
    dynamicFilename = getDynamicFileName(str(frame['feed_time'][0]))

    return frame,dynamicFilename

def main():
    iteration=0
    prevName=""
    folder = "LiveStream/"
    while(True):
        t1= time.time()
        newFrame,fileName=getFrame()
        if(not os.path.exists(folder+fileName+".csv")):
            if(prevName != fileName):
                iteration=0
                with open(folder+fileName+".csv",'w') as f:
                     newFrame.to_csv(f,index=False)
            else:
                with open(folder+fileName+".csv",'a') as f:
                     newFrame.to_csv(f,index=False,header=False)
        else:
            with open(folder+fileName+".csv",'a') as f:
                newFrame.to_csv(f,index=False,header=False)
        prevName = fileName
        iteration+=1
        t2 = time.time()
        print("Iter : {0}, Shape : {1}, time :{2}".format(iteration,newFrame.shape,t2-t1))
        totalTime= t2-t1
        if(totalTime<10):
            time.sleep(10-totalTime)            
    
if __name__=="__main__":
    main()
