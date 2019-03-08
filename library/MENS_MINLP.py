#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Mon May 7 13:14:01 2018

MINLP model for Mass Exchanger Network Synthesis (MENS) in Pyomo

Made to be used as a part of the HybridStrategy module

@author: shortm
"""

from __future__ import division
from pyomo.environ import *
import pandas as pd
import os
import inspect
import numpy
from pyomo.opt import SolverFactory, ProblemFormat, TerminationCondition
from library.MassExchanger  import *

__author__ = "Michael Short"
__copyright__ = "Copyright 2018"
__credits__ = ["Michael Short, Lorenz T. Biegler, Isafiade, AJ."]
__license__ = "GPL-3"
__version__ = "0.9"
__maintainer__ =  "Michael Short"
__email__ = "shortm@andrew.cmu.edu"
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
    data = pd.read_csv(filename,index_col=0, header=0)
    return data

class MENS(object):
    def __init__(self, rich_data, lean_data, parameter_data, stream_properties, correction_factors=None):
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
            
        """
        #self.ip = SolverFactory('ipopt')

        self._rich_data = rich_data
        self._lean_data = lean_data
        self._correction_factors = None
        self._parameters = parameter_data
        self._stream_properties = stream_properties
        self.BARONsolved = False
        self.DICOPTsolved = False
        
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

    def solve_until_feas_NLP(self,m):
        """The solve function for the NLP.
        
        This function solves the NLP Pyomo model using ipopt. It has many try and except statements
        in order to try to use many different solver options to solve the problem. Ensures that the iterative
        procedure does not exit if an infeasible model is found and increases the likelihood that a feasible 
        solution is found.
        
        Args:
            m (pyomo model, concrete): the pyomo model of the MEN with all potential matches selected
            
        returns:
            results (solver results): returns the solved model and results from the solve.
            
        """
        solver= SolverFactory('ipopt')
        options={}
        try:
            results = solver.solve(m,tee=False, options=options)

            if (results.solver.status == SolverStatus.ok) and (results.solver.termination_condition == TerminationCondition.optimal):
                print("successfully solved")
            elif (results.solver.termination_condition == TerminationCondition.infeasible) or  (results.solver.termination_condition == TerminationCondition.maxIterations):
                print("First solve was infeasible")
                options1 = {}
                options1['mu_strategy'] = 'adaptive'
                results = solver.solve(m,tee=False, options=options1)
                if (results.solver.status == SolverStatus.ok) and (results.solver.termination_condition == TerminationCondition.optimal):
                    print("successfully solved")
                elif (results.solver.termination_condition == TerminationCondition.infeasible) or  (results.solver.termination_condition == TerminationCondition.maxIterations):
                    print("Second solve was infeasible")
                    options2 = {}
                    options2['mu_init'] = 1e-6
                    #CAN STILL ADD MORE OPTIONS SPECIFICALLY WITH ANOTHER LINEAR SOLVER
                    results = solver.solve(m,tee=False, options=options2) 
                    if (results.solver.status == SolverStatus.ok) and (results.solver.termination_condition == TerminationCondition.optimal):
                        print("successfully solved")
                    elif (results.solver.termination_condition == TerminationCondition.infeasible) or  (results.solver.termination_condition == TerminationCondition.maxIterations):
                        print("Second solve was infeasible")
                        options3 = {}
                        options3['mu_init'] = 1e-6
                        options['bound_push'] =1e-6
                        results = solver.solve(m,tee=False, options=options3)
                        if (results.solver.status == SolverStatus.ok) and (results.solver.termination_condition == TerminationCondition.optimal):
                            print("successfully solved")
                        #elif (results.solver.termination_condition == TerminationCondition.infeasible) or (results.solver.termination_condition == TerminationCondition.maxIterations):
                        #    solver = SolverFactory('./../../BARON/baron')
                        #    if (results.solver.status == SolverStatus.ok) and (results.solver.termination_condition == TerminationCondition.optimal):
                        #        print("successfully solved")
                        #    else:
                        #         print("BARON failed to find a feasible solution")
                        #    results = solver.solve(m,tee=False)
                        else:
                            print("Cannot determine cause of fault")
                            print("Solver Status:",  result.solver.status)
                            results = m
                    else:
                        print("Cannot determine cause of fault")
                        print("Solver Status: ",  result.solver.status)
                        results = m
                else:
                    print("Cannot determine cause of fault")
                    print("Solver Status: ",  result.solver.status)  
                    results = m                      
            else:
                print("Cannot determine cause of fault")
                print("Solver Status: ",  result.solver.status)
                results = m
        except:
            print("Something failed during the solve process!")
            try:
                options1 = {}
                options1['mu_strategy'] = 'adaptive'
                results = solver.solve(m,tee=False, options=options1)
                if (results.solver.status == SolverStatus.ok) and (results.solver.termination_condition == TerminationCondition.optimal):
                    print("successfully solved")
                elif (results.solver.termination_condition == TerminationCondition.infeasible) or (results.solver.termination_condition == TerminationCondition.maxIterations):
                    print("Second solve was infeasible")
                    options2 = {}
                    options2['mu_init'] = 1e-6
                    #options['bound_push'] =1e-5
                    results = solver.solve(m,tee=False, options=options2) 
                    if (results.solver.status == SolverStatus.ok) and (results.solver.termination_condition == TerminationCondition.optimal):
                        print("successfully solved")
                    elif (results.solver.termination_condition == TerminationCondition.infeasible) or (results.solver.termination_condition == TerminationCondition.maxIterations):
                        print("Second solve was infeasible")
                        options3 = {}
                        options3['mu_init'] = 1e-6
                        options3['bound_push'] =1e-6
                        results = solver.solve(m,tee=False, options=options3)
                        if (results.solver.status == SolverStatus.ok) and (results.solver.termination_condition == TerminationCondition.optimal):
                            print("successfully solved")
                        elif (results.solver.termination_condition == TerminationCondition.infeasible) or (results.solver.termination_condition == TerminationCondition.maxIterations):
                            solver = SolverFactory('baron')
                            results = solver.solve(m,tee=True)
                            if (results.solver.status == SolverStatus.ok) and (results.solver.termination_condition == TerminationCondition.optimal):
                                print("successfully solved")
                            else:
                                print("BARON failed to find a feasible solution")
                        else:
                            print("Cannot determine cause of fault")
                            print ("Solver Status: ",  result.solver.status)
                            results = m
                    else:
                        print("Cannot determine cause of fault")
                        print("Solver Status: ",  result.solver.status)
                        results = m
                else:
                    print("Cannot determine cause of fault")
                    print("Solver Status: ",  result.solver.status)
                    results = m
            except:
                results = m
        if (results.solver.termination_condition == TerminationCondition.infeasible) or (results.solver.termination_condition == TerminationCondition.maxIterations):  
            print("The initialization problem could not be solved")
            raise Exception("Could not find a valid model to initialize NLP")
        else:        
            return results

    #should possibly include more solvers, solver options and user options to choose exe location and solver
    def solve_until_feas_MINLP(self,m):
        """The solve function for the MINLP.
        
        This function solves the MINLP Pyomo model using Bonmin. It has many try and except statements
        in order to try to use many different solver options to solve the problem. Ensures that the iterative
        procedure does not exit if an infeasible model is found and increases the likelihood that a feasible 
        solution is found.
        
        Args:
            m (pyomo model, concrete): the pyomo model of the MEN with all potential matches selected
            
        returns:
            results (solver results): returns the solved model and results from the solve.
            
        """
        opt = SolverFactory('baron')
        options={}
        #options['bonmin.algorithm']='B-BB'
        #BARON SECTION
        print("==================ATTEMPTING TO SOLVE WITH BARON==========================")
        try:
            results = opt.solve(m,options = options,tee=False)
            if (results.solver.status == SolverStatus.ok) and (results.solver.termination_condition == TerminationCondition.optimal):
                print("successfully solved")
                self.BARONsolved = True
                
            elif (results.solver.termination_condition == TerminationCondition.infeasible) or  (results.solver.termination_condition == TerminationCondition.maxIterations):
                print("First solve was infeasible, solving with changed match options")
                options['EpsR']= 0.02
                results = opt.solve(m,options = options,tee=False)
                
                if (results.solver.status == SolverStatus.ok) and (results.solver.termination_condition == TerminationCondition.optimal):
                    print("successfully solved")
                    self.BARONsolved = True
                
                elif (results.solver.termination_condition == TerminationCondition.infeasible) or  (results.solver.termination_condition == TerminationCondition.maxIterations):
                    print("Second solve was infeasible, solving with changed match options")
                    options['EpsR']= 0.05
                    results = opt.solve(m,options = options,tee=False)
                    if (results.solver.status == SolverStatus.ok) and (results.solver.termination_condition == TerminationCondition.optimal):
                        print("successfully solved")
                        self.BARONsolved = True
                    
                    else:
                        print("Cannot determine cause of fault")
                        print("Solver Status: ",  result.solver.status) 
                else:
                    print("Cannot determine cause of fault")
                    print("Solver Status: ",  result.solver.status)     
            else:
                print("Cannot determine cause of fault")
                print("Solver Status: ",  result.solver.status)        
        except:
             print("Could not solve with BARON")
                    
                    
        #opt = SolverFactory('bonmin',executable='./../../../../cygwin64/home/Michael/Bonmin-1.8.6/build/bin/bonmin')
        #opt = SolverFactory('./../../Bonmin/build/bin/bonmin')
        '''if (results.solver.status == SolverStatus.ok) and (results.solver.termination_condition == TerminationCondition.optimal):
            self.BARONsolved = True    
            print("successfully solved with BARON")
        else:
            solver=SolverFactory('gams')
            options={}
            m1 = m
            print("Solving with DICOPT")
            try:
                results = solver.solve(m1,tee=True, solver = 'dicopt')

                if (results.solver.status == SolverStatus.ok) and (results.solver.termination_condition == TerminationCondition.optimal):
                    self.DICOPTsolved = True    
                    print("successfully solved with DICOPT")
            except:
                pass
        '''   
        print("BARONsolved:", self.BARONsolved)
        if self.BARONsolved == True:
            print("Solved using one of the global solvers")
        else:
            opt = SolverFactory('./../../../Bonmin/build/bin/bonmin')
            options={}
            options['bonmin.algorithm']='B-BB'
            
            #This can probably be greatly improved
            
            print("==================ATTEMPTING TO SOLVE WITH BONMIN==========================")
            try:
                results = opt.solve(m,options = options,tee=False)
                if (results.solver.status == SolverStatus.ok) and (results.solver.termination_condition == TerminationCondition.optimal):
                    print("successfully solved")
                elif (results.solver.termination_condition == TerminationCondition.infeasible) or  (results.solver.termination_condition == TerminationCondition.maxIterations):
                    print("First solve was infeasible, solving with changed match options")
                    options={}
                    options['mu_strategy'] = 'monotone'
                    options['mu_init'] = 1e-6
                    options['bonmin.algorithm']='B-BB'
                    options['bonmin.allowable_fraction_gap']= 0.05
                    results = opt.solve(m,options = options,tee=False)
                    
                    if (results.solver.status == SolverStatus.ok) and (results.solver.termination_condition == TerminationCondition.optimal):
                        print("successfully solved")
                        
                    elif (results.solver.termination_condition == TerminationCondition.infeasible) or  (results.solver.termination_condition == TerminationCondition.maxIterations):
                        print("First solve was infeasible, solving with changed match options")
                        options1={}
                        options1['mu_strategy'] = 'monotone'
                        options1['mu_init'] = 1e-5
                        options1['bound_relax_factor'] = 0
                        options1['bonmin.algorithm']='B-BB'
                        options1['bonmin.num_resolve_at_root']=5
                        results = opt.solve(m,options = options1,tee=False)
                        
                        if (results.solver.status == SolverStatus.ok) and (results.solver.termination_condition == TerminationCondition.optimal):
                            print("successfully solved")
                            
                        elif (results.solver.termination_condition == TerminationCondition.infeasible) or  (results.solver.termination_condition == TerminationCondition.maxIterations):
                            options2['mu_strategy'] = 'monotone'
                            options2['mu_init'] = 1e-5
                            options2['bound_relax_factor'] = 0
                            options2['bonmin.algorithm']='B-BB'
                            options2['bonmin.num_resolve_at_node']=5
                            results = opt.solve(m,options = options2,tee=False)
                            
                            if (results.solver.status == SolverStatus.ok) and (results.solver.termination_condition == TerminationCondition.optimal):
                                print("successfully solved")
                            elif (results.solver.termination_condition == TerminationCondition.infeasible) or  (results.solver.termination_condition == TerminationCondition.maxIterations):
                                options3['mu_strategy'] = 'monotone'
                                options3['mu_init'] = 1e-5
                                options3['bound_push'] = 1e-5
                                #options3['bound_relax_factor'] = 0
                                options3['bonmin.algorithm']='B-BB'
                                results = opt.solve(m, options = options3, tee=False)
                                if (results.solver.status == SolverStatus.ok) and (results.solver.termination_condition == TerminationCondition.optimal):
                                    print("successfully solved")
                                elif (results.solver.termination_condition == TerminationCondition.infeasible) or  (results.solver.termination_condition == TerminationCondition.maxIterations):
                                    options4['mu_strategy'] = 'monotone'
                                    options4['mu_init'] = 1e-5
                                    options4['bound_push'] = 1e-5
                                    #options3['bound_relax_factor'] = 0
                                    options4['bonmin.algorithm']='B-Hyb'
                                    options4['bonmin.pump_for_minlp']='yes'
                                    options4['pump_for_minlp.time_limit']=90
                                    options4['pump_for_minlp.solution_limit']= 7
                                    results = opt.solve(m, options = options4, tee=False)
                                    if(results.solver.status == SolverStatus.ok) and (results.solver.termination_condition == TerminationCondition.optimal):
                                        print("successfully solved")
                                    elif (results.solver.termination_condition == TerminationCondition.infeasible) or  (results.solver.termination_condition == TerminationCondition.maxIterations):
                                        options11['bonmin.algorithm']='B-OA'
                                        results = opt.solve(m, options = options4, tee=False)
                                        if(results.solver.status == SolverStatus.ok) and (results.solver.termination_condition == TerminationCondition.optimal):
                                            print("successfully solved")
                                        else:
                                            print("Cannot determine cause of fault")
                                            print("Solver Status: ",  result.solver.status)
                                    else:
                                        print("Cannot determine cause of fault")
                                        print("Solver Status: ",  result.solver.status)
                                else:
                                    print("Cannot determine cause of fault")
                                    print("Solver Status: ",  result.solver.status)
                            
                                    
                            else:
                                print("Cannot determine cause of fault")
                                print("Solver Status: ",  result.solver.status)
                    else:
                        print("Cannot determine cause of fault")
                        print("Solver Status: ",  result.solver.status)
                    #results = m    
                        
                else:
                    print("Cannot determine cause of fault")
                    print("Solver Status: ",  result.solver.status)
                    #results = m
    
            except:
                print("First try encountered an error") 
                results = opt.solve(m,options = options,tee=True)
        
        if (results.solver.termination_condition == TerminationCondition.infeasible) or (results.solver.termination_condition == TerminationCondition.maxIterations):  
            print("The MINLP problem could not be solved")
            #raise Exception("Could not find a valid model to continue iterations")
            return results
        else:        
            return results              
    #==========================================================
    #        FIRST NLP FOR INITIALIZATION OF MINLP
    #==========================================================
    def NLP_MENS_init(self, correction_factors=None):
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
        
        #print("self._correction_factors = ", self._correction_factors)
        

        #==============
        #   SCALARS
        #==============

        model.nrps = len(self._rich_data.index)
        model.nlut = len(self._lean_data.index)
        model.nstages = max(model.nlut,model.nrps)+1
        
        #==============
        #   SETS
        #==============
        #Rich streams
        model.i = Set(initialize=self._rich_data.index)

        #lean streams/utilities
        model.j = Set(initialize=self._lean_data.index)

        #Composition superstructure locations
        #will have number of stages = to largest of number of utilities or rps
        model.k = RangeSet((model.nstages+1))
        model.stages = RangeSet(model.nstages+1)

        #Stream Data
        model.data = Set(['Cin','Cout','F','cost','m'])
        model.stream_props = Set(['RHOG','RHOL'])
        model.parameters = Set(['kw','omega','AF','ACH','fixcost','EMAC','diameter','packcost','SurfA'])
        #================================
        #   SUPERSTRUCTURE GENERATION
        #================================
        #IDEA IS TO AUTOMATE THE SUPERSTRUCTURE GENERATION and include in init
        model.arex = {}
        model.arex['R1','L1',1] = 1
        model.arex['R1','L2',1] = 1
        model.arex['R2','L1',1] = 0
        model.arex['R2','L2',1] = 0

        model.arex['R1','L1',2] = 1
        model.arex['R1','L2',2] = 1
        model.arex['R2','L1',2] = 1 
        model.arex['R2','L2',2] = 1

        model.arex['R1','L1',3] = 0
        model.arex['R2','L2',3] = 1 
        model.arex['R1','L2',3] = 1
        model.arex['R2','L1',3] = 0
        
        model.arex['R1','L1',4] = 0
        model.arex['R2','L2',4] = 0 
        model.arex['R1','L2',4] = 0
        model.arex['R2','L1',4] = 0
        #Superstructure for SBS
        ckval = {}
        ckval[1] = 0.07
        ckval[2] = 0.051
        ckval[3] = 0.00087
        ckval[4] = 0.000052
        model.ck =Param(model.k, initialize = ckval)
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
        
        parameters = dict()
        for i in self._parameters.index:
            parameters[i] = self._parameters.at[i,'value']
        #BIG-M vale for Big-M constraint
        model.omega = Param (model.i,model.j, initialize=parameters['omega'])
        
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
        #aci={}
        #aci['L1']=117360
        #aci['L2']=176040
        model.AC = Param(model.j, initialize=aci)

        #=================
        #   VARIABLES
        #=================
        #These are actually fixed here to arex
        model.y = Param(model.i,model.j,model.k, initialize = model.arex)
        #relaxed binary
        model.y1 = Param(model.i,model.j,model.k, initialize = model.arex)
        
        #Variables for design of network
        #Composition at each interval boundary
        def cl_init(model,j,k):
            #return 0.0
            return abs((self._lean_data.at[j,'Cin']-self._lean_data.at[j,'Cout']))/2

        def cr_init(model,i,k):
            #return 0.0
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
        
        #Composition at each interval boundary before mixing
        #enables non sio-compositional mixing
        
        def crin_bounds(model,i,j,k):
            lb = 0.0
            #Rich_data.at[i,'Cout']
            ub = None
            return (lb,ub)

        def clin_bounds(model,i,j,k):
            lb = 0
            #Lean_data.at[j,'Cin']
            ub = None
            return (lb,ub)

        def clin_init(model,i,j,k):
            return self._lean_data.at[j,'Cin']
        def crin_init(model,i,j,k):
            return self._rich_data.at[i,'Cin']

        #THESE HERE SHOULD BE INCLUDED VIA AN OPTION TO THE USER AS TO WHETHER THEY WOULD LIKE TO INCLUDE 
        #NON-ISOCOMPOSITIONAL MIXING

        #model.crin = Var(model.i,model.j,model.k, initialize = crin_init, bounds=crin_bounds)
        #model.clin = Var(model.i,model.j,model.k, initialize = clin_init, bounds=clin_bounds)
        
        #Amount of lean stream utilized
        model.avlean = Var(model.j, initialize=0.3, within=NonNegativeReals)
        
        #Mass exchanged
        def m_init(model,i,j,k):
            if model.arex[i,j,k] ==1:
                c=(self._rich_data.at[i,'F']*(self._rich_data.at[i,'Cin']-self._rich_data.at[i,'Cout']))/2
                return c
            else:
                return 0.0
   
            #return float(Rich_data.at[i,'F']*(Rich_data.at[i,'Cin']-Rich_data.at[i,'Cout']))
        def m_bounds(model,i,j,k):
            if model.arex[i,j,k] ==1:
                return (0,(self._rich_data.at[i,'F']*(self._rich_data.at[i,'Cin']-self._rich_data.at[i,'Cout'])))
            else:
                return (0,0)

        model.M = Var(model.i,model.j,model.k, initialize=m_init, bounds = m_bounds)
        
        #rule for bounds of lean streams
        def L_bounds(model,j):
            if self._lean_data.at[j,'F']>0:
                #print("LEAN DATA:   ",self._lean_data.at[j,'F'])
                return (0.0001,self._lean_data.at[j,'F'])
        
            else:
                #print("LEAN DATA:   ",0,2)
                return (0.00001, 100)
            
        def L_init(model,j):
            if self._lean_data.at[j,'F']>0:
                #print("LEAN DATA:   ",self._lean_data.at[j,'F'])
                return self._lean_data.at[j,'F']/2
        
            else:
                return 0.1
        
        #Flowrate of lean used (J) all included
        #this should be changed - init
        model.L = Var(model.j, initialize=L_init,bounds = L_bounds)

        #   Flowrate of splits for non iso-compositional mixing
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

        #initialization rules
        def dcin_init_rule(model,i,j,k):
            return self._rich_data.at[i,'Cin']-self._lean_data.at[j,'Cin']

        def dcin_bounds_rule(model,i,j,k):
            if model.arex[i,j,k] ==1:
                return (model.EMAC,1)
            else:
                return (0,None)
    
        def dcout_init_rule(model,i,j,k):
            return self._rich_data.at[i,'Cin']-self._lean_data.at[j,'Cin']

        def dcout_bounds_rule(model,i,j,k):
            if k>=2:
                if model.arex[i,j,k-1] == 1:
                    return (model.EMAC,1)
                else:
                    return (0,None) 
            else:
                return (0,None) 
    
        #Composition difference/ driver for the mass exchange
        model.dcin = Var(model.i,model.j,model.k, initialize=dcin_init_rule,bounds=dcin_bounds_rule)
        model.dcout= Var(model.i,model.j,model.k, initialize=dcout_init_rule,bounds=dcout_bounds_rule)

        # non-isocompositional mixing flows in branches - Turn on with option
        def flv_init(model,i,j,k):
            if model.arex[i,j,k] ==1:
                return 0.1
            else:
                return 0.1 
        #model.flv = Var(model.i,model.j,model.k, initialize=flv_init, bounds = (0.00, None))
        
        #positive/negative tolerance
        model.pnhc=Var(model.i,model.j,model.k, initialize= 1e-6,within = NonNegativeReals)
        model.snhc=Var(model.i,model.j,model.k, initialize= 1e-6,within = NonNegativeReals)

        #mass transfer coefficient
        model.kya=Var(model.i,model.j,model.k, initialize = 1, bounds = (0.00, None))
        
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
                return (0.0,None)

        model.height =  Var(model.i,model.j,model.k, initialize=height_init,bounds=height_bounds)

        #===============================================================================
        # DEFINE SUPERSTRUCTURE
        #===============================================================================
        #Will want to automate this based on the stream data inputed
        # assignment of stream inlet compositions - Automate in future

        model.ckr_first = Param(model.i,model.k,initialize = 0.0,mutable=True)
        model.ckr_first['R1',1]=model.ck[1]
        model.ckr_first['R2',2]=model.ck[2]
        
        model.ckl_first = Param(model.j,model.k,initialize = 0.0,mutable=True)
        model.ckl_first['L1',3] = model.ck[3]
        model.ckl_first['L2',4] = model.ck[4]

        #model.ckr_first.pprint()
        #model.ckl_first.pprint()

        model.r_exist = Param(model.i,model.k,initialize = 0.0,mutable=True)

        model.r_exist['R1',1]=1
        model.r_exist['R1',2]=1
        model.r_exist['R1',3]=1
        model.r_exist['R1',4]=0

        model.r_exist['R2',1]=0
        model.r_exist['R2',2]=1
        model.r_exist['R2',3]=1
        model.r_exist['R2',4]=0

        model.l_exist = Param(model.j,model.k,initialize = 0.0,mutable=True)
        
        model.l_exist['L1',1]=1
        model.l_exist['L1',2]=1
        model.l_exist['L1',3]=0
        model.l_exist['L1',4]=0

        model.l_exist['L2',1]=1
        model.l_exist['L2',2]=1
        model.l_exist['L2',3]=1
        model.l_exist['L2',4]=0
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

        #EQUATIONS FOR NON_ISOCOMP MIXING
        #def FlowLV_(model,i,j,k):
        #    if arex[i,j,k] == 1:
        #        return model.flv[i,j,k] == (model.Flean[i,j,k]/model.Flrich[i,j,k])*((model.RHOG[i,j]/model.RHOL[j])**0.5)
        #    else:
        #        return Constraint.Skip
    
        #model.FlowLV = Constraint(model.i, model.j, model.k, rule = FlowLV_)   

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
                                           (model.dcin[i,j,k]+model.dcout[i,j,(k+1)])*0.5)**(0.33333)))
            else:
                return Constraint.Skip

        model.HeightColumn = Constraint(model.i, model.j, model.k, rule = HeightColumn_)
        
        #==================================================================================
        #   COBJECTIVE FUNCTION AND SOLVE STATEMENT
        #==================================================================================
        
        def TACeq_(model):
            tac = 0
            for i in model.i:
                for j in model.j:
                    for k in model.k:
                        tac += model.AF*23805*((model.diacor[i,j,k]*model.dia[i,j,k])**0.57)*1.15*model.heightcor[i,j,k]*model.height[i,j,k]*model.y[i,j,k]
                        tac += model.AF*numpy.pi*((model.dia[i,j,k]*model.diacor[i,j,k])**2)/4*model.height[i,j,k]*model.heightcor[i,j,k]*model.packcost[i,j,k]*model.packcostcor[i,j,k]
                        tac += model.fixcost*model.y[i,j,k]
            for j in model.j:
                tac += model.L[j]*model.AC[j]            
            return tac
        model.TACeqn = Objective(rule = TACeq_, sense = minimize)

        #Use this line for solving:
        # pyomo solve synheat.py --solver=./../../Couenne/build/bin/couenne
        #opt = SolverFactory('./../../Couenne/build/bin/couenne')
        #opt = SolverFactory('./../../BARON/baron')
        #opt = SolverFactory('bonmin')
        
        #options = {}
        #options['max_iter'] =20000

        #opt = SolverFactory('ipopt')
        #instance = model.create_instance()
        #model.write("MENS_nlp_nl.nl", format=ProblemFormat.nl)
        results= self.solve_until_feas_NLP(model)
        #results = opt.solve(model)
        #model.write(filename="MENS1", format = ProblemFormat.nl,io_options={"symbolic_solver_labels":True})
        #results.pprint
        #print(results)
        #model.display()
        #model.height.pprint()
        #model.M.pprint()
        #model.L.pprint()
        #model.cr.pprint()
        #model.cl.pprint()
        #model.dcin.pprint()
        #model.dcout.pprint()
        print("THIS IS THE END OF THE NLP INITIALIZATION")
        
        return model
    
    def MINLP_MENS_full(self, model, min_height_from_nlp=None, min_mass_ex_from_nlp=None):
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
                        print("no min height from NLP set, so it is assumed to be 0.1")
                        if model.height[i,j,k].value <= 0.1:
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
        
        model.del_component(model.y)
        model.del_component(model.y_index)
        model.del_component(model.y_index_index_0)
        
        model.y = Var(model.i,model.j,model.k, initialize = model.arex,within = Binary, bounds=(0,1))
        for i in model.i:
            for j in model.j:
                for k in model.k:        
                    if model.arex == 0:
                        model.y[i,j,k].fixed=True

        model.del_component(model.y1)
        model.del_component(model.y1_index)
        model.del_component(model.y1_index_index_0)
        
        model.y1 = Var(model.i,model.j,model.k, initialize = model.arex, within = NonNegativeReals, bounds=(0,1))
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

        #model.im = {}
        #for i in model.i:
        #    for j in model.j:
        #        for k in model.k:
        #            if model.arex[i,j,k] == 1:
        #                model.im [i,j,k] = model.M[i,j,k].value
        #            else:
        #                model.im [i,j,k] = 0
                        
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
                return (0.0001,self._lean_data.at[j,'F'])
        
            else:
                #print("LEAN DATA:   ",0,2)
                return (0.00001, 100)
        #model.L.pprint()
        l_init={}
        for j in model.j:
            print(j)
            l_init[j] = model.L[j].value
            #print(model.L[j].value)
        #print(l_init)
        #model.del_component(model.L)
        model.del_component(model.avlean)
        model.avlean = Var(model.j, initialize=0.3, within=NonNegativeReals)
        
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
        model.del_component(model.HeightColumn)
        model.del_component(model.HeightColumn_index)
        model.del_component(model.HeightColumn_index_index_0)
        def HeightColumn_(model,i,j,k):
            if model.arex[i,j,k] == 1:
                return model.height[i,j,k] == model.y[i,j,k]*model.M[i,j,k]/(((model.kya[i,j,k]*numpy.pi/4*((model.dia[i,j,k]*model.diacor[i,j,k])**2))) *\
                                          (((1e-8+model.dcin[i,j,k]*model.dcout[i,j,(k+1)])*\
                                           (model.dcin[i,j,k]+model.dcout[i,j,(k+1)])*0.5 + 1e-8)**(0.33333)+1e-8))
            else:
                return Constraint.Skip

        model.HeightColumn = Constraint(model.i, model.j, model.k, rule = HeightColumn_)
        
        #==================================================================================
        #   OBJECTIVE FUNCTION AND SOLVE STATEMENT
        #==================================================================================
        model.del_component(model.TACeqn)
        def TACeq_(model):
            tac = 0
            for i in model.i:
                for j in model.j:
                    for k in model.k:
                        tac += model.AF*23805*((model.diacor[i,j,k]*model.dia[i,j,k])**0.57)*1.15*model.heightcor[i,j,k]*model.height[i,j,k]
                        tac += model.AF*numpy.pi*((model.dia[i,j,k]*model.diacor[i,j,k])**2)/4*model.height[i,j,k]*model.heightcor[i,j,k]*model.packcost[i,j,k]*model.packcostcor[i,j,k]
                        tac += model.fixcost*model.y[i,j,k]
            for j in model.j:
                tac += model.L1[j]*model.AC[j]                    
            return tac
        model.TACeqn = Objective(rule = TACeq_, sense = minimize)
        
        options = {}
        #options['max_iter'] =20000
        #opt =SolverFactory('couenne',executable='./../../Couenne/build/bin/couenne')
        #opt = SolverFactory('./../../Couenne/build/bin/couenne')
        #opt = SolverFactory('baron',executable='./../../BARON/baron')
        #opt = SolverFactory('./../../Bonmin/build/bin/bonmin')
        #opt = SolverFactory('bonmin',executable='./../../../../cygwin64/home/Michael/Bonmin-1.8.6/build/bin/bonmin')
        #opt = SolverFactory('ipopt')
        #instance = model.create_instance()
        #model.pprint()
        #model.write("MENS_bin_nl.nl", format=ProblemFormat.nl)
        #results = opt.solve(model,options = options,tee=True)
        
        results = self.solve_until_feas_MINLP(model)
        #==================================================================================
        #   POSTPROCESSING AND DISPLAY AND RETURN
        #==================================================================================
        #model.write(filename="MENS1", format = ProblemFormat.nl,io_options={"symbolic_solver_labels":True})
        #results.pprint
        
        #display (model)
        #model.display()
        print(results)
        if (results.solver.status == SolverStatus.ok) and (results.solver.termination_condition == TerminationCondition.optimal):
            model.height.pprint()
            model.M.pprint()
            model.L1.pprint()
            model.cr.pprint()
            model.cl.pprint()
            model.dcin.pprint()
            model.dcout.pprint()
            model.y.pprint()
        model.baronsolved = False
        if self.BARONsolved == True:
            model.baronsolved = True
        #print(results)
        return model,results
    
