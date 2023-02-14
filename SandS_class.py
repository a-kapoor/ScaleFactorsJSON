import correctionlib.schemav2 as schema
from correctionlib.schemav2 import CorrectionSet,Correction,Category,CategoryItem
from JSONTools import *
import pandas as pd
import numpy as np
class SandS:
    def __init__(self,runbins,fulldict):
        
        self.runbins=runbins
        self.df=fulldict
        self.etabins=[float('-inf'),-2.0,-1.566,-1.442, -1.2,-1, 0, 1,1.2, 1.442, 1.566,2.0,float('inf')]
        self.etabinsstr=['EE3','EE2','EE1','EB3','EB2','EB1','EB1','EB2','EB3','EE1','EE2','EE3']
        self.etas={'EE3':[2.0,2.5],'EE2':[1.566,2.0],
                   'EE1':[1.566,2.0],#'EE1':[1.442,1.566],EE1 needs to be defined properly. currently substituted
                   'EB3':[1.2,1.442],
                   'EB2':[1.0,1.2],
                   'EB1':[0.0,1.0]}
        self.etbins=[0.0,14000.0]
        
    def  getout(self,bins):
        binsy=[]
        for i in range(len(bins)):
            if i<len(bins)-1:
                binsy.append([bins[i],bins[i+1]])
        return binsy   
    
    def getmultibin(self,name,edges,content):
        return schema.MultiBinning.parse_obj({"inputs":[name],"nodetype": "multibinning","edges": [edges],
                                              "flow": 'error',
                                              "content":content
                                             })
    
    def getSS(self,runs,etas,r9bin,etbin,gain,valtype):
        try:
            if etas[0]==1.442:
                return 0
            return self.df[runs[0]][runs[1]][etas[0]][etas[1]][r9bin[0]][r9bin[1]][etbin[0]][etbin[1]][valtype][gain]
        except:
            return 0
        
    def getr9SS(self,runs,etas):
        r9bins=[]
        fullr9=[]
        heredf=self.df[runs[0]][runs[1]][etas[0]][etas[1]]
        r9binsa=list(heredf.keys())
        fullr9=[i for i in r9binsa]
        fullr9.append(list(heredf[r9binsa[-1]].keys())[0])
        for r9bina in r9binsa:
            r9bins.append([r9bina,list(heredf[r9bina].keys())[0]])
        return [fullr9,r9bins]
    
    def getrunSSnew(self,runbinsall,gain,valtype):
        edges=[runbin[0] for runbin in runbinsall]
        if runbinsall[-1][1]!=edges[-1]:
            edges.append(runbinsall[-1][1])
        else:
            edges.append(edges[-1]+0.1)
        
        return self.getmultibin("run",edges,[
            self.getmultibin("eta",self.etabins,[
                self.getmultibin("r9",self.getr9SS(runs,self.etas[strbin])[0],[
                    self.getmultibin("et",self.etbins,[
                        self.getSS(runs,self.etas[strbin],r9bin,etbin,gain,valtype)
                        for etbin in self.getout(self.etbins)]) 
                    for r9bin in self.getr9SS(runs,self.etas[strbin])[1]])
                for strbin in self.etabinsstr])
            for runs in runbinsall])