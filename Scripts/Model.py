#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May  3 12:59:07 2020

@author: nikhil
"""

import matplotlib.pyplot as plt
import torch
import numpy as np
import pickle
import math
import torch.nn.functional as F
import torch.nn as nn
import torch.optim as optim
from torch.nn import Conv2d, LSTM, Linear
from torch.autograd import Variable
import time
import random
from sklearn.model_selection import train_test_split
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")



def load_pickle(filename):
    data=None
    with open(filename,'rb') as dbfile:
        data=pickle.load(dbfile)
    return data
#-------------------------------------------------------------------------------------   
# MODEL SPATIO-Temporal
#-------------------------------------------------------------------------------------
class ST_MODEL(nn.Module):
    def __init__(self,neigh_size,rnn_param,filter_size=1):
        super(ST_MODEL,self).__init__()
        self.k_size=neigh_size
        self.filter_size = filter_size
        self.num_layers = rnn_param['num_layers']
        self.hidden_size= rnn_param['hidden_size']
        
        self.conv1Layer=nn.Sequential(
            nn.Conv2d(in_channels=1,out_channels=1,kernel_size=(self.filter_size,self.k_size)),
            nn.ReLU()
            
        )
        self.conv2Layer=nn.Sequential(
            nn.Conv2d(in_channels=4,out_channels=1,kernel_size=(1,1)),
            nn.ReLU(),
            nn.AvgPool2d(kernel_size=(1,2),stride=1)
        )
        
        
        self.lstm = LSTM(input_size=rnn_param['input_size'],hidden_size=rnn_param['hidden_size'],num_layers=rnn_param['num_layers'],batch_first=True)
       
        self.linearFC1=nn.Sequential(
     
            nn.Linear(rnn_param['hidden_size'],10),
            
            nn.Linear(10,1)
        )
        
        
    def forward(self,t):
        t = self.conv1Layer(t)
        t=t.view(t.size(0),-1,1)
        h_0 = Variable(torch.zeros(
            self.num_layers, t.size(0), self.hidden_size))
        c_0 = Variable(torch.zeros(
            self.num_layers, t.size(0), self.hidden_size))
        t, (h_out, _) = self.lstm(t, (h_0, c_0))
        h_out = h_out.view(-1, self.hidden_size)
        t=self.linearFC1(h_out)
        return t
#-----------------------------------------------------------------------------------------
#Spatio-Temporal-Historical Model
#-----------------------------------------------------------------------------------------
class STH_MODEL(nn.Module):
    def __init__(self,neigh_size,rnn_param,filter_size=1):
        super(STH_MODEL,self).__init__()
        self.k_size=neigh_size
        self.filter_size = filter_size
        self.num_layers = rnn_param['num_layers']
        self.hidden_size= rnn_param['hidden_size']
        
        self.conv1Layer=nn.Sequential(
            nn.Conv2d(in_channels=1,out_channels=1,kernel_size=(self.filter_size,self.k_size)),
            nn.ReLU()
            
        )
        self.conv2Layer=nn.Sequential(
            nn.Conv2d(in_channels=4,out_channels=1,kernel_size=(1,1)),
            nn.ReLU(),
            nn.AvgPool2d(kernel_size=(1,2),stride=1)
        )
        
        
        self.lstm = LSTM(input_size=rnn_param['input_size'],hidden_size=rnn_param['hidden_size'],num_layers=rnn_param['num_layers'],batch_first=True)
       
        self.linearFC1=nn.Sequential(
     
            nn.Linear(rnn_param['hidden_size'],10),
            
            nn.Linear(10,1)
        )
        
        
        self.historyFC=nn.Sequential(
            nn.Linear(5,10),
            nn.Linear(10,1)
        )
        
        self.operateFC=nn.Sequential(
            nn.Linear(2,2),
            nn.Linear(2,1)
        )
        
    def forward(self,t,h):
        t = self.conv1Layer(t)
        t=t.view(t.size(0),-1,1)
        h_0 = Variable(torch.zeros(
            self.num_layers, t.size(0), self.hidden_size))
        c_0 = Variable(torch.zeros(
            self.num_layers, t.size(0), self.hidden_size))
        t, (h_out, _) = self.lstm(t, (h_0, c_0))
        h_out = h_out.view(-1, self.hidden_size)
        t=self.linearFC1(h_out)
        his = self.historyFC(h)
        t = torch.cat((t,his),dim=1)
        t = self.operateFC(t)
        return t
def getEstimatedtime(timeperEpoch,epochleft):
    totaltime=timeperEpoch*epochleft
    return getTimeString(totaltime)
def getTimeString(totaltime):
    hr,mn,sec=0.0,0.0,0.0
    hr = round(totaltime/3600)
    tot = totaltime%3600
    mn = round(tot/60)
    tt=tot%60
    sec = round(tt)
    timeStr = ''
    if hr>0:
        timeStr += str(hr)+'hr '
    if mn>0:
        timeStr += str(mn)+'min '
    timeStr += str(sec)+'secs'
    return timeStr
def getRNNParam(input_size,hidden_size,out_size,num_layers):
    di={}
    di['input_size']=input_size
    di['hidden_size']=hidden_size
    di['out_size']=out_size
    di['num_layers']=num_layers
    return di
def load_model_ST(path,param,N,h):
    model = ST_MODEL(N,param,h)
    model.load_state_dict(torch.load(path))
    model.eval()
    return model
def load_model_STH(path,param,N,h):
    model = STH_MODEL(N,param,h)
    model.load_state_dict(torch.load(path))
    model.eval()
    return model  
def get_training_MODEL(lr,N,h,param,his=False):
    learning_rate = lr
    neighbour_size=N
    temp_rel=h
    MyModel=None
    if his==False:
        MyModel = ST_MODEL(neighbour_size,param,temp_rel)
    else:
        MyModel = STH_MODEL(neighbour_size,param,temp_rel)
    criterion = torch.nn.MSELoss()    # mean-squared error for regression
    optimizer = torch.optim.Adam(MyModel.parameters(), lr=learning_rate)          
    return MyModel,criterion,optimizer
def get_DEFAULT_param():
    param = getRNNParam(1,8,1,1) 
    return param
