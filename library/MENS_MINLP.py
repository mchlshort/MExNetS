#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Mon May 7 13:14:01 2018

MINLP model for Mass Exchanger Network Synthesis (MENS) in Pyomo

Made to be used as a part of the HybridStrategy module

@author: mchlshort
"""

from __future__ import division
from pyomo.environ import *
import pandas as pd
import os
import inspect
import numpy
from pyomo.opt import SolverFactory, ProblemFormat, TerminationCondition
from library.FeasibleSolver import *

__author__ = "Michael Short"
__copyright__ = "Copyright 2020"
__credits__ = ["Michael Short, Lorenz T. Biegler, Isafiade, AJ."]
__license__ = "GPL-3"
__version__ = "0.9"
__maintainer__ =  "Michael Short"
__email__ = "m.short@surrey.ac.uk"
__status__ = "Development"

#=====================
#   DATA READING
#=====================
def read_stream_data(filename):
    """ Reads csv with stream data data
    
        Args:
            filename (str): name of input file
          
        Returns:
            DataFrame

    """
    data = pd.read_csv(filename,index_col=0, header=0, float_precision = 'round_trip')
    return data

class MENS(object):
    def __init__(self, rich_data, lean_data, parameter_data, stream_properties, correction_factors=None, stages = None, superstruct = 'SBS'):
        """MENS mass exchanger network synthesis class.

        This class aims to take in data for the rich streams and lean streams as separate matrices
        and then perform a network synthesis which makes use of an initialization step that fixes
        all possible binary variables and computes the optimal solution as an NLP
        Following this, the MINLP optimization can be performed in a subsequent step.

        Args:
            rich_data (pandas DataFrame): DataFrame of rich stream name, concentration in, concentration out and flowrates.
            lean_data (pandas DataFrame): DataFrame of lean stream name, concentration in, concentration out and flowrates.
            correction_factors (dictionary): Dictionary of all correction factors
            parameter_data (pandas DataFrame): DataFrame of problem-specific parameters.
            stages (optional, int): Number of stages for the SWS
            superstructure (optional, str): Either SBS or SWS as of now
            
        """
        self._rich_data = rich_data
        self._lean_data = lean_data
        self._correction_factors = None
        self._parameters = parameter_data
        self._stream_properties = stream_properties
        self.stages = stages
        self.superstructure = superstruct
        
        if correction_factors == None:
            print("No correction factors provided, so all assumed to equal 1")
            
        elif isinstance(correction_factors,dict):
            if bool(correction_factors) == True:
                self._correction_factors = {}
                self._correction_factors = correction_factors
            else:
                pass
        else:
            raise RuntimeError("correction factors need to be inputted as a dictionary or set to None")
        # NEED TO GIVE ERROR MESSAGES AND  Checks for the data
  
    #==========================================================
    #        FIRST NLP FOR INITIALIZATION OF MINLP
    #==========================================================
    def NLP_MENS_init(self, correction_factors=None, omega = None):
        """This function performs an NLP suboptimization with all user-defined matches selected.
        
        This is then used to initialize the MINLP optimization. Currently utilizes IPOPT to perform the
        optimization, however it is hoped to include options for other solvers in the future.
        
        Args:
            correction_factors (dict, optional): Can be used to start an optimization with correction facotrs known,
                                            e.g. when a previous iteration failed.
                                            
        Returns:
            model (Concrete model from Pyomo): the model with optimal solution found
            results (Pyomo solved results): the results from the solver
            
        """
        if correction_factors == None:
            print("No correction factors provided, so all assumed to equal 1")
                    
        elif isinstance(correction_factors,dict):
            if bool(correction_factors) == True:
                self._correction_factors = {}
                self._correction_factors = correction_factors
            else:
                pass
        else:
            raise RuntimeError("correction factors need to be inputted as a dictionary or set to None")
        
        model = ConcreteModel()
        #Setting the data to belong to the model
        model._rich_data=None
        model._rich_data = self._rich_data
        model._lean_data = self._lean_data
        #==============
        #   SCALARS
        #==============
        # number of rich and lean streams
        model.nrps = len(self._rich_data.index)
        model.nlut = len(self._lean_data.index)
       
        #==============
        #   SETS
        #==============
        #Rich streams
        model.i = Set(initialize=self._rich_data.index)

        #lean streams/utilities
        model.j = Set(initialize=self._lean_data.index)

        # Composition superstructure locations
        # will have number of stages = to largest of number of utilities or rps

        # model.stages = RangeSet(model.nstages+1)

        #Stream Data
        model.data = Set(['Cin','Cout','F','cost','m'])
        model.stream_props = Set(['RHOG','RHOL'])
        model.parameters = Set(['kw','omega','AF','ACH','fixcost','EMAC','diameter','packcost','SurfA'])
        #================================
        #   SUPERSTRUCTURE GENERATION
        #================================
        # IDEA IS TO AUTOMATE THE SUPERSTRUCTURE GENERATION and include in init
        # THIS IS SBS
        if self.superstructure == 'SBS':
            model.nstages = (model.nlut+model.nrps)-1
        elif self.superstructure == 'SWS':
            if self.stages == None:
                #if we do not have explicitly defined stages we just use Yee and Grossmann's heuristic
                self.stages = max(model.nlut,model.nrps)
                model.nstages = self.stages
            else:
                model.nstages = self.stages
        #max(model.nlut,model.nrps)+1
        
        #model.k = RangeSet((model.nstages+1))        
 
        if self.superstructure == 'SBS':                
            count = 0
            supply_dict = {}
            for i in model.i:
                if self._rich_data.at[i,'Cin'] in supply_dict.values():
                    pass
                else: 
                    supply_dict[count] = self._rich_data.at[i,'Cin']
                    count += 1
            for j in model.j:
                if self._lean_data.at[j,'Cin'] in supply_dict.values():
                    pass
                else:
                    supply_dict[count] = self._lean_data.at[j,'Cin']    
                    count += 1
            vals = sorted(supply_dict.values(), reverse=True)
            #print(vals)
            
            ckval = {}
            for i in range(count):
                #print(i)
                ckval[i+1] = vals[i]
            
            #print(ckval)
            model.k = RangeSet((len(ckval)))
            model.nstages = len(ckval) - 1
            model.ck =Param(model.k, initialize = ckval)
            
            model.ckr_first = Param(model.i,model.k,initialize = 0.0,mutable=True)
            
            for i in model.i:
                for k in model.k:
                    if model.ck[k] == self._rich_data.at[i,'Cin']:
                        model.ckr_first[i,k] = model.ck[k]
            model.ckr_first.pprint()            
            model.ckl_first = Param(model.j,model.k,initialize = 0.0,mutable=True)
            
            for j in model.j:
                for k in model.k:
                    if model.ck[k] == self._lean_data.at[j,'Cin']:
                        model.ckl_first[j,k] = model.ck[k]
                  
            model.ckl_first.pprint()         
            model.r_exist = Param(model.i,model.k,initialize = 0.0,mutable=True)
            
            for i in model.i:
                for k in model.k:
                    if k == (model.nstages+1):
                        model.r_exist[i,k] = 0
                    elif model.ck[k] <= self._rich_data.at[i,'Cin']:
                        model.r_exist[i,k] = 1
                    else:
                        model.r_exist[i,k] = 0
            
    
            model.l_exist = Param(model.j,model.k,initialize = 0.0,mutable=True)
            
            for j in model.j:
                for k in model.k:
                    if k == (model.nstages+1):
                        model.l_exist[j,k] = 0
                    elif k == 1:
                        model.l_exist[j,k] = 1
                    elif model.ck[k] == self._lean_data.at[j,'Cin']:
                        model.l_exist[j,k] = 0
                    elif model.ck[k] >= self._lean_data.at[j,'Cin']:
                        model.l_exist[j,k] = 1
                                
            #model.l_exist.pprint()        
            #model.r_exist.pprint() 
                        
            #Superstructure for SBS
            model.arex = {}
            for i in model.i:
                for j in model.j:
                    for k in model.k:
                        if model.l_exist[j,k] == 1 and model.r_exist[i,k] == 1:
                            model.arex[i,j,k] = 1
                        else:
                            model.arex[i,j,k] = 0         

        elif self.superstructure == 'SWS':
            model.k = RangeSet((model.nstages+1)) 
            model.arex ={}
            for i in model.i:
                for j in model.j:
                    for k in model.k:
                        if k != model.nstages+1:
                            model.arex[i,j,k] = 1
                        else:
                            model.arex[i,j,k] = 0
            
            r_exist ={}
            for i in model.i:
                for k in model.k:
                    
                    if k != model.nstages+1:
                        r_exist[i,k] = 1
                    else:
                        r_exist[i,k] = 0

            model.r_exist = Param(model.i,model.k,initialize = r_exist)
            l_exist ={}
            for j in model.j:
                for k in model.k:
                    
                    if k != model.nstages+1:
                        l_exist[j,k] = 1
                    else:
                        l_exist[j,k] = 0

            model.l_exist = Param(model.j,model.k,initialize = l_exist)
            
            model.ckr_first = Param(model.i,model.k,initialize = 0.0,mutable=True)
            
            for i in model.i:
                for k in model.k:
                    if k == 1:
                        model.ckr_first[i,k] = 1

            model.ckr_first.pprint()  
                       
            model.ckl_first = Param(model.j,model.k,initialize = 0.0,mutable=True)
            
            for j in model.j:
                for k in model.k:
                    if k == model.nstages + 1: 
                        model.ckl_first[j,k] = 1
                  
            model.ckl_first.pprint()         
                                
            model.l_exist.pprint()        
            model.r_exist.pprint() 
            
        else:
            raise RuntimeError("Superstructure not SWS or SBS")
        #print(model.arex)       
        #=========================================================
        #   PARAMETERS
        #=========================================================

        #Number of rich streams/contaminated streams
        model.rps = Param(model.i, within = Integers)
        #Number of lean streams/utilities
        model.lps = Param(model.j, within = Integers)

        #Locations of first and last stages
        def first_stage(model,i):
            if i==1:
                return True
            else:
                return False
        
        model.first = Param(model.k, initialize=first_stage)
        
        def last_stage(model,i):  
            if i==(model.nstages+1):
                return True
            else:
                return False
        
        model.last = Param(model.k, initialize = last_stage)

        #is this a mass transfer stage? (i.e. not an interval boundary)
        def m_stage(model,i):  
            if i<=(model.nstages):
                return True
            else:
                return False
        model.st = Param(model.k, initialize = m_stage)
        model.stages = RangeSet(model.nstages)
        model.stages.pprint()
        model.last.pprint()
        parameters = dict()
        for i in self._parameters.index:
            parameters[i] = self._parameters.at[i,'value']
        #BIG-M vale for Big-M constraint
        # THIS SHOULD BE EXTERNAL AND WE SHOULD GENERATE IT.Start some big val and decrease
        if omega == None:
            model.omega = Param (model.i,model.j, initialize=parameters['omega'])
        else:
            model.omega = Param (model.i,model.j, initialize=omega)
        
        #Problem-specific parameters
        #Still need to implement CHECKs FOR THEIR PRESENCE
        #mass transfer coefficient
        p=parameters['kw']
        model.kw = Param(initialize=p)
                
        count = 0
        kw_cord = dict() 
        for i in model.i:
            for j in model.j:
                for k in model.k:
                    if self._correction_factors==None:
                        kw_cord[i,j,k]=1
                    else:
                        kw_cord[i,j,k]=self._correction_factors[count,"kwcor"]
                    count +=1

        def kw_cor_init(model, i,j,k):
            return kw_cord[i,j,k]

        model.kwcor = Param(model.i, model.j, model.k, initialize=kw_cor_init)
        #annualization factor (over how many years, normally 5 thus AF = 0.2)
        model.AF = Param(initialize=parameters['AF'])
        #annual cost per height of continuous contact colum
        model.ACH = Param(initialize=parameters['ACH'])
        #fixedcost associated with an exchanger
        model.fixcost = Param(initialize=parameters['fixcost'])
        #minimum approach composition
        model.EMAC = Param(initialize=parameters['EMAC'])
        
        # densities
        rhog={}
        rhol={}
        aci={}
        count = 0
        for i in self._stream_properties.stream:            
            if self._stream_properties.index[count]=='RHOG':
                rhog[i]=self._stream_properties.iloc[count]['value']
            if self._stream_properties.index[count]=='RHOL':
                rhol[i]=self._stream_properties.iloc[count]['value']
            if self._stream_properties.index[count]=='aci':
                aci[i]=self._stream_properties.iloc[count]['value']
            count+=1
                
        model.RHOG=Param(model.i, initialize=rhog)
        model.RHOL=Param(model.j,initialize=rhol)
        
        # diameter (initial and correction)
        # This should also be set by user (or even decided through the software based on initialization run)
        def dia_init(model, i,j,k):
            if model.arex[i,j,k] == 1:
                return parameters['diameter']
            else:
                return 0.0
        
        model.dia = Param(model.i, model.j, model.k, initialize=dia_init) 

        count = 0
        dia_cord = dict() 
        for i in model.i:
            for j in model.j:
                for k in model.k:
                    if self._correction_factors==None:
                        dia_cord[i,j,k]=1
                    else:
                        dia_cord[i,j,k]=self._correction_factors[count, "diacor"]
                    count +=1

        def dia_cor_init(model, i,j,k):
            return dia_cord[i,j,k]
           
        model.diacor = Param(model.i, model.j, model.k, initialize=dia_cor_init)     
        
        count = 0
        h_cord = dict() 
        for i in model.i:
            for j in model.j:
                for k in model.k:
                    if self._correction_factors==None:
                        h_cord[i,j,k]=1
                    else:
                        h_cord[i,j,k]=self._correction_factors[count, "heightcor"]
                    count +=1

        def h_cor_init(model, i,j,k):
            return h_cord[i,j,k]        
        
        model.heightcor= Param(model.i, model.j, model.k, initialize=h_cor_init)
        
        # packing cost per meter^3
        model.packcost = Param(model.i, model.j, model.k, initialize=parameters['packcost'])

        count = 0
        packc_cord = dict() 
        for i in model.i:
            for j in model.j:
                for k in model.k:
                    if self._correction_factors==None:
                        packc_cord[i,j,k]=1
                    else:
                        packc_cord[i,j,k]=self._correction_factors[count,"packcostcor"]
                    count +=1

        def packc_cor_init(model, i,j,k):
            return packc_cord[i,j,k]
        
        model.packcostcor = Param(model.i, model.j, model.k, initialize=packc_cor_init)
           
        #surface area associated with the packing and fluid/gas velocities
        model.surfA = Param(model.i, model.j, model.k, initialize=parameters['SurfA'])
        
        count = 0
        surfA_cord = dict() 
        for i in model.i:
            for j in model.j:
                for k in model.k:
                    if self._correction_factors==None:
                        surfA_cord[i,j,k]=1
                    else:
                        surfA_cord[i,j,k]=self._correction_factors[count,"surfAcor"]
                    count +=1

        def surfA_cor_init(model, i,j,k):
            return surfA_cord[i,j,k]
        
        model.surfAcor = Param(model.i, model.j, model.k, initialize = surfA_cor_init)

        #cost of the lean streams
        model.AC = Param(model.j, initialize=aci)
        model.AC.pprint()
        #=================
        #   VARIABLES
        #=================
        def y_bounds(model,i,j,k):
            if model.arex[i,j,k] ==1:
                return (0,1)
            else:
                return (0.0,0.0)
        
        
        #These are actually fixed here to arex
        model.y = Param(model.i,model.j,model.k, initialize = model.arex)
        #relaxed binary
        model.y1 = Var(model.i,model.j,model.k, initialize = model.arex, bounds=y_bounds)
        
        #Variables for design of network
        #Composition at each interval boundary
        def cl_init(model,j,k):
            return abs((self._lean_data.at[j,'Cin']-self._lean_data.at[j,'Cout']))/2

        def cr_init(model,i,k):
            return abs((self._rich_data.at[i,'Cout']-self._rich_data.at[i,'Cin']))/2

        def cr_bounds(model,i,k):
            lb = self._rich_data.at[i,'Cout']
            ub = self._rich_data.at[i,'Cin']
            return (lb,ub)

        def cl_bounds(model,j,k):
            lb = self._lean_data.at[j,'Cin']
            ub = self._lean_data.at[j,'Cout']
            return (lb,ub)

        model.cr = Var(model.i,model.k, initialize= cr_init, bounds = cr_bounds)
        model.cl = Var(model.j,model.k, initialize= cl_init, bounds = cl_bounds)
        
        # THESE WILL ONLY BE NECESSARY IF WE WANT TO SOLVE MINLP WITH NON ISOCOMP MIXING
        '''
        #Composition at each interval boundary before mixing
        #enables non sio-compositional mixing
        
        #def crin_bounds(model,i,j,k):
        #    lb = 0.0
            #Rich_data.at[i,'Cout']
        #    ub = None
        #    return (lb,ub)

        #def clin_bounds(model,i,j,k):
        #    lb = 0
            #Lean_data.at[j,'Cin']
        #    ub = None
        #    return (lb,ub)

        #def clin_init(model,i,j,k):
        #    return self._lean_data.at[j,'Cin']
        #def crin_init(model,i,j,k):
        #    return self._rich_data.at[i,'Cin']

        #THESE HERE SHOULD BE INCLUDED VIA AN OPTION TO THE USER AS TO WHETHER THEY WOULD LIKE TO INCLUDE 
        #NON-ISOCOMPOSITIONAL MIXING in the MINLP

        #model.crin = Var(model.i,model.j,model.k, initialize = crin_init, bounds=crin_bounds)
        #model.clin = Var(model.i,model.j,model.k, initialize = clin_init, bounds=clin_bounds)
        '''
        
        #Amount of lean stream utilized
        model.avlean = Var(model.j, initialize=0.06, within=NonNegativeReals)
        
        #Mass exchanged
        def m_init(model,i,j,k):
            if model.arex[i,j,k] ==1:
                c=(self._rich_data.at[i,'F']*(self._rich_data.at[i,'Cin']-self._rich_data.at[i,'Cout']))
                return c
            else:
                return 0.0
   
        def m_bounds(model,i,j,k):
            if model.arex[i,j,k] ==1:
                return (0,(self._rich_data.at[i,'F']*(self._rich_data.at[i,'Cin']-self._rich_data.at[i,'Cout'])))
            else:
                return (0,0)

        model.M = Var(model.i,model.j,model.k, initialize=m_init, bounds = m_bounds)
        
        #rule for bounds of lean streams
        def L_bounds(model,j):
            if self._lean_data.at[j,'F']>0:
                return (0.05,self._lean_data.at[j,'F'])
        
            else:
                # THESE SHOULD BE GENERATED FROM DATA
                return (0.01, 10)
            
        def L_init(model,j):
            if self._lean_data.at[j,'F']>0:
                return self._lean_data.at[j,'F']
        
            else:
                # THESE SHOULD BE GENERATED FROM DATA
                return 1.5
        
        #Flowrate of lean used (J) all included
        #this should be changed - init
        model.L = Var(model.j, initialize=L_init,bounds = L_bounds)

        #   Flowrate of splits for non iso-compositional mixing
        '''
        def Flrich_bounds(model,i,j,k):
            if model.arex[i,j,k] ==1:
                return (0.01,self._rich_data.at[i,'F'])
            else:
                return (0.0,50)
    
        def Flrich_init(model,i,j,k):
            if model.arex[i,j,k] ==1:
                return 0.1
            else:
                return 0.1
            
        def Flean_bounds(model,i,j,k):
            if model.arex[i,j,k] ==1:
                return (0.0,10.0)
            else:
                return (0.00,10.0)
    
        def Flean_init(model,i,j,k):
            if model.arex[i,j,k] ==1:
                return 0.1
            else:
                return 0.1       
        #model.Flrich = Var(model.i,model.j,model.k, initialize=Flrich_init,bounds=Flrich_bounds)
        #model.Flean = Var(model.i,model.j,model.k, initialize=Flean_init,bounds=Flean_bounds)
        '''
        
        #initialization rules
        def dcin_init_rule(model,i,j,k):
            return self._rich_data.at[i,'Cin']-self._lean_data.at[j,'Cin']

        def dcin_bounds_rule(model,i,j,k):
            if model.arex[i,j,k] ==1:
                return (model.EMAC,1)
            else:
                return (model.EMAC,None)
    
        def dcout_init_rule(model,i,j,k):
            return self._rich_data.at[i,'Cin']-self._lean_data.at[j,'Cin']

        def dcout_bounds_rule(model,i,j,k):
            if k>=2:
                if model.arex[i,j,k-1] == 1:
                    return (model.EMAC,1)
                else:
                    return (model.EMAC,None) 
            else:
                return (model.EMAC,None) 
    
        #Composition difference/ driver for the mass exchange
        model.dcin = Var(model.i,model.j,model.k, initialize=dcin_init_rule,bounds=dcin_bounds_rule)
        model.dcout= Var(model.i,model.j,model.k, initialize=dcout_init_rule,bounds=dcout_bounds_rule)

        # non-isocompositional mixing flows in branches - Turn on with option
        '''
        def flv_init(model,i,j,k):
            if model.arex[i,j,k] ==1:
                return 0.1
            else:
                return 0.1 
        #model.flv = Var(model.i,model.j,model.k, initialize=flv_init, bounds = (0.00, None))
        '''
        
        #positive/negative tolerance
        model.pnhc=Var(model.i,model.j,model.k, initialize= 1e-6,within = NonNegativeReals)
        model.snhc=Var(model.i,model.j,model.k, initialize= 1e-6,within = NonNegativeReals)

        #mass transfer coefficient
        model.kya=Var(model.i,model.j,model.k, initialize = 13, bounds = (0.00, None))
        
        #height of column
        def height_init(model, i,j,k):
            if model.arex[i,j,k] ==1:
                return 2
            else:
                return 0.0
    
        def height_bounds(model, i,j,k):
            if model.arex[i,j,k] ==1:
                return (0.0,None)
            else:
                return (0.0,0.0)

        model.height =  Var(model.i,model.j,model.k, initialize=height_init,bounds=height_bounds)

        #==================================================================================
        #   CONSTRAINTS
        #==================================================================================
        #===============================================================================
        #===============================================================================
        #assignment of stream inlet compositions
        def CRichIn_(model, i,k):
            if model.ckr_first[i,k] != 0.0:
                return model.cr[i,k] == (self._rich_data.at[i,'Cin'])

            else:
                return Constraint.Skip

        model.CRichIn = Constraint(model.i,model.k, rule=CRichIn_)
        
        def CLeanIn_(model, j,k):
            if model.ckl_first[j,k] != 0.0:
                return model.cl[j,k] == float(self._lean_data.at[j,'Cin'])
            else:
                return Constraint.Skip

        model.CLeanIn = Constraint(model.j, model.k, rule=CLeanIn_)

        def CRichOut_(model, i,k):
            if (model.last[k])==True:
                return model.cr[i,k] == float(self._rich_data.at[i,'Cout'])
            else:
                return Constraint.Skip

        model.CRichOut = Constraint(model.i,model.k, rule=CRichOut_)
             
        def CLeanOut_(model, j,k):
            if model.first[k] == True:
                return model.cl[j,k] == float(self._lean_data.at[j,'Cout'])        
            else:
                return Constraint.Skip

        model.CLeanOut = Constraint(model.j,model.k,rule=CLeanOut_)
        
        #Available mass in lean stream j
        def AvLean_(model,j):
            a = (self._lean_data.at[j,'Cout'])-(self._lean_data.at[j,'Cin'])
            return model.avlean[j] == model.L[j]*(a)

        model.AvLean = Constraint(model.j, rule=AvLean_)

        #Stream overall mass balance
        def Total_Mass_Rich_(model,i):   
            f=(self._rich_data.at[i,'F'])*((self._rich_data.at[i,'Cin'])-(self._rich_data.at[i,'Cout'])) 
            return float(f)== sum(model.M[i,j,k] for j in model.j for k in model.k if model.arex[i,j,k] == 1)                    
        
        model.Total_Mass_Rich = Constraint(model.i, rule = Total_Mass_Rich_)
        
        def Total_Mass_Lean_(model,j):
            f=model.L[j]*(((self._lean_data.at[j,'Cout'])-(self._lean_data.at[j,'Cin'])))
            c=f
            return model.L[j]*(((self._lean_data.at[j,'Cout'])-(self._lean_data.at[j,'Cin']))) == sum(model.M[i,j,k] for i in model.i for k in model.k if model.arex[i,j,k] == 1)
            
        model.Total_Mass_Lean = Constraint(model.j, rule = Total_Mass_Lean_)

        # stage stream overall mass balance
        def Stage_Mass_Rich_(model,i,k):    
            if k == (model.nstages+1):
                return Constraint.Skip
            elif model.r_exist[i,k] == 1:    
                f =(self._rich_data.at[i,'F'])
                c=f
                return float(self._rich_data.at[i,'F'])*(model.cr[i,k]-model.cr[i,(k+1)])== sum(model.M[i,j,k] for j in model.j if model.arex[i,j,k] == 1)
            else:
                return Constraint.Skip
    
        model.Stage_Mass_Rich = Constraint(model.i, model.k, rule = Stage_Mass_Rich_)

        def Stage_Mass_Lean_(model,j,k):    
            if k == (model.nstages+1):
                return Constraint.Skip
            elif model.l_exist[j,k] == 1:
                return model.L[j]*(model.cl[j,k] - model.cl[j,(k+1)]) == \
                    sum(model.M[i,j,k] for i in model.i if model.arex[i,j,k] == 1)                
            else:
                return Constraint.Skip 
            
        model.Stage_Mass_Lean = Constraint(model.j,model.k, rule = Stage_Mass_Lean_)

        # Checking that concentrations move in one direction
        def Monot_Rich_(model,i,k):
            if k == (model.nstages+1):
                return Constraint.Skip
            else:
                return model.cr[i,k] >= model.cr[i,(k+1)]

        model.Monot_Rich = Constraint(model.i, model.k, rule = Monot_Rich_)

        def Monot_Lean_(model,j,k):
            if k == (model.nstages+1):
                return Constraint.Skip
            else:
                return model.cl[j,k] >= model.cl[j,(k+1)]

        model.Monot_Lean = Constraint(model.j, model.k, rule = Monot_Lean_)

        '''
        #Equations for non-isocomp mixing
        #def Monot_RichSub_(model,i,j,k):
        #    if k == (model.nstages+1):
        #        return Constraint.Skip
        #    else:
        #        return model.cr[i,k] >= model.crin[i,j,(k+1)]

        #model.Monot_RichSub = Constraint(model.i, model.j, model.k, rule = Monot_RichSub_)
    
        #def Monot_LeanSub_(model,i,j,k):
        #    if k == (model.nstages+1):
        #        return Constraint.Skip
        #    else:
        #        return model.clin[i,j,k] >= model.cl[j,(k+1)]
    
        #model.Monot_LeanSub = Constraint(model.i,model.j, model.k, rule = Monot_LeanSub_)
        '''
        
        # Binary variable relaxation strategy
        def P_(model,i,j,k):
            if k == (model.nstages+1):
                return Constraint.Skip
            else:
                return model.pnhc[i,j,k] == 1e-6
        model.P = Constraint(model.i, model.j, model.k, rule = P_)

        def S_(model,i,j,k):
            if k == (model.nstages+1):
                return Constraint.Skip
            else:
                return model.snhc[i,j,k] == 1e-6

        model.S = Constraint(model.i, model.j, model.k, rule = S_)

        def N_(model,i,j,k):
            if k == (model.nstages+1):
                return Constraint.Skip
            else:
                return model.y[i,j,k] == model.y1[i,j,k]+(model.pnhc[i,j,k]- model.snhc[i,j,k])

        model.N = Constraint(model.i, model.j, model.k, rule = N_)

        '''
        # Mass balances over streams for non-iso-comp mixing
        #def FlowRich_(model,i,k):
        #    if k == (model.nstages+1):
        #        return Constraint.Skip
        #    elif model.r_exist[i,k] == 1:
        #        c = float(Rich_data.at[i,'F'])
        #        return c == sum(model.Flrich[i,j,k] for j in model.j if arex[i,j,k] == 1)
        #    else:
        #        return Constraint.Skip
    
        #model.FlowRich = Constraint(model.i, model.k, rule = FlowRich_)
    
        #def FlowLean_(model,j,k):
        #    if k == (model.nstages+1):
        #        return Constraint.Skip
        #    elif model.l_exist[j,k] == 1:
        #        return model.L[j]== sum(model.Flean[i,j,k] for i in model.i if arex[i,j,k]==1)
        #    else:
        #        return Constraint.Skip
    
        #model.FlowLean = Constraint(model.j, model.k,  rule = FlowLean_)

        #Unit mass balances
        #def ExUnitR_(model,i,j,k):
        #    if arex[i,j,k] == 1:
        #      return model.Flrich[i,j,k]*(model.cr[i,k]-model.crin[i,j,(k+1)])== model.M[i,j,k]
        #    else:
        #        return Constraint.Skip
                
        #model.ExUnitR = Constraint(model.i, model.j, model.k, rule = ExUnitR_)

        #def ExUnitL_(model,i,j,k):
        #    if arex[i,j,k] == 1:   
        #        return model.Flean[i,j,k]*(model.clin[i,j,k]-model.cl[j,(k+1)])== model.M[i,j,k]
        #    else:
        #        return Constraint.Skip    
        #model.ExUnitL = Constraint(model.i, model.j, model.k, rule = ExUnitL_)
        '''
        
        #Logical Constraint on Mass exchanged between RPS(i) and LPS (j)
        def Log_M_RPS_LPS_(model,i,j,k):

            c = ((self._rich_data.at[i,'F'])*((self._rich_data.at[i,'Cin'])-(self._rich_data.at[i,'Cout'])))
            c=(c)
            d=(model.L[j]*(((self._lean_data.at[j,'Cout'])-((self._lean_data.at[j,'Cin'])))))
            if model.arex[i,j,k] == 1:
                if value(c) >=value(d):
                    return model.M[i,j,k] <= (model.L[j]*(((self._lean_data.at[j,'Cout'])-((self._lean_data.at[j,'Cin'])))))*model.y[i,j,k]
                else:
                    return model.M[i,j,k] <= ((self._rich_data.at[i,'F'])*((self._rich_data.at[i,'Cin'])-(self._rich_data.at[i,'Cout'])))*model.y[i,j,k]
            else:
                return Constraint.Skip
    
        model.Log_M_RPS_LPS = Constraint(model.i, model.j, model.k, rule = Log_M_RPS_LPS_)
        
        #LOGICAL CONSTRAINT ON RICH SIDE COMPOSITION DIFFERENCE BETWEEN RPS(I) AND LPS(J)
        def Log_DC_RPS_LPS_RS_(model,i,j,k):
            if model.arex[i,j,k] == 1:
                return model.dcin[i,j,k] <= model.cr[i,k] - model.cl[j,k]+ model.omega[i,j]*(1-model.y[i,j,k])
            else:
                return Constraint.Skip

        model.Log_DC_RPS_LPS_RS = Constraint(model.i, model.j, model.k, rule = Log_DC_RPS_LPS_RS_)
        
        def Log_DC_RPS_LPS_RS1_(model,i,j,k):
            if model.arex[i,j,k] == 1:
                return model.dcin[i,j,k] >= model.cr[i,k] - model.cl[j,k]- model.omega[i,j]*(1-model.y[i,j,k])
            else:
                return Constraint.Skip
        model.Log_DC_RPS_LPS_RS1 = Constraint(model.i, model.j, model.k, rule = Log_DC_RPS_LPS_RS1_)

        #LOGICAL CONSTRAINT ON Lean SIDE COMPOSITION DIFFERENCE BETWEEN RPS(I) AND LPS(J)
        def Log_DC_RPS_LPS_LS_(model,i,j,k):
            if model.arex[i,j,(k)] == 1:
                return model.dcout[i,j,(k+1)] <= model.cr[i,(k+1)] - model.cl[j,(k+1)]+\
                                                 model.omega[i,j]*(1-model.y[i,j,k])
            else:
                return Constraint.Skip
        model.Log_DC_RPS_LPS_LS = Constraint(model.i, model.j, model.k, rule = Log_DC_RPS_LPS_LS_)

        def Log_DC_RPS_LPS_LS1_(model,i,j,k):
            if model.arex[i,j,k] == 1:
                return model.dcout[i,j,(k+1)] >= model.cr[i,(k+1)] - model.cl[j,(k+1)] -\
                                     model.omega[i,j]*(1-model.y[i,j,k])
            else:
                return Constraint.Skip

        model.Log_DC_RPS_LPS_LS1 = Constraint(model.i, model.j, model.k, rule = Log_DC_RPS_LPS_LS1_)


        '''
        #EQUATIONS FOR NON_ISOCOMP MIXING
        #def FlowLV_(model,i,j,k):
        #    if arex[i,j,k] == 1:
        #        return model.flv[i,j,k] == (model.Flean[i,j,k]/model.Flrich[i,j,k])*((model.RHOG[i,j]/model.RHOL[j])**0.5)
        #    else:
        #        return Constraint.Skip
    
        #model.FlowLV = Constraint(model.i, model.j, model.k, rule = FlowLV_)   
        '''
        def KYTransferMass_(model, i,j,k):
            if model.arex[i,j,k]==1:
                return model.kya[i,j,k]==model.kw*model.surfA[i,j,k]*model.surfAcor[i,j,k]*model.kwcor[i,j,k]
            else:
                return Constraint.Skip
    
        model.KYTransferMass = Constraint(model.i, model.j, model.k, rule = KYTransferMass_)    
    
        def HeightColumn_(model,i,j,k):
            if model.arex[i,j,k] == 1:
                return model.height[i,j,k] == model.M[i,j,k]/(((model.kya[i,j,k]*numpy.pi/4*((model.dia[i,j,k]*model.diacor[i,j,k])**2))) *\
                                          (((model.dcin[i,j,k]*model.dcout[i,j,(k+1)])*\
                                           (model.dcin[i,j,k]+model.dcout[i,j,(k+1)])*0.5)**(0.33333)+1E-12)+1E-12)*model.y[i,j,k]
            else:
                return Constraint.Skip

        model.HeightColumn = Constraint(model.i, model.j, model.k, rule = HeightColumn_)
        
        #==================================================================================
        #   COBJECTIVE FUNCTION AND SOLVE STATEMENT
        #==================================================================================
        model.w = 0.000001
        def TACeq_(model):
            tac = 0
            for i in model.i:
                for j in model.j:
                    for k in model.k:
                        tac += model.AF*23805*((model.diacor[i,j,k]*model.dia[i,j,k])**0.57)*1.15*model.heightcor[i,j,k]*model.height[i,j,k]
                        tac += model.AF*numpy.pi*((model.dia[i,j,k]*model.diacor[i,j,k])**2)/4*model.height[i,j,k]*model.heightcor[i,j,k]*model.packcost[i,j,k]*model.packcostcor[i,j,k]
                        tac += model.fixcost*model.y[i,j,k]
                        tac += model.w*(model.pnhc[i,j,k]+model.snhc[i,j,k])
            for j in model.j:
                tac += model.L[j]*model.AC[j]            
            return tac
        
        model.TACeqn = Objective(rule = TACeq_, sense = minimize)


        model_clone_before_solve = model.clone()
        
        results = solve_until_feas_NLP(model)
        model.display()

        print("THIS IS THE END OF THE NLP INITIALIZATION")
        success = bool
        #print(results)
        try:
            if (results.solver.status == SolverStatus.ok) and (results.solver.termination_condition == TerminationCondition.optimal):
                model.height.pprint()
                model.M.pprint()
                model.avlean.pprint()
                model.L.pprint()
                model.cr.pprint()
                model.cl.pprint()
                model.dcin.pprint()
                model.dcout.pprint()
                model.y.pprint()
                print(model.TACeqn())
                success = True
                print("Successful solution of initialization problem")
            elif (results.solver.status == SolverStatus.ok) and (results.solver.termination_condition == TerminationCondition.locallyOptimal):
                model.height.pprint()
                model.M.pprint()
                model.avlean.pprint()
                model.L.pprint()
                model.cr.pprint()
                model.cl.pprint()
                model.dcin.pprint()
                model.dcout.pprint()
                model.y.pprint()
                print(model.TACeqn())
                print("Successful solution of initialization problem")  
                success = True
            else:
                print("INITIALIZATION FAILED")
                model.height.pprint()
                model.M.pprint()
                model.avlean.pprint()
                model.L.pprint()
                model.cr.pprint()
                model.cl.pprint()
                model.dcin.pprint()
                model.dcout.pprint()
                model.y.pprint()
                print(model.TACeqn())
                success = False
                model = model_clone_before_solve
            print("THIS IS THE END OF THE NLP INITIALIZATION")
        except:
            print("THE NLP initialization FAILED, problem may be infeasible!")
            success = False
        
        return model, success
    
    def MINLP_MENS_full(self, model, min_height_from_nlp=None, min_mass_ex_from_nlp=None, omega = None, bin_cuts = None, sym_cuts = None):
        """MINLP optimization model building and solving.
        
        This is the function that is called to solve the full MINLP model for MENS including binary variables
        Requires the solved NLP in as an argument in order to utilize the initializations provided.
        Args:
            model (Concrete Pyomo model): Pyomo model passed from the NLP solver, NLP_MENS_init
            min_height_from_nlp (int, optional): the smallest height values taken from the NLP suboptimization.
                                            These values will be changed if the first solve fails.
                                            
            min_mass_ex_from_nlp (int, optional): the smallest mass exchanged values taken from the NLP suboptimization.
                                            These values will be changed if the first solve fails.
            
        returns:
            solved pyomo model
            
        """
        
        print("MINLP MODEL SOLVING")
        # Initializing and adding/removing components from/to the pyomo model
        
        #==================================================================================
        #   CONSTRAINTS AND SETTING UP MODEL BASED ON NLP
        #==================================================================================
        #===============================================================================
        #===============================================================================
        
        #This section is where the initial heights are filtered and the smaller set of binary variables
        #are chosen based on the values from the NLP
        if omega == None:
            pass
        else:
            model.del_component(model.omega)
            model.omega = Param (model.i,model.j, initialize=omega)
                        
        model.ih = {}
        for i in model.i:
            for j in model.j:
                for k in model.k:
                    if min_height_from_nlp:
                        if model.height[i,j,k].value <= min_height_from_nlp:
                        
                            model.ih [i,j,k] = 0
                            model.arex[i,j,k] = 0
                        else:
                            model.arex [i,j,k] =1
                            model.ih [i,j,k] = model.height[i,j,k].value
                    else:
                        #print("no min height from NLP set, so it is assumed to be 0.000001")
                        if model.height[i,j,k].value <= 0.000000000001:
                            model.ih [i,j,k] = 0
                            model.arex[i,j,k] = 0
                        else:
                            model.arex [i,j,k] =1
                            model.ih [i,j,k] = model.height[i,j,k].value
                   
        model.min_height_from_nlp = min_height_from_nlp
        def height_bounds(model, i,j,k):
            if model.arex[i,j,k] ==1:
                return (0.0,None)
            else:
                return (0.0,0.0)
      
        model.del_component(model.height)
        model.del_component(model.height_index)
        model.del_component(model.height_index_index_0)
        
        model.height =  Var(model.i,model.j,model.k, initialize=model.ih, within=NonNegativeReals, bounds = height_bounds)
        
        model.iy = {}
        for i in model.i:
            for j in model.j:
                for k in model.k:
                    if model.arex[i,j,k] == 1:
                        model.iy[i,j,k] = 1
                    else:
                        model.iy[i,j,k] = 0
      
        
        model.del_component(model.y)
        model.del_component(model.y_index)
        model.del_component(model.y_index_index_0)
        
        model.y = Var(model.i,model.j,model.k, initialize = model.iy,within = Binary)
        #for i in model.i:
        #    for j in model.j:
        #        for k in model.k:        
        #            if model.arex[i,j,k] == 0 and model.iy[i,j,k] == 0:
                        #model.y[i,j,k].value = 0
                        #model.y[i,j,k].fixed=True
        print("THESE ARE THE INIT y")
        model.y.pprint()
        model.del_component(model.y1)
        model.del_component(model.y1_index)
        model.del_component(model.y1_index_index_0)
        
        model.y1 = Var(model.i,model.j,model.k, initialize = model.iy, within = NonNegativeReals, bounds=(0,1))
        #initialization rules
       
        def dcin_init_rule(model,i,j,k):
            return self._rich_data.at[i,'Cin']-self._lean_data.at[j,'Cin']

        def dcin_bounds_rule(model,i,j,k):
            if model.arex[i,j,k] ==1:
                return (model.EMAC,1)
            else:
                return (model.EMAC,None)
        model.del_component(model.dcin)
        model.del_component(model.dcin_index)
        model.del_component(model.dcin_index_index_0)
        
        def dcout_init_rule(model,i,j,k):
            return self._rich_data.at[i,'Cin']-self._lean_data.at[j,'Cin']

        def dcout_bounds_rule(model,i,j,k):
            if k>=2:
                if model.arex[i,j,k-1] == 1:
                    return (model.EMAC,1)
                else:
                    return (model.EMAC,None) 
            else:
                return (model.EMAC,None) 
        model.del_component(model.dcout)
        model.del_component(model.dcout_index)
        model.del_component(model.dcout_index_index_0)

        model.dcin = Var(model.i,model.j,model.k, initialize=dcin_init_rule,bounds=dcin_bounds_rule)
        model.dcout= Var(model.i,model.j,model.k, initialize=dcout_init_rule,bounds=dcout_bounds_rule)
        
        #This section is where the initial mass exchanged variable are filtered and the smaller set of 
        #binary variables are chosen based on the values from the NLP
        """
        model.im = {}
        for i in model.i:
            for j in model.j:
                for k in model.k:
                    if min_mass_ex_from_nlp:
                        if model.M[i,j,k].value:
                            if model.M[i,j,k].value <= min_mass_ex_from_nlp:
                                model.im [i,j,k] = 0
                                #model.arex[i,j,k] = 0
                            elif model.arex [i,j,k] ==1:
                                model.im [i,j,k] = model.M[i,j,k].value
                    else:
                        #print("no min mass from NLP set, so it is assumed to be 1e-7")
                        if model.M[i,j,k].value:
                            if model.M[i,j,k].value <= 1e-7:
                                model.im [i,j,k] = 0
                                #model.arex[i,j,k] = 0
                            else:
                                #model.arex [i,j,k] =1
                                model.im [i,j,k] = model.M[i,j,k].value 
                        else:
                            model.im [i,j,k] = model.M[i,j,k].value
        """
        model.im = {}
        for i in model.i:
            for j in model.j:
                for k in model.k:
                    if model.arex[i,j,k] == 1:
                        model.im [i,j,k] = model.M[i,j,k].value
                    else:
                        model.im [i,j,k] = 0
                        
        def M_bounds(model, i,j,k):
            if model.arex[i,j,k] ==1:
                return (0.0,None)
            else:
                return (0.0,0.0)       
            
        model.del_component(model.M)
        model.del_component(model.M_index)
        model.del_component(model.M_index_index_0)  
        
        model.M = Var(model.i,model.j,model.k, initialize=model.im, bounds = M_bounds)
        
                #rule for bounds of lean streams
        def L_bounds(model,j):
            if self._lean_data.at[j,'F']>0:
                #print("LEAN DATA:   ",self._lean_data.at[j,'F'])
                return (0.1,self._lean_data.at[j,'F'])
        
            else:
                #print("LEAN DATA:   ",0,2)
                return (0.1, 10)
        #model.L.pprint()
        l_init={}
        for j in model.j:
            #print(j)
            l_init[j] = model.L[j].value
            #print(model.L[j].value)
        #print(l_init)
        #model.del_component(model.L)
        avleaninit={}
        for j in model.j:
            avleaninit[j] = model.avlean[j].value
                    
        model.del_component(model.avlean)
        model.avlean = Var(model.j, initialize=avleaninit, within=NonNegativeReals)
        
        model.L1 = Var(model.j, initialize=l_init,bounds = L_bounds)
        #model.L.pprint()
    
        #Available mass in lean stream j
        model.del_component(model.AvLean) 
        def AvLean_(model,j):
            a = (self._lean_data.at[j,'Cout'])-(self._lean_data.at[j,'Cin'])
            return model.avlean[j] == model.L1[j]*(a)

        model.AvLean = Constraint(model.j, rule=AvLean_)
        
        model.del_component(model.Total_Mass_Rich) 
        
        def Total_Mass_Rich_(model,i):   
            f=(self._rich_data.at[i,'F'])*((self._rich_data.at[i,'Cin'])-(self._rich_data.at[i,'Cout'])) 
            return float(f)== sum(model.M[i,j,k] for j in model.j for k in model.k if model.arex[i,j,k] == 1)                     
        
        model.Total_Mass_Rich = Constraint(model.i, rule = Total_Mass_Rich_)
        #for i in model.i:    
        #    print((self._rich_data.at[i,'F'])*((self._rich_data.at[i,'Cin'])-(self._rich_data.at[i,'Cout'])))
            
        model.del_component(model.Total_Mass_Lean) 
      
        def Total_Mass_Lean_(model,j):
            f=model.L1[j]*(((self._lean_data.at[j,'Cout'])-(self._lean_data.at[j,'Cin'])))
            c=f
            return model.L1[j]*(((self._lean_data.at[j,'Cout'])-(self._lean_data.at[j,'Cin']))) == sum(model.M[i,j,k] for i in model.i for k in model.k if model.arex[i,j,k] == 1)
            
        model.Total_Mass_Lean = Constraint(model.j, rule = Total_Mass_Lean_)

        # stage stream overall mass balance
        model.del_component(model.Stage_Mass_Rich) 
        model.del_component(model.Stage_Mass_Rich_index)
        def Stage_Mass_Rich_(model,i,k):    
            if k == (model.nstages+1):
                return Constraint.Skip
            elif model.r_exist[i,k] == 1:    
                f =(self._rich_data.at[i,'F'])
                c=f
                return float(self._rich_data.at[i,'F'])*(model.cr[i,k]-model.cr[i,(k+1)])== sum(model.M[i,j,k] for j in model.j if model.arex[i,j,k] == 1)
            else:
                return Constraint.Skip
            
        model.Stage_Mass_Rich = Constraint(model.i, model.k, rule = Stage_Mass_Rich_)
        
        model.del_component(model.Stage_Mass_Lean) 
        model.del_component(model.Stage_Mass_Lean_index)
        
        def Stage_Mass_Lean_(model,j,k):
    
            if k == (model.nstages+1):
                return Constraint.Skip
    
            elif model.l_exist[j,k] == 1:
                return model.L1[j]*(model.cl[j,k] - model.cl[j,(k+1)]) == \
                    sum(model.M[i,j,k] for i in model.i if model.arex[i,j,k] == 1)
                
            else:
                return Constraint.Skip 
            
        model.Stage_Mass_Lean = Constraint(model.j,model.k, rule = Stage_Mass_Lean_)

        # Binary variable relaxation strategy
        model.del_component(model.P) 
        model.del_component(model.P_index)
        model.del_component(model.P_index_index_0)
        
        def P_(model,i,j,k):
            if k == (model.nstages+1):
                return Constraint.Skip
            else:
                return model.pnhc[i,j,k] == 1e-6
        
        model.P = Constraint(model.i, model.j, model.k, rule = P_)
        
        model.del_component(model.S) 
        model.del_component(model.S_index)
        model.del_component(model.S_index_index_0) 
        
        def S_(model,i,j,k):
            if k == (model.nstages+1):
                return Constraint.Skip
            else:
                return model.snhc[i,j,k] == 1e-6

        model.S = Constraint(model.i, model.j, model.k, rule = S_)
        
        model.del_component(model.N) 
        model.del_component(model.N_index)
        model.del_component(model.N_index_index_0)
        
        def N_(model,i,j,k):
            if k == (model.nstages+1):
                return Constraint.Skip
            else:
                return model.y[i,j,k] == model.y1[i,j,k]+(model.pnhc[i,j,k]- model.snhc[i,j,k])

        model.N = Constraint(model.i, model.j, model.k, rule = N_) 
        
        model.del_component(model.Log_M_RPS_LPS) 
        model.del_component(model.Log_M_RPS_LPS_index)
        model.del_component(model.Log_M_RPS_LPS_index_index_0)
        
        def Log_M_RPS_LPS_(model,i,j,k):    
            c = ((self._rich_data.at[i,'F'])*((self._rich_data.at[i,'Cin'])-(self._rich_data.at[i,'Cout'])))
            c=(c)
            d=(model.L1[j]*(((self._lean_data.at[j,'Cout'])-((self._lean_data.at[j,'Cin'])))))
            if model.arex[i,j,k] == 1:
                if value(c) >=value(d):
                    return model.M[i,j,k] <= (model.L1[j]*(((self._lean_data.at[j,'Cout'])-((self._lean_data.at[j,'Cin'])))))*model.y[i,j,k]
                else:
                    return model.M[i,j,k] <= ((self._rich_data.at[i,'F'])*((self._rich_data.at[i,'Cin'])-(self._rich_data.at[i,'Cout'])))*model.y[i,j,k]
            else:
                return Constraint.Skip
    
        model.Log_M_RPS_LPS = Constraint(model.i, model.j, model.k, rule = Log_M_RPS_LPS_)
        
        #LOGICAL CONSTRAINT ON RICH SIDE COMPOSITION DIFFERENCE BETWEEN RPS(I) AND LPS(J)
        model.del_component(model.Log_DC_RPS_LPS_RS)
        model.del_component(model.Log_DC_RPS_LPS_RS_index)
        model.del_component(model.Log_DC_RPS_LPS_RS_index_index_0)
        
        def Log_DC_RPS_LPS_RS_(model,i,j,k):
            if model.arex[i,j,k] == 1:
                return model.dcin[i,j,k] <= model.cr[i,k] - model.cl[j,k]+ model.omega[i,j]*(1-model.y[i,j,k])
            else:
                return Constraint.Skip

        model.Log_DC_RPS_LPS_RS = Constraint(model.i, model.j, model.k, rule = Log_DC_RPS_LPS_RS_)

        model.del_component(model.Log_DC_RPS_LPS_RS1)
        model.del_component(model.Log_DC_RPS_LPS_RS1_index)
        model.del_component(model.Log_DC_RPS_LPS_RS1_index_index_0)        
        def Log_DC_RPS_LPS_RS1_(model,i,j,k):
            if model.arex[i,j,k] == 1:
                return model.dcin[i,j,k] >= model.cr[i,k] - model.cl[j,k]- model.omega[i,j]*(1-model.y[i,j,k])
            else:
                return Constraint.Skip
        model.Log_DC_RPS_LPS_RS1 = Constraint(model.i, model.j, model.k, rule = Log_DC_RPS_LPS_RS1_)

        #LOGICAL CONSTRAINT ON Lean SIDE COMPOSITION DIFFERENCE BETWEEN RPS(I) AND LPS(J)
        model.del_component(model.Log_DC_RPS_LPS_LS)
        model.del_component(model.Log_DC_RPS_LPS_LS_index)
        model.del_component(model.Log_DC_RPS_LPS_LS_index_index_0)
        def Log_DC_RPS_LPS_LS_(model,i,j,k):
            if model.arex[i,j,(k)] == 1:
                return model.dcout[i,j,(k+1)] <= model.cr[i,(k+1)] - model.cl[j,(k+1)]+\
                                                 model.omega[i,j]*(1-model.y[i,j,k])
            else:
                return Constraint.Skip
        model.Log_DC_RPS_LPS_LS = Constraint(model.i, model.j, model.k, rule = Log_DC_RPS_LPS_LS_)
        
        model.del_component(model.Log_DC_RPS_LPS_LS1)
        model.del_component(model.Log_DC_RPS_LPS_LS1_index)
        model.del_component(model.Log_DC_RPS_LPS_LS1_index_index_0)
        def Log_DC_RPS_LPS_LS1_(model,i,j,k):
            if model.arex[i,j,k] == 1:
                return model.dcout[i,j,(k+1)] >= model.cr[i,(k+1)] - model.cl[j,(k+1)] -\
                                     model.omega[i,j]*(1-model.y[i,j,k])
            else:
                return Constraint.Skip

        model.Log_DC_RPS_LPS_LS1 = Constraint(model.i, model.j, model.k, rule = Log_DC_RPS_LPS_LS1_)        
        
        model.del_component(model.KYTransferMass)
        model.del_component(model.KYTransferMass_index)
        model.del_component(model.KYTransferMass_index_index_0)
        def KYTransferMass_(model, i,j,k):
            if model.arex[i,j,k]==1:
                return model.kya[i,j,k]==model.kw*model.surfA[i,j,k]*model.surfAcor[i,j,k]*model.kwcor[i,j,k]
            else:
                return Constraint.Skip
    
        model.KYTransferMass = Constraint(model.i, model.j, model.k, rule = KYTransferMass_) 

        # Cut generation
        model.cuts = ConstraintList()
        
        print('cuts:',bin_cuts)
        if bin_cuts:
            for cutnum in bin_cuts:
                #print('cutnum:', cutnum)
                #print('cut_iter:', bin_cuts[cutnum])
                expr = 0
                for i in model.i:
                    for j in model.j:
                        for k in model.stages:
                            if bin_cuts[cutnum][i,j,k] == 1:
                                expr += (1 - model.y[i,j,k])
                                #print(expr)
                            else:
                                expr +=  model.y[i,j,k]
                                
                model.cuts.add(expr >= 1)
        
        if sym_cuts:
            for cutnum in sym_cuts:
                #print('cutnum sym:', cutnum)
                #print('cut_iter sym:', sym_cuts[cutnum])
                #print(type(sym_cuts[cutnum]))
                expr = 0
                if sym_cuts[cutnum]:
                    for i in model.i:
                        for j in model.j:
                            for k in model.stages:
                                if sym_cuts[cutnum][i,j,k] == 1:
                                    expr += (1 - model.y[i,j,k])
                                    #print(expr)
                                else:
                                    expr +=  model.y[i,j,k]
                                
                    model.cuts.add(expr >= 1)

        model.del_component(model.HeightColumn)
        model.del_component(model.HeightColumn_index)
        model.del_component(model.HeightColumn_index_index_0)
        def HeightColumn_(model,i,j,k):
            if model.arex[i,j,k] == 1:
                return model.height[i,j,k] == model.M[i,j,k]/(((model.kya[i,j,k]*numpy.pi/4*((model.dia[i,j,k]*model.diacor[i,j,k])**2))) *\
                                          (((model.dcin[i,j,k]*model.dcout[i,j,(k+1)])*\
                                           (model.dcin[i,j,k]+model.dcout[i,j,(k+1)])*0.5)**(0.33333)+1E-6)+1E-6)*model.y[i,j,k]
            else:
                return Constraint.Skip

        model.HeightColumn = Constraint(model.i, model.j, model.k, rule = HeightColumn_)
        
        #==================================================================================
        #   OBJECTIVE FUNCTION AND SOLVE STATEMENT
        #==================================================================================
        model.del_component(model.TACeqn)
        model.w = 0.000001
        def TACeq_(model):
            tac = 0
            for i in model.i:
                for j in model.j:
                    for k in model.k:
                        tac += model.AF*23805*((model.diacor[i,j,k]*model.dia[i,j,k])**0.57)*1.15*model.heightcor[i,j,k]*model.height[i,j,k]
                        tac += model.AF*numpy.pi*((model.dia[i,j,k]*model.diacor[i,j,k])**2)/4*model.height[i,j,k]*model.heightcor[i,j,k]*model.packcost[i,j,k]*model.packcostcor[i,j,k]
                        tac += model.fixcost*model.y[i,j,k]
                        tac += model.w*(model.pnhc[i,j,k]+model.snhc[i,j,k])
            for j in model.j:
                tac += model.L1[j]*model.AC[j]            
            return tac
        
        model.TACeqn = Objective(rule = TACeq_, sense = minimize)
        
        results, solversolved, globalsol  = solve_until_feas_MINLP_DICOPT(model)
        #==================================================================================
        #   POSTPROCESSING AND DISPLAY AND RETURN
        #==================================================================================
        print(results)
        if (results.solver.status == SolverStatus.ok) and (results.solver.termination_condition == TerminationCondition.optimal):
            model.height.pprint()
            model.M.pprint()
            model.avlean.pprint()
            model.L1.pprint()
            model.cr.pprint()
            model.cl.pprint()
            model.dcin.pprint()
            model.dcout.pprint()
            model.y.pprint()
            print(model.TACeqn())
        model.solversolved = solversolved
        model.globalsol = globalsol

        return model,results
    
