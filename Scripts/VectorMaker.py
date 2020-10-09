from datetime import datetime
from dateutil import tz
from RoadUtils import loadfile
from RoadDFS import loadEdgeList

el = None

def getTimeSlot(ts,minpslot):
        
    mtim = datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    tim = datetime.utcfromtimestamp(ts).strptime(mtim,'%Y-%m-%d %H:%M:%S')
    
    #print(tim)
    from_zone = tz.tzutc()
    to_zone = tz.tzlocal()
    
    tim =tim.replace(tzinfo=from_zone)
    tim = tim.astimezone(to_zone)
    tim=tim.strftime('%Y-%m-%d %H:%M:%S')
    tim = tim.split(" ")[1]
    s= tim.split(':')
    hr = int(s[0])
    mn = int(s[1])
    sec = int(s[2])
    divs = math.floor(mn/minpslot)
    timslot = hr*(60/minpslot)+divs
    return int(timslot)
def VectorizeBD(bd,minslot,el):
    bv  = {}
    l=len(bd.keys())
    c=0
    for key in bd.keys():
        if c%1000==0:
            print(c,"/",l)
        c+=1
        for feed in bd[key]['feed']:
            ts = getTimeSlot(int(feed[2]),minslot)
            rid = el[feed[4]][0]
            sp = feed[-1]
            sp=(18/5)*sp
            if sp>1:
                if bv.get(rid)==None:
                    bv[rid]={}

                if bv[rid].get(ts)==None:
                    bv[rid][ts]={}
                    bv[rid][ts]['sum']=0.0
                    bv[rid][ts]['count']=0
                bv[rid][ts]['sum']+=sp
                bv[rid][ts]['count']+=1
    
    return bv
def getSpeed(bv,rid,ts):
    su = bv[rid][ts]['sum']
    co = bv[rid][ts]['count']
    return su/co
def CreateVector(bus_dict,minslot):
    global el 
    el = loadfile(loadEdgeList())
    return VectorizeBD(bus_dict,minslot,el)