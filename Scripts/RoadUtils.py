# -*- coding: utf-8 -*-
"""
Created on Mon Jan  6 20:47:38 2020

@author: nikhi
"""
import pickle
import math
import numpy as np
from numpy import arccos, array, dot, pi, cross
from numpy.linalg import det, norm


def distance_numpy(A, B, P):
    """ segment line AB, point P, where each one is an array([x, y]) """
    
    if all(A == P) or all(B == P):
        return 0
    conda = arccos(dot((P - A) / norm(P - A), (B - A) / norm(B - A)))
    pi2= pi / 2
    if conda > pi2: 
        return norm(P - A)
    condb = arccos(dot((P - B) / norm(P - B), (A - B) / norm(A - B)))
    if  condb > pi2:
        return norm(P - B)
    return norm(cross(A-B, A-P))/norm(B-A)


def getDistanceFromline(e1,e2,point):
        A=np.array([e1[0],e1[1]])
        B=np.array([e2[0],e2[1]])
        P=np.array([point.x,point.y])
        return distance_numpy(A,B,P)


def distancepoint(a,b,c,point):
        num = abs(a*point.x+ b*point.y + c)
        den = math.sqrt(a**2+b**2)
        return num/den


def savefile(data,filename):
    with open(filename,'wb') as dbfile:
        pickle.dump(data,dbfile)

def loadfile(filename):
    data=None
    with open(filename,'rb') as dbfile:
        data=pickle.load(dbfile)
    return data
