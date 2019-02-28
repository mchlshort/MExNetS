#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Fri Jun  1 10:35:31 2018

Individual Mass Exchanger optimization model in Pyomo. To be used in conjunction with the
MENS package developed. 

@author: shortm
"""

from __future__ import division
from math import pi
from pyomo.environ import *
from pyomo.dae import *
from pyomo.opt import SolverFactory, ProblemFormat, TerminationCondition, SolverStatus
import pandas as pd
import os
import inspect
import numpy as np
import sys

__author__ = "Michael Short"
__copyright__ = "Copyright 2018"
__credits__ = ["Michael Short, Lorenz T. Biegler, Isafiade, AJ."]
__license__ = "GPL-3"
__version__ = "0.9"
__maintainer__ =  "Michael Short"
__email__ = "shortm@andrew.cmu.edu"
__status__ = "Development"

class mass_exchanger(object):
    def __init__(self, rich_stream_name, lean_stream_name, rich_in_side, rich_out_side, flowrates, me_inits, stream_properties, ncp =3, nfe =100):
        # type: dict,dict, dict,
        """mass_exchanger class for individual packed column optimization from mass balances.

        This class aims to take in a mass balance for a mass tranfer unit with inputs of initial
        and destination concentrations of contaminants and the flowrates of the contaminated streams
        and output the optimized design based on the streams and contaminants found. Only does
        packed columns for now and also only one contaminant. Mean to be used as part of the MENS strategy.
        Uses the pyomo.dae to perform the orthogonal collocation on finite elements.

        input rich_in_side as a dictionary with the rich stream name and then the concentration and
        the lean stream name with conc

        Args:
            rich_stream_name (str): name of the stream from the MINLP
            lean_stream_name (str): name of the stream from the MINLP
            rich_in_side (dict): dictionary of rich stream name, concentration in, lean stream name, concentration in.
            rich_out_side (dict): the destination concs in same format as above
            flowrates (dict): flowrates of the streams in m3/hour
            me_inits (dict): obtained initializations from the previous iterations or MINLP.
            stream_properties (dict): physical properties of the streams
            ncp (int, optional):number of collocation points. Default is 3, must be an odd number for Radau roots (preferably under 10)
            nfe (int, optional): number of finite elements. Default is 100, must be a whole number.
            
        """
        #self.ip = SolverFactory('ipopt')

        #provide both streams concentration at this side of exchanger
        self.rich_in = rich_in_side
        self.rich_out = rich_out_side
        self.mass_flows = flowrates
        self.rich_stream_name = rich_stream_name
        self.lean_stream_name = lean_stream_name
        #Need to be checked for all init values
        self.ME_inits = me_inits
        self._stream_properties = stream_properties
        self.ncp = ncp
        self.nfe = nfe
        
    def solve_until_feas(self,m):
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
        #solver=SolverFactory('gams')
        options={}
        #results = solver.solve(m,tee=True, solver = 'conopt')
        try:
            solver=SolverFactory('gams')
            options={}
            m1 = m
            results = solver.solve(m1,tee=True, solver = 'conopt')
        except:
            print("conopt failed")
            print("CONOPT assumed unsuccessful... IPOPT it is")
            solver= SolverFactory('ipopt')
            options={}
            try:
                results = solver.solve(m,tee=False, options=options)
                #m.load(results)
    
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
                            #    results = solver.solve(m,tee=True)
                            else:
                                print("Cannot determine cause of fault")
                                print("Solver Status:",  results.solver.status)
                                #results = m
                        else:
                            print("Cannot determine cause of fault")
                            print("Solver Status: ",  results.solver.status)
                            #results = m
                    else:
                        print("Cannot determine cause of fault")
                        print("Solver Status: ",  results.solver.status)  
                        #results = m                      
                else:
                    print("Cannot determine cause of fault")
                    print("Solver Status: ",  results.solver.status)
                    #results = m
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
                            #elif (results.solver.termination_condition == TerminationCondition.infeasible) or (results.solver.termination_condition == TerminationCondition.maxIterations):
                            #    solver = SolverFactory('./../../BARON/baron')
                            #    results = solver.solve(m,tee=True)    
                            else:
                                print("Cannot determine cause of fault")
                                print ("Solver Status: ",  results.solver.status)
                                results = m
                        else:
                            print("Cannot determine cause of fault")
                            print("Solver Status: ",  results.solver.status)
                            results = m
                    else:
                        print("Cannot determine cause of fault")
                        print("Solver Status: ",  results.solver.status)
                        results = m
                except:
                    print("Something failed again during the solve")
                    try:
                        
                        options4 = {}
                        options4['mu_init'] = 1e-6
                        options4['bound_push'] =1e-6
                        results = solver.solve(m,tee=False, options=options3)
                        if (results.solver.status == SolverStatus.ok) and (results.solver.termination_condition == TerminationCondition.optimal):
                            print("successfully solved")
                        elif (results.solver.termination_condition == TerminationCondition.infeasible) or (results.solver.termination_condition == TerminationCondition.maxIterations):
                            print("Second solve was infeasible")
                            options4 = {}
                            options4['mu_init'] = 1e-6
                            #options['bound_push'] =1e-5
                            results = solver.solve(m,tee=False, options=options4) 
                            if (results.solver.status == SolverStatus.ok) and (results.solver.termination_condition == TerminationCondition.optimal):
                                print("successfully solved")
                            elif (results.solver.termination_condition == TerminationCondition.infeasible) or (results.solver.termination_condition == TerminationCondition.maxIterations):
                                print("Second solve was infeasible")
                                options4 = {}
                                options4['mu_init'] = 1e-5
                                options4['bound_push'] =1e-5
                                results = solver.solve(m,tee=False, options=options4)
                                if (results.solver.status == SolverStatus.ok) and (results.solver.termination_condition == TerminationCondition.optimal):
                                    print("successfully solved")
                                elif (results.solver.termination_condition == TerminationCondition.infeasible) or (results.solver.termination_condition == TerminationCondition.maxIterations):
                                    solver = SolverFactory('baron')
                                    results = solver.solve(m,tee=True)    
                                else:
                                    print("Cannot determine cause of fault")
                                    print ("Solver Status: ",  results.solver.status)
                                    results = "Failed epically"
                            else:
                                print("Cannot determine cause of fault")
                                print("Solver Status: ",  results.solver.status)
                                results = "Failed epically"
                        else:
                            print("Cannot determine cause of fault")
                            print("Solver Status: ",  results.solver.status)
                            results = "Failed epically"
                        
                    except:
                        try:
                            print("Something failed again again during the solve")
                            options4 = {}
                            options4['mu_init'] = 1e-5
                            options4['bound_push'] =1e-5
                            results = solver.solve(m,tee=False, options=options4)
                            if (results.solver.status == SolverStatus.ok) and (results.solver.termination_condition == TerminationCondition.optimal):
                                print("successfully solved")
                            else:
                                print("Cannot determine cause of fault")
                                print ("Solver Status: ",  results.solver.status)
                                results = "Failed epically"  
                        except:
                            results = "Failed epically"
                            pass

        print("This is to see why we are still solving with ipopt")
        
        if results == "Failed epically":
            print("CONOPT assumed unsuccessful... IPOPT it is")
            solver= SolverFactory('ipopt')
            options={}
            try:
                results = solver.solve(m,tee=False, options=options)
                #m.load(results)
    
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
                            #    results = solver.solve(m,tee=True)
                            else:
                                print("Cannot determine cause of fault")
                                print("Solver Status:",  results.solver.status)
                                results = m
                        else:
                            print("Cannot determine cause of fault")
                            print("Solver Status: ",  results.solver.status)
                            results = m
                    else:
                        print("Cannot determine cause of fault")
                        print("Solver Status: ",  results.solver.status)  
                        results = m                      
                else:
                    print("Cannot determine cause of fault")
                    print("Solver Status: ",  results.solver.status)
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
                            #elif (results.solver.termination_condition == TerminationCondition.infeasible) or (results.solver.termination_condition == TerminationCondition.maxIterations):
                            #    solver = SolverFactory('./../../BARON/baron')
                            #    results = solver.solve(m,tee=True)    
                            else:
                                print("Cannot determine cause of fault")
                                print ("Solver Status: ",  results.solver.status)
                                results = m
                        else:
                            print("Cannot determine cause of fault")
                            print("Solver Status: ",  results.solver.status)
                            results = m
                    else:
                        print("Cannot determine cause of fault")
                        print("Solver Status: ",  results.solver.status)
                        results = m
                except:
                    print("Something failed again during the solve")
                    try:
                        
                        options4 = {}
                        options4['mu_init'] = 1e-6
                        options4['bound_push'] =1e-6
                        results = solver.solve(m,tee=False, options=options3)
                        if (results.solver.status == SolverStatus.ok) and (results.solver.termination_condition == TerminationCondition.optimal):
                            print("successfully solved")
                        elif (results.solver.termination_condition == TerminationCondition.infeasible) or (results.solver.termination_condition == TerminationCondition.maxIterations):
                            print("Second solve was infeasible")
                            options4 = {}
                            options4['mu_init'] = 1e-6
                            #options['bound_push'] =1e-5
                            results = solver.solve(m,tee=False, options=options4) 
                            if (results.solver.status == SolverStatus.ok) and (results.solver.termination_condition == TerminationCondition.optimal):
                                print("successfully solved")
                            elif (results.solver.termination_condition == TerminationCondition.infeasible) or (results.solver.termination_condition == TerminationCondition.maxIterations):
                                print("Second solve was infeasible")
                                options4 = {}
                                options4['mu_init'] = 1e-5
                                options4['bound_push'] =1e-5
                                results = solver.solve(m,tee=False, options=options4)
                                if (results.solver.status == SolverStatus.ok) and (results.solver.termination_condition == TerminationCondition.optimal):
                                    print("successfully solved")
                                #elif (results.solver.termination_condition == TerminationCondition.infeasible) or (results.solver.termination_condition == TerminationCondition.maxIterations):
                                #    solver = SolverFactory('./../../BARON/baron')
                                #    results = solver.solve(m,tee=True)    
                                else:
                                    print("Cannot determine cause of fault")
                                    print ("Solver Status: ",  results.solver.status)
                                    results = m
                            else:
                                print("Cannot determine cause of fault")
                                print("Solver Status: ",  results.solver.status)
                                results = m
                        else:
                            print("Cannot determine cause of fault")
                            print("Solver Status: ",  results.solver.status)
                            results = m
                        
                    except:
                        try:
                            print("Something failed again again during the solve")
                            options4 = {}
                            options4['mu_init'] = 1e-5
                            options4['bound_push'] =1e-5
                            results = solver.solve(m,tee=False, options=options4)
                            if (results.solver.status == SolverStatus.ok) and (results.solver.termination_condition == TerminationCondition.optimal):
                                print("successfully solved")
                            else:
                                print("Cannot determine cause of fault")
                                print ("Solver Status: ",  results.solver.status)
                                results = "Failed epically"  
                        except:
                            results = m
                            results = "Failed epically"
        elif (results.solver.status == SolverStatus.ok) and (results.solver.termination_condition == TerminationCondition.locallyOptimal):
            print("successfully solved with CONOPT")
        elif (results.solver.status == SolverStatus.ok) and (results.solver.termination_condition == TerminationCondition.optimal):
            print("successfully solved using IPOPT")
        else:
            print("CONOPT assumed unsuccessful... IPOPT it is")
            solver= SolverFactory('ipopt')
            options={}
            try:
                results = solver.solve(m,tee=False, options=options)
                #m.load(results)
    
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
                            #    results = solver.solve(m,tee=True)
                            else:
                                print("Cannot determine cause of fault")
                                print("Solver Status:",  results.solver.status)
                                results = m
                        else:
                            print("Cannot determine cause of fault")
                            print("Solver Status: ",  results.solver.status)
                            results = m
                    else:
                        print("Cannot determine cause of fault")
                        print("Solver Status: ",  results.solver.status)  
                        results = m                      
                else:
                    print("Cannot determine cause of fault")
                    print("Solver Status: ",  results.solver.status)
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
                            #elif (results.solver.termination_condition == TerminationCondition.infeasible) or (results.solver.termination_condition == TerminationCondition.maxIterations):
                            #    solver = SolverFactory('./../../BARON/baron')
                            #    results = solver.solve(m,tee=True)    
                            else:
                                print("Cannot determine cause of fault")
                                print ("Solver Status: ",  results.solver.status)
                                results = m
                        else:
                            print("Cannot determine cause of fault")
                            print("Solver Status: ",  results.solver.status)
                            results = m
                    else:
                        print("Cannot determine cause of fault")
                        print("Solver Status: ",  results.solver.status)
                        results = m
                except:
                    print("Something failed again during the solve")
                    try:
                        
                        options4 = {}
                        options4['mu_init'] = 1e-6
                        options4['bound_push'] =1e-6
                        results = solver.solve(m,tee=False, options=options3)
                        if (results.solver.status == SolverStatus.ok) and (results.solver.termination_condition == TerminationCondition.optimal):
                            print("successfully solved")
                        elif (results.solver.termination_condition == TerminationCondition.infeasible) or (results.solver.termination_condition == TerminationCondition.maxIterations):
                            print("Second solve was infeasible")
                            options4 = {}
                            options4['mu_init'] = 1e-6
                            #options['bound_push'] =1e-5
                            results = solver.solve(m,tee=False, options=options4) 
                            if (results.solver.status == SolverStatus.ok) and (results.solver.termination_condition == TerminationCondition.optimal):
                                print("successfully solved")
                            elif (results.solver.termination_condition == TerminationCondition.infeasible) or (results.solver.termination_condition == TerminationCondition.maxIterations):
                                print("Second solve was infeasible")
                                options4 = {}
                                options4['mu_init'] = 1e-5
                                options4['bound_push'] =1e-5
                                results = solver.solve(m,tee=False, options=options4)
                                if (results.solver.status == SolverStatus.ok) and (results.solver.termination_condition == TerminationCondition.optimal):
                                    print("successfully solved")
                                #elif (results.solver.termination_condition == TerminationCondition.infeasible) or (results.solver.termination_condition == TerminationCondition.maxIterations):
                                #    solver = SolverFactory('./../../BARON/baron')
                                #    results = solver.solve(m,tee=True)    
                                else:
                                    print("Cannot determine cause of fault")
                                    print ("Solver Status: ",  results.solver.status)
                                    results = m
                            else:
                                print("Cannot determine cause of fault")
                                print("Solver Status: ",  results.solver.status)
                                results = m
                        else:
                            print("Cannot determine cause of fault")
                            print("Solver Status: ",  results.solver.status)
                            results = m
                        
                    except:
                        try:
                            print("Something failed again again during the solve")
                            options4 = {}
                            options4['mu_init'] = 1e-5
                            options4['bound_push'] =1e-5
                            results = solver.solve(m,tee=False, options=options4)
                            if (results.solver.status == SolverStatus.ok) and (results.solver.termination_condition == TerminationCondition.optimal):
                                print("successfully solved")
                            else:
                                print("Cannot determine cause of fault")
                                print ("Solver Status: ",  results.solver.status)
                                results = "Failed epically"  
                        except:
                            results = m
                            results = "Failed epically"
        return results
        
    def Construct_pyomo_model(self):
        """ Constructs the first basic pyomo model. Used to initialize further models
        
        Sets up the first few equations as well as pyomo dae in order to obtain initializations 
        for subsequent more detailed models.
        
        Args:
            None
            
        Returns:
            m (Concrete pyomo model): final solution.
            results (solver results): ipopt solver output.
            pre_solve_clone (clone of concrete model before solve statement): should only be used if solve failed
        """
        print("Setting up the 1st NLP subp-problem...")
        print("Hi")
        m = ConcreteModel()

        # way to move from unscaled time to scaled time
        m.tau = ContinuousSet(bounds=(0,1))
        m.h = Var(m.tau)
        m.height = Var(initialize = self.ME_inits["height"],within=NonNegativeReals)
        #=========================================
        #Parameters
        #=========================================
        #I will fix these here for now, but the plan is to load these from a seperate file
        #preferably for each component
        m.kw = Param(initialize = self.ME_inits["kw"])
        m.kwcor = Param(initialize = self.ME_inits["kwcor"])
        m.surfarea = Param(initialize =self.ME_inits["surfarea"])
        m.surfacor = Param(initialize = self.ME_inits["surfacor"])
        #Henry for mol SO2 per mol H2O = 0.0234, but in this eg, it is already inc
        m.henry = Param(initialize = 1)
        #print("mTHIS IS THE MASS_FLOWS", self.mass_flows)
        m.FlowRm = Param(initialize = self.mass_flows[self.rich_stream_name])
        m.FlowLm = Param (initialize = self.mass_flows[self.lean_stream_name])
        #=========================================
        #Variables
        #=========================================

        #flux of the contaminant from vapour
        m.flux =Var(m.tau)
        m.cRs = Var(m.tau,within = NonNegativeReals)
        m.cLs = Var(m.tau,within = NonNegativeReals)
        d = self.ME_inits["diameter"]*self.ME_inits["diacor"]
        m.diameter = Var(initialize =d, bounds = (0.0001, None))

        #DIFFERENTIAL VAR
        m.dheight = DerivativeVar(m.h)
        m.dCRdh= DerivativeVar(m.cRs, withrespectto=m.tau)
        m.dCLdh= DerivativeVar(m.cLs, withrespectto=m.tau)
        #========================================
        #CONSTRAINTS
        #========================================
        def TRateVap_(m, h):
            if h==0:
                return Constraint.Skip
            else: 
                return m.flux[h] == -m.kw*m.kwcor*m.surfarea*m.surfacor*pi/4*(m.diameter**2)*(m.cRs[h]-m.henry*m.cLs[h])
        m.TRateVap = Constraint(m.tau, rule = TRateVap_)

        #Differential Equations
        def ODECR_(m, h):
            if h==0:
                return Constraint.Skip
            else:
                return m.dCRdh[h] == m.flux[h]/m.FlowRm
        m.ODECR = Constraint(m.tau, rule = ODECR_)

        def ODECL_(m, h):
            if h==0:
                return Constraint.Skip
            else:
                return m.dCLdh[h] == m.flux[h]/m.FlowLm
        m.ODECL = Constraint(m.tau, rule = ODECL_)
        
        #Constraint to make the height not go from 0 to 1
        def ode_h_ (m,i):
            if i == 0:
                return Constraint.Skip
            else:
                return m.dheight[i] == m.height
        m.ode_h = Constraint(m.tau, rule= ode_h_)
        
        #initial conditions
        def _init1(m):
            return m.cRs[0] == self.rich_in[self.rich_stream_name]
        m.initcon1 = Constraint(rule=_init1)
        def _init2(m):
            return m.cRs[1] == self.rich_out[self.rich_stream_name]
        m.initcon2 = Constraint(rule=_init2)
        def _init3(m):
            return m.cLs[0] == self.rich_in[self.lean_stream_name]
        m.initcon3 = Constraint(rule=_init3)
        def _init4(m):
            return m.cLs[1] == self.rich_out[self.lean_stream_name]
        m.initcon4 = Constraint(rule=_init4)        
        def _init5(m):
            return m.h[0] == 0
        m.initcon5 = Constraint(rule=_init5)  

        #Need to do discretization before the objective
        discretizer = TransformationFactory('dae.collocation')
        discretizer.apply_to(m, nfe = self.nfe, ncp =self.ncp, scheme = 'LAGRANGE-RADAU')

        def Obj_(model):
            return 1

        m.Obj = Objective( rule = Obj_,sense=minimize)
        options = {}
        #options['mu_init'] = 1e-5
        #options['bound_push'] =1e-5
        #options['mu_strategy'] = 'adaptive'
        presolved_clone = m.clone()
        results = self.solve_until_feas(m)        
        #display(m)
        print(results)
        print("Hi")
        #q = m.FlowRm.value*(m.cRs[0].value-m.cRs[1].value)
        #print("mass exchanged R:  ", q )
        m.height.pprint()
        #q = m.FlowLm.value*(m.cLs[0].value-m.cLs[1].value)
        #print("mass exchanged L:  ", q )
        success_solve = bool

        print("results type: ",type(results))
        if results == 'failed epically':
            print("The exchanger could not be solved. This means that for this exchanger no model is stored. Could result in failure to produce correction factors.")
            success_solve = False
        elif not isinstance(results, str):
            if isinstance(results, pyomo.core.base.PyomoModel.ConcreteModel):
                print("model did not solve correctly, so it is skipped")
                success_solve = False
            elif (results.solver.status == SolverStatus.ok) and ((results.solver.termination_condition == TerminationCondition.optimal)):
                success_solve=True
            elif (results.solver.status == SolverStatus.ok) and (results.solver.termination_condition == TerminationCondition.locallyOptimal):
                success_solve=True
            else:
                #Should add way to deal with unsolved NLPs (increase elements?)
                print("NLP1 failed.")
                success_solve = False
        else:
            success_solve = False
        print("solve success = ", success_solve)     
                                
        return m, success_solve, presolved_clone 
        
    def Construct_pyomo_model_2(self, m, success_solve, m2):
        """ Constructs the second basic pyomo model. Used to initialize further models
        
        Builds on previous model by adding a few equations and variables in order to obtain initializations 
        for subsequent more detailed models.
        
        Args:
            m (Concrete pyomo model): model from Construct_pyomo_model_1
            success_solve (bool): passed from previous solve and tells the model whether it should provide 
                                    a different initial point as the previous model failed (from pre-solved clone above)
            m2 (clone of concrete pyomo model): clone of previous NLP model from before the solve statement. Used if 
            
        Returns:
                                            previous model did not solve correctly
            m (Concrete pyomo model): final solution.
            results (solver results): ipopt solver output.
            pre_solve_clone (clone of concrete model before solve statement): should only be used if solve failed
        
        """
        #=========================================
        #Variables from Previous NLP
        #=========================================
        #m.tau = ContinuousSet(bounds=(0,1))
        #m.h = Var(m.tau)
        
        #To get inits we clone the solved model
        old_solve_clone = m.clone()
        
        if success_solve:
            height_init=old_solve_clone.height.value
        else:
            height_init=m2.height.value
            
        m.del_component(m.height)
        m.height = Var(initialize = height_init,within=NonNegativeReals)
        
        
        flux_init = {}
        if success_solve:
            for h in m.h:
                flux_init[h]=old_solve_clone.flux[h].value
        else:
            for h in m.h:
                flux_init[h]=m2.flux[h].value
                
        m.del_component(m.flux)
        m.flux = Var(m.tau,initialize = flux_init)

        cRs_init = {}
        if success_solve:
            for h in m.h:
                cRs_init[h]=old_solve_clone.cRs[h].value 
        else:
            for h in m.h:
                cRs_init[h]=m2.cRs[h].value 
        #m.del_component(m.cRs)
        #m.cRs = Var(m.tau, initialize = cRs_init, within = NonNegativeReals)

        cLs_init = {}
        if success_solve:
            for h in m.h:
                cLs_init[h]=old_solve_clone.cLs[h].value  
        else:
            for h in m.h:
                cLs_init[h]=m2.cLs[h].value
            
        #m.del_component(m.cLs)
        #m.cLs = Var(m.tau, initialize = cLs_init, within = NonNegativeReals)
        
        if success_solve:
            diameter_init=old_solve_clone.diameter.value
        else:
            diameter_init=m2.diameter.value
        m.del_component(m.diameter)
        m.diameter = Var(initialize = diameter_init, bounds = (0.000001,None))

        #m.del_component(m.dheight)
        #m.dheight = DerivativeVar(m.h)
        #m.del_component(m.dCRdh)
        #m.dCRdh= DerivativeVar(m.cRs, withrespectto=m.tau)
        #m.del_component(m.dCLdh)
        #m.dCLdh= DerivativeVar(m.cLs, withrespectto=m.tau)

        #=========================================
        #New Parameters
        #=========================================
        print("Setting up the 2nd NLP subp-problem")
        m.ag = Param(initialize = 0.123)
        m.PartSizeCor = Param(initialize = 1)
        m.porosity = Param(initialize = 0.68)
        m.poroCor = Param(initialize = 1)

        rhog={}
        rhol={}
        m.surft={}
        m.visR={}
        m.visL={}
        count = 0
        for i in self._stream_properties.stream:
            if self._stream_properties.index[count]=='RHOG':
                rhog[i]=self._stream_properties.iloc[count]['value']
            if self._stream_properties.index[count]=='RHOL':
                rhol[i]=self._stream_properties.iloc[count]['value']
            if self._stream_properties.index[count]=='surften':
                m.surft[i]=self._stream_properties.iloc[count]['value']
            if self._stream_properties.index[count]=='visRich':
                m.visR[i]=self._stream_properties.iloc[count]['value']
            if self._stream_properties.index[count]=='vis':
                m.visL[i]=self._stream_properties.iloc[count]['value']
            count+=1
            
        m.visRich = Param(initialize = m.visR[self.rich_stream_name])
        m.visRich.pprint()
        m.de = Param(initialize=0.02)        
        m.AF = Param(initialize = 0.2)
        
        #These need to come from data
        m.RHOG = Param(initialize = rhog[self.rich_stream_name])
        m.RHOG.pprint()
        m.RHOL = Param(initialize = rhol[self.lean_stream_name])
        m.RHOL.pprint()
        #sys.exit()
        #Henry for mol SO2 per mol H2O = 0.0234, but in this eg, it is already inc
        #m.henry = Param(initialize = 1)
        #m.FlowRm = Param(initialize = self.mass_flows['R1'])
        #m.FlowLm = Param (initialize = self.mass_flows['L2'])
        
        FlowRVlat = self.mass_flows[self.rich_stream_name]/m.RHOG
        FlowLVlat = self.mass_flows[self.lean_stream_name]/m.RHOL

        m.FlowRVlat =Param(initialize=FlowRVlat)
        m.FlowLVlat =Param(initialize=FlowLVlat)
                
        m.FixCost = Param(initialize = 30000) # need to read from data
        m.PackCost = Param(initialize = (self.ME_inits["packcost"]*self.ME_inits["packcostcor"]))
        #=========================================
        #New Variables
        #=========================================

        def init_area(m):
            return pi/4*(m.diameter.value**2)
        
        m.area = Var(initialize=init_area,  bounds = (0,None))

        def init_koga(m):
            return m.kw*m.kwcor
        
        m.koga = Var(initialize = init_koga, bounds = (0.00000001,None))
        
        def init_velocityR(m):
            return (m.FlowRVlat/m.area.value)
        
        def init_velocityL(m):
            return (m.FlowLVlat/m.area.value)
        
        m.VelocityR = Var(initialize = init_velocityR, bounds = (0.000000001,200))
        m.VelocityL = Var(initialize = init_velocityL, bounds = (0.000000001,200))
        
        #========================================
        #OLD CONSTRAINTS
        #========================================
        #Differential Equations
        m.del_component(m.ODECR)
        def ODECR_(m, h):
            if h==0:
                return Constraint.Skip
            else:
                return m.dCRdh[h] == m.flux[h]/m.FlowRm
        m.ODECR = Constraint(m.tau, rule = ODECR_)

        m.del_component(m.ODECL)
        def ODECL_(m, h):
            if h==0:
                return Constraint.Skip
            else:
                return m.dCLdh[h] == m.flux[h]/m.FlowLm
        m.ODECL = Constraint(m.tau, rule = ODECL_)        
        
        m.del_component(m.ode_h)
        def ode_h_ (m,i):
            if i == 0:
                return Constraint.Skip
            else:
                return m.dheight[i] == m.height
        m.ode_h = Constraint(m.tau, rule= ode_h_)
        
        m.del_component(m.initcon1)
        def _init1(m):
            return m.cRs[0] == self.rich_in[self.rich_stream_name]
        m.initcon1 = Constraint(rule=_init1)
        m.del_component(m.initcon2)
        def _init2(m):
            return m.cRs[1] == self.rich_out[self.rich_stream_name]
        m.initcon2 = Constraint(rule=_init2)
        m.del_component(m.initcon3)
        def _init3(m):
            return m.cLs[0] == self.rich_in[self.lean_stream_name]
        m.initcon3 = Constraint(rule=_init3)
        m.del_component(m.initcon4)
        def _init4(m):
            return m.cLs[1] == self.rich_out[self.lean_stream_name]
        m.initcon4 = Constraint(rule=_init4) 
        m.del_component(m.initcon5)
        def _init5(m):
            return m.h[0] == 0
        m.initcon5 = Constraint(rule=_init5)  
        
        #========================================
        #MODIFIED CONSTRAINTS
        #========================================
        
        m.del_component(m.TRateVap)

        def TRateVap_(m, h):
            if h==0:
                return Constraint.Skip
            else:
                return m.flux[h] == -m.koga*m.area*m.surfarea*m.surfacor*\
                                    (m.cRs[h]-m.henry*m.cLs[h])
        m.TRateVap = Constraint(m.tau, rule = TRateVap_)
        
        #========================================
        #NEW CONSTRAINTS
        #========================================     
        def KogaEq_(m):
            return m.koga == (m.VelocityR)/(m.porosity*m.poroCor)*m.ag*(((m.de*m.PartSizeCor*m.VelocityR)/(m.porosity*m.poroCor*m.visRich))**(-0.25))*(0.7**(-0.677))*1
        
        m.KogaEq = Constraint(rule=KogaEq_)
        
        def VelocityREq_(m):
            return m.VelocityR*m.area == m.FlowRVlat
            
        m.VelocityREq = Constraint(rule=VelocityREq_)

        def VelocityLEq_(m):
            return m.VelocityL*m.area == m.FlowLVlat
            
        m.VelocityLEq = Constraint(rule=VelocityLEq_)

        def AreaEq_(m):
            return m.area == pi/4*(m.diameter**2)
            
        m.AreaEq = Constraint(rule=AreaEq_)

        def loverdup_(m):
            return m.height <= 250*m.diameter
            
        m.loverdup = Constraint(rule=loverdup_)
        
        def loverdlo_(m):
            return m.height >= 0.5*m.diameter
            
        m.loverdlo = Constraint(rule=loverdlo_)

        #========================================
        # OBJECTIVE and SOLVE
        #========================================             
        #m.del_component(m.Obj)
        def Obj1_(m):
            return m.AF*23805*(m.diameter**0.57)*1.15*m.height + m.AF*pi*(m.diameter**2)/4*m.height*m.PackCost
        #m.AF*23805*(m.diameter**0.57)*1.15*m.height + m.AF*pi*(m.diameter**2)/4*m.height*m.PackCost

        m.Obj1 = Objective(rule = Obj1_,sense=minimize)
        m.Obj.deactivate()
        m.Obj1.activate()
        
        presolved_clone = m.clone()
        results = self.solve_until_feas(m)
        #========================================
        # POST PROCESSING AND PRINTING
        #========================================         
        
        #instance = m.create_instance()
        #results1 = solver.solve(m,tee=False)
        #display(m)
        q= m.AF*23805*(m.diameter.value**0.57)*1.15*m.height.value
        w=m.AF*pi*(m.diameter.value**2)/4*m.height.value*m.PackCost
        #print(m.FixCost, "    ", q, "   ", w)
        #print(m.CapCost.value)
        #m.CapCost.pprint()
        #m.height.pprint()
        #m.diameter.pprint()
        #m.VelocityL.pprint()
        #m.VelocityR.pprint()
        #m.koga.pprint()
        
        #m.display()
        print(results)
        #results.pprint
        #q = m.FlowRm.value*(m.cRs[0].value-m.cRs[1].value)
        #print("mass exchanged R:  ", q )
        #q = m.FlowLm.value*(m.cLs[0].value-m.cLs[1].value)
        #print("mass exchanged L:  ", q )
        success_solve = bool

        print("results type: ",type(results))
        if results == 'failed epically':
            print("The exchanger could not be solved. This means that for this exchanger no model is stored. Could result in failure to produce correction factors.")
            success_solve = False
        elif not isinstance(results, str):
            if isinstance(results, pyomo.core.base.PyomoModel.ConcreteModel):
                print("model did not solve correctly, so it is skipped")
                success_solve = False
            elif (results.solver.status == SolverStatus.ok) and (results.solver.termination_condition == TerminationCondition.optimal):
                success_solve=True
            elif (results.solver.status == SolverStatus.ok) and (results.solver.termination_condition == TerminationCondition.locallyOptimal):
                success_solve=True
            else:
                #Should add way to deal with unsolved NLPs (increase elements?)
                print("NLP1 failed.")
                success_solve = False
        else:
            success_solve = False
        print("solve success = ", success_solve)     
                                
        return m, success_solve, presolved_clone
    
    def Construct_pyomo_model_3(self,m, success_solve, m2):
        """ Constructs the 3rd pyomo model of 5. Used to initialize further models.
        
        Builds on previous model by adding a few equations and variables in order to obtain initializations 
        for subsequent more detailed models.
        
        Args:
            m (Concrete pyomo model): model from Construct_pyomo_model_2
            success_solve (bool): passed from previous solve and tells the model whether it should provide 
                                    a different initial point as the previous model failed (from pre-solved clone above)
            m2 (clone of concrete pyomo model): clone of previous NLP model from before the solve statement. Used if 
                                            previous model did not solve correctly
            
        Returns:
            m (Concrete pyomo model): final solution.
            results (solver results): ipopt solver output.
            pre_solve_clone (clone of concrete model before solve statement): should only be used if solve failed
        
        """
        print("Setting up the 3rd NLP subp-problem, deet in GAMS")
        #=========================================
        #Variables from Previous NLP
        #=========================================
        #To get inits we clone the solved model
        old_solve_clone = m.clone()
        
        
        if success_solve:
            height_init=old_solve_clone.height.value
        else:
            height_init=m2.height.value
            
        m.del_component(m.height)
        m.height = Var(initialize = height_init,bounds = (0.0000001,None))
        
        
        flux_init = {}
        if success_solve:
            for h in m.h:
                flux_init[h]=old_solve_clone.flux[h].value
        else:
            for h in m.h:
                flux_init[h]=m2.flux[h].value
                
        m.del_component(m.flux)
        m.flux = Var(m.tau,initialize = flux_init)

        cRs_init = {}
        if success_solve:
            for h in m.h:
                cRs_init[h]=old_solve_clone.cRs[h].value 
        else:
            for h in m.h:
                cRs_init[h]=m2.cRs[h].value 
        #m.del_component(m.cRs)
        #m.cRs = Var(m.tau, initialize = cRs_init, within = NonNegativeReals)

        cLs_init = {}
        if success_solve:
            for h in m.h:
                cLs_init[h]=old_solve_clone.cLs[h].value  
        else:
            for h in m.h:
                cLs_init[h]=m2.cLs[h].value
            
        #m.del_component(m.cLs)
        #m.cLs = Var(m.tau, initialize = cLs_init, within = NonNegativeReals)
        
        if success_solve:
            diameter_init=old_solve_clone.diameter.value
        else:
            diameter_init=m2.diameter.value
        m.del_component(m.diameter)
        m.diameter = Var(initialize = diameter_init, bounds = (0.000001,None))

        #m.del_component(m.dheight)
        #m.dheight = DerivativeVar(m.h)
        #m.del_component(m.dCRdh)
        #m.dCRdh= DerivativeVar(m.cRs, withrespectto=m.tau)
        #m.del_component(m.dCLdh)
        #m.dCLdh= DerivativeVar(m.cLs, withrespectto=m.tau)
        area_init = 0
        if success_solve:
            area_init=old_solve_clone.area.value
        else:
            area_init=m2.area.value
            
        m.del_component(m.area)
        m.area = Var(initialize = area_init, within = NonNegativeReals)

        koga_init = 0
        if success_solve:
            koga_init=old_solve_clone.koga.value
        else:
            koga_init=m2.koga.value
            
        m.del_component(m.koga)
        m.koga = Var(initialize = koga_init, bounds = (0.0000000001,None))
        
        VelocityR_init = 0
        if success_solve:
            VelocityR_init=old_solve_clone.VelocityR.value
        else:
            VelocityR_init=m2.VelocityR.value
            
        VelocityR_init=m.VelocityR.value
        m.del_component(m.VelocityR)
        m.VelocityR = Var(initialize =VelocityR_init, bounds = (0.0000000000001,200))
        
        VelocityL_init = 0
        if success_solve:
            VelocityL_init=old_solve_clone.VelocityL.value
        else:
            VelocityL_init=m2.VelocityL.value
        
        m.del_component(m.VelocityL)
        m.VelocityL = Var(initialize = VelocityL_init, bounds = (0.000000000001,200)) 
       
        #=========================================
        #NEW Parameters
        #=========================================        
        
        m.vis = Param(initialize= m.visL[self.lean_stream_name])
        
        #=========================================
        #NEW Variables
        #=========================================
        m.packfact = Var(initialize=120, bounds = (20.0,100000))
        
        ReLini = m.RHOL*m.VelocityL.value*0.05/m.vis.value
        ReGini = m.RHOG*m.VelocityR.value*0.05/m.visRich.value
        
        m.ReL = Var(initialize = ReLini,bounds = (0.000000001,100000))
        m.ReG = Var(initialize = ReGini,bounds = (0.000000001,100000))
                
        Floodini = 249.089/0.3048*0.12*((m.packfact.value*0.3048)**0.7)
        FloodActini = 22.3*(m.packfact.value)*(m.vis**0.2)*((m.VelocityR.value)**2)*((10**(0.035*m.VelocityL.value))/(9.81*m.RHOG))

        m.Flood= Var(initialize = Floodini, bounds = (0.000000001,10000000))
        m.FloodAct= Var(initialize = FloodActini, bounds = (0.000000001,10000000))

        #========================================
        #OLD CONSTRAINTS
        #========================================
        #Differential Equations
        m.del_component(m.ODECR)
        def ODECR_(m, h):
            if h==0:
                return Constraint.Skip
            else:
                return m.dCRdh[h] == m.flux[h]/m.FlowRm
        m.ODECR = Constraint(m.tau, rule = ODECR_)

        m.del_component(m.ODECL)
        def ODECL_(m, h):
            if h==0:
                return Constraint.Skip
            else:
                return m.dCLdh[h] == m.flux[h]/m.FlowLm
        m.ODECL = Constraint(m.tau, rule = ODECL_)        
        
        m.del_component(m.ode_h)
        def ode_h_ (m,i):
            if i == 0:
                return Constraint.Skip
            else:
                return m.dheight[i] == m.height
        m.ode_h = Constraint(m.tau, rule= ode_h_)
        
        #m.del_component(m.initcon)
        def _init(m):
            yield m.cRs[0] == self.rich_in[self.rich_stream_name]
            yield m.cRs[1] == self.rich_out[self.rich_stream_name]
            yield m.cLs[0] == self.rich_in[self.lean_stream_name]
            yield m.cLs[1] == self.rich_out[self.lean_stream_name]
            yield m.h[0] == 0
        #m.initcon = ConstraintList(rule=_init)  
        
        m.del_component(m.KogaEq)
        def KogaEq_(m):
            return m.koga == (m.VelocityR)/(m.porosity*m.poroCor)*m.ag*(((m.de*m.PartSizeCor*m.VelocityR)/(m.porosity*m.poroCor*m.visRich))**(-0.25))*(0.7**(-0.677))*1
        
        m.KogaEq = Constraint(rule=KogaEq_)
        
        m.del_component(m.VelocityREq)
        def VelocityREq_(m):
            return m.VelocityR*m.area == m.FlowRVlat
            
        m.VelocityREq = Constraint(rule=VelocityREq_)

        m.del_component(m.VelocityLEq)
        def VelocityLEq_(m):
            return m.VelocityL*m.area == m.FlowLVlat
            
        m.VelocityLEq = Constraint(rule=VelocityLEq_)

        m.del_component(m.AreaEq)
        def AreaEq_(m):
            return m.area == pi/4*(m.diameter**2)
            
        m.AreaEq = Constraint(rule=AreaEq_)
        
        m.del_component(m.TRateVap)

        def TRateVap_(m, h):
            if h==0:
                return Constraint.Skip
            else:
                return m.flux[h] == -m.koga*m.area*m.surfarea*m.surfacor*\
                                    (m.cRs[h]-m.henry*m.cLs[h])
                                    
        m.TRateVap = Constraint(m.tau, rule = TRateVap_)
        #========================================
        #MODIFIED CONSTRAINTS
        #========================================
            
        m.del_component(m.loverdup)        
        def loverdup_(m):
            return m.height <= 50*m.diameter
            
        m.loverdup = Constraint(rule=loverdup_)
        
        m.del_component(m.loverdlo)
        def loverdlo_(m):
            return m.height >=1.5*m.diameter
            
        m.loverdlo = Constraint(rule=loverdlo_)
         
        #========================================
        #NEW CONSTRAINTS
        #========================================

        #Flooding equations
        def Flood1_(m):
            return m.Flood == 249.089/0.3048*0.12*((m.packfact*0.3048)**0.7)  
        m.Flood1 = Constraint(rule = Flood1_) 
        
        def Flood2_(m):
            return m.FloodAct == (94*((m.ReL**1.11)/(m.ReG**1.8))+4.4)*6*(1-m.porosity*m.poroCor)/(m.de*m.PartSizeCor*((m.porosity*m.poroCor)**3))*m.RHOG*(m.VelocityR**2)
                                                                               
        m.Flood2 = Constraint(rule = Flood2_)
        
        def Flood3_(m):
            return m.Flood >=  m.FloodAct
        
        m.Flood3 = Constraint(rule = Flood3_) 
        
        def ReynoldsG_(m):
            return m.ReG ==  m.RHOG*m.VelocityR*m.de*m.PartSizeCor/(m.visRich);
        m.ReynoldsG = Constraint(rule = ReynoldsG_) 
        
        def ReynoldsL_(m):
            return m.ReL ==  m.RHOL*m.VelocityL*m.de*m.PartSizeCor/(m.vis);
        m.ReynoldsL = Constraint(rule = ReynoldsL_) 
        
        #========================================
        # OBJECTIVE and SOLVE
        #========================================  
        m.del_component(m.Obj1)
        m.del_component(m.Obj)
        def Obj2_(m):
            return m.AF*23805*(m.diameter**0.57)*1.15*m.height + m.AF*pi*(m.diameter**2)/4*m.height*m.PackCost
        #m.AF*23805*(m.diameter**0.57)*1.15*m.height + m.AF*pi*(m.diameter**2)/4*m.height*m.PackCost
                                
        m.Obj2 = Objective(rule = Obj2_,sense=minimize)
        #m.Obj1.deactivate()
        #m.Obj2.activate()   
        #solver = SolverFactory('./../../BARON/baron')
        presolve_clone = m.clone()
        results = self.solve_until_feas(m)
        
        #========================================
        # POST PROCESSING AND PRINTING
        #======================================== 
        print(results)
        #display(m)
        #results = solver_manager.solve(m,opt=solver)
        #q= m.AF*23805*(m.diameter**0.57)*1.15*m.height()
        #w=m.AF*pi*(m.diameter()**2)/4*m.height()*m.PackCost
        #print(m.FixCost, "    ",q,"   ", w)
        #m.CapCost.pprint()
        m.height.pprint()
        #m.heightp.pprint()
        #m.diameter.pprint()
        #m.ReG.pprint()
        #m.ReL.pprint()
        #m.Flood.pprint()
        #m.FloodAct.pprint()
        #m.VelocityR.pprint()
        #m.VelocityL.pprint()
        #m.packfact.pprint()
        #m.koga.pprint()
        #m.display()
        #print(results)
        #results.pprint
        #q = m.FlowRm.value*(m.cRs[0].value-m.cRs[1].value)
        #print("mass exchanged R:  ", q )
        #q = m.FlowLm.value*(m.cLs[0].value-m.cLs[1].value)
        #print("mass exchanged L:  ", q )
        success_solve = bool

        print("results type: ",type(results))
        if results == 'failed epically':
            print("The exchanger could not be solved. This means that for this exchanger no model is stored. Could result in failure to produce correction factors.")
            success_solve = False
        elif not isinstance(results, str):
            if isinstance(results, pyomo.core.base.PyomoModel.ConcreteModel):
                print("model did not solve correctly, so it is skipped")
                success_solve = False
            elif (results.solver.status == SolverStatus.ok) and (results.solver.termination_condition == TerminationCondition.optimal):
                success_solve=True
            elif (results.solver.status == SolverStatus.ok) and (results.solver.termination_condition == TerminationCondition.locallyOptimal):
                success_solve=True
            else:
                #Should add way to deal with unsolved NLPs (increase elements?)
                print("NLP1 failed.")
                success_solve = False
        else:
            success_solve = False
        print("solve success = ", success_solve)     
                                
        return m, success_solve, presolve_clone
       
    def Construct_pyomo_model_4(self,m, success_solve, m2):
        """ Constructs the 4th pyomo model of 5. Used to initialize further models.
        
        Builds on previous model by adding a few equations and variables in order to obtain initializations 
        for subsequent more detailed models.
        
       Args:
            m (Concrete pyomo model): model from Construct_pyomo_model_3
            success_solve (bool): passed from previous solve and tells the model whether it should provide 
                                    a different initial point as the previous model failed (from pre-solved clone above)
            m2 (clone of concrete pyomo model): clone of previous NLP model from before the solve statement. Used if 
                                            previous model did not solve correctly
            
        Returns:
            m (Concrete pyomo model): final solution.
            results (solver results): ipopt solver output.
            pre_solve_clone (clone of concrete model before solve statement): should only be used if solve failed
        
        """                
        print("Setting up the 4th NLP subp-problem, final in GAMS")
        
        #=========================================
        #Variables from Previous NLP
        #=========================================
        
        old_solve_clone = m.clone()
        
        if success_solve:
            print("This is the test")
            print(old_solve_clone.height.value)
            print(m.height.value)
            height_init=old_solve_clone.height.value
        else:
            height_init=m2.height.value
            
        m.del_component(m.height)
        m.height = Var(initialize = height_init,bounds = (0.0000001,None))
        
        
        flux_init = {}
        if success_solve:
            for h in m.h:
                flux_init[h]=old_solve_clone.flux[h].value
        else:
            for h in m.h:
                flux_init[h]=m2.flux[h].value
                
        m.del_component(m.flux)
        m.flux = Var(m.tau,initialize = flux_init)

        cRs_init = {}
        if success_solve:
            for h in m.h:
                cRs_init[h]=old_solve_clone.cRs[h].value 
        else:
            for h in m.h:
                cRs_init[h]=m2.cRs[h].value 
        #m.del_component(m.cRs)
        #m.cRs = Var(m.tau, initialize = cRs_init, within = NonNegativeReals)

        cLs_init = {}
        if success_solve:
            for h in m.h:
                cLs_init[h]=old_solve_clone.cLs[h].value  
        else:
            for h in m.h:
                cLs_init[h]=m2.cLs[h].value
            
        #m.del_component(m.cLs)
        #m.cLs = Var(m.tau, initialize = cLs_init, within = NonNegativeReals)
        
        if success_solve:
            diameter_init=old_solve_clone.diameter.value
        else:
            diameter_init=m2.diameter.value
        m.del_component(m.diameter)
        m.diameter = Var(initialize = diameter_init, bounds = (0.0000001, None))

        #m.del_component(m.dheight)
        #m.dheight = DerivativeVar(m.h)
        #m.del_component(m.dCRdh)
        #m.dCRdh= DerivativeVar(m.cRs, withrespectto=m.tau)
        #m.del_component(m.dCLdh)
        #m.dCLdh= DerivativeVar(m.cLs, withrespectto=m.tau)
        area_init = 0
        if success_solve:
            area_init=old_solve_clone.area.value
        else:
            area_init=m2.area.value
            
        m.del_component(m.area)
        m.area = Var(initialize = area_init, within = NonNegativeReals)

        koga_init = 0
        if success_solve:
            koga_init=old_solve_clone.koga.value
        else:
            koga_init=m2.koga.value
            
        m.del_component(m.koga)
        m.koga = Var(initialize = koga_init, within = NonNegativeReals)
        
        VelocityR_init = 0
        if success_solve:
            VelocityR_init=old_solve_clone.VelocityR.value
        else:
            VelocityR_init=m2.VelocityR.value
            
        #VelocityR_init=m.VelocityR.value
        print("The velocityR init is :", VelocityR_init )
        m.del_component(m.VelocityR)
        m.VelocityR = Var(initialize = VelocityR_init, bounds =(0.0000001, None))
        
        VelocityL_init = 0
        if success_solve:
            VelocityL_init=old_solve_clone.VelocityL.value
        else:
            VelocityL_init=m2.VelocityL.value
        
        m.del_component(m.VelocityL)
        m.VelocityL = Var(initialize = VelocityL_init,bounds =(0.0000001, None)) 
        
        ReL_init=0
        if success_solve:
            ReL_init=old_solve_clone.ReL.value
        else:
            ReL_init=m2.ReL.value
            
        m.del_component(m.ReL)
        m.ReL = Var(initialize = ReL_init, within = NonNegativeReals) 
        
        ReG_init=0
        if success_solve:
            ReG_init=old_solve_clone.ReG.value
        else:
            ReG_init=m2.ReG.value

        m.del_component(m.ReG)
        m.ReG = Var(initialize = ReG_init, within = NonNegativeReals)

        Flood_init=0
        if success_solve:
            Flood_init=old_solve_clone.Flood.value
        else:
            Flood_init=m2.Flood.value

        m.del_component(m.Flood)
        m.Flood = Var(initialize = Flood_init, within = NonNegativeReals)

        FloodAct_init=0
        if success_solve:
            FloodAct_init=old_solve_clone.FloodAct.value
        else:
            FloodAct_init=m2.FloodAct.value

        m.del_component(m.FloodAct)
        m.FloodAct = Var(initialize = FloodAct_init, within = NonNegativeReals)
        
        packfact_init=0
        if success_solve:
            packfact_init=old_solve_clone.packfact.value
        else:
            packfact_init=m2.packfact.value
            
        m.del_component(m.packfact)
        m.packfact = Var(initialize = packfact_init, bounds = (0, None))

        #=========================================
        #NEW Parameters
        #=========================================   

        m.ap = Param(initialize =(self.ME_inits["surfarea"]*self.ME_inits["surfacor"]))
        m.surften = Param(initialize = m.surft[self.lean_stream_name])

        #=========================================
        #New Variables
        #=========================================

        p = m.ap.value*m.surfacor.value*(1-exp(-1.45*((0.075/m.surften.value)**0.75)*((m.RHOL.value*m.VelocityR.value/(m.vis.value*m.ap.value))**0.1)*((m.ap.value*(m.VelocityR.value**2)/9.81)**(-0.05))*((m.RHOL.value*(m.VelocityR.value**2)/(m.ap.value*m.surften.value))**0.2)))
        p = m.ap.value*m.surfacor.value*(1-exp(-1.45*((0.075/m.surften.value)**0.75)*((m.RHOL.value*m.VelocityL.value/(m.vis.value*m.ap.value))**0.1)*(((m.ap.value*((m.RHOL.value*m.VelocityL.value)**2))/((m.RHOL.value**2)*9.81))**(-0.05))*((((m.RHOL.value*m.VelocityL.value)**2)/((m.RHOL.value**2)*m.ap.value*m.surften.value))**0.2)))
        print("Ai initial value=", p)
        m.ai = Var(initialize = p, within = NonNegativeReals)
        
        #========================================
        #OLD CONSTRAINTS
        #========================================
        #Differential Equations
        m.del_component(m.ODECR)
        def ODECR_(m, h):
            if h==0:
                return Constraint.Skip
            else:
                return m.dCRdh[h] == m.flux[h]/m.FlowRm
        m.ODECR = Constraint(m.tau, rule = ODECR_)

        m.del_component(m.ODECL)
        def ODECL_(m, h):
            if h==0:
                return Constraint.Skip
            else:
                return m.dCLdh[h] == m.flux[h]/m.FlowLm
        m.ODECL = Constraint(m.tau, rule = ODECL_)        
        
        m.del_component(m.ode_h)
        def ode_h_ (m,i):
            if i == 0:
                return Constraint.Skip
            else:
                return m.dheight[i] == m.height
        m.ode_h = Constraint(m.tau, rule= ode_h_)
        
        #m.del_component(m.initcon)
        def _init(m):
            yield m.cRs[0] == self.rich_in[self.rich_stream_name]
            yield m.cRs[1] == self.rich_out[self.rich_stream_name]
            yield m.cLs[0] == self.rich_in[self.lean_stream_name]
            yield m.cLs[1] == self.rich_out[self.lean_stream_name]
            yield m.h[0] == 0
        #m.initcon = ConstraintList(rule=_init)  
        
        m.del_component(m.KogaEq)
        def KogaEq_(m):
            return m.koga == (m.VelocityR)/(m.porosity*m.poroCor)*m.ag*(((m.de*m.PartSizeCor*m.VelocityR)/(m.porosity*m.poroCor*m.visRich))**(-0.25))*(0.7**(-0.677))*1
        
        m.KogaEq = Constraint(rule=KogaEq_)
        
        m.del_component(m.VelocityREq)
        def VelocityREq_(m):
            return m.VelocityR*m.area == m.FlowRVlat
            
        m.VelocityREq = Constraint(rule=VelocityREq_)

        m.del_component(m.VelocityLEq)
        def VelocityLEq_(m):
            return m.VelocityL*m.area == m.FlowLVlat
            
        m.VelocityLEq = Constraint(rule=VelocityLEq_)

        m.del_component(m.AreaEq)
        def AreaEq_(m):
            return m.area == pi/4*(m.diameter**2)
            
        m.AreaEq = Constraint(rule=AreaEq_)
        
        #Flooding equations
        m.del_component(m.Flood1)
        def Flood1_(m):
            return m.Flood == 249.089/0.3048*(0.12*(m.packfact*0.3048)**0.7)  
        m.Flood1 = Constraint(rule = Flood1_) 
        
        m.del_component(m.Flood2)
        def Flood2_(m):
            return m.FloodAct ==(94*((m.ReL**1.11)/(m.ReG**1.8))+4.4)*6*(1-m.porosity*m.poroCor)/(m.de*m.PartSizeCor*((m.porosity*m.poroCor)**3))*m.RHOG*(m.VelocityR**2)
                                                                                                
        m.Flood2 = Constraint(rule = Flood2_)
        
        m.del_component(m.Flood3)
        def Flood3_(m):
            return m.Flood >=  m.FloodAct
        
        m.Flood3 = Constraint(rule = Flood3_) 
                
        #========================================
        # MODIFIED CONSTRAINTS
        #========================================
            
        m.del_component(m.TRateVap)
        def TRateVap_(m, h):
            if h==0:
                return Constraint.Skip
            else:
                return m.flux[h] == -m.koga*m.area*m.ai*\
                                    (m.cRs[h]-m.henry*m.cLs[h])
        m.TRateVap = Constraint(m.tau, rule = TRateVap_)
        
        m.del_component(m.loverdup)
        
        def loverdup_(m):
            return m.height <= 40*m.diameter
            
        m.loverdup = Constraint(rule=loverdup_)
        
        m.del_component(m.loverdlo)
        
        def loverdlo_(m):
            return m.height >= 0.1*m.diameter
            
        m.loverdlo = Constraint(rule=loverdlo_)

        m.del_component(m.ReynoldsG)
        
        def ReynoldsG_(m):
            return m.ReG ==   m.RHOG*m.VelocityR/(m.visRich*m.ap);
        m.ReynoldsG = Constraint(rule = ReynoldsG_) 
        
        m.del_component(m.ReynoldsL)
        
        def ReynoldsL_(m):
            return m.ReL ==   m.RHOL*m.VelocityL/(m.vis*m.ai);
        m.ReynoldsL = Constraint(rule = ReynoldsL_) 
        
        def Aid_(m):
            return m.ai ==  m.ap*m.surfacor*(1-exp(-1.45*((0.075/m.surften)**0.75)*((m.RHOL*m.VelocityR/(m.vis*m.ap))**0.1)*((m.ap*((m.VelocityR)**2)/9.81)**(-0.05))*((((m.RHOL*(m.VelocityR)**2))/(m.ap*m.surften))**0.2)))
            
        m.Aid = Constraint(rule = Aid_) 

        #========================================
        # OBJECTIVE and SOLVE
        #======================================== 

        m.del_component(m.Obj2)
        def Obj3_(m):
            return m.AF*23805*(m.diameter**0.57)*1.15*m.height + m.AF*pi*(m.diameter**2)/4*m.height*m.PackCost
        #23805*(m.diameter**0.57)*1.15*m.height + pi*(m.diameter**2)/4*m.height*m.PackCost

        m.Obj3 = Objective(rule = Obj3_,sense=minimize)
        
        #m.Obj2.deactivate()
        m.Obj3.activate()  
        #solver = SolverFactory('./../../BARON/baron')
        #solver= SolverFactory('ipopt')
        #results = solver.solve(m,tee=True)
        presolve_clone = m.clone()
        results = self.solve_until_feas(m)
        
        #========================================
        # POST PROCESSING AND PRINT
        #======================================== 
        #display(m)
        #results = solver_manager.solve(m,opt=solver)

        #display(m)
        q= m.AF*23805*(m.diameter**0.57)*1.15*m.height()
        w=m.AF*pi*(m.diameter()**2)/4*m.height()*m.PackCost
        #print(m.FixCost, "    ",q,"   ", w)
        m.height.pprint()
        m.diameter.pprint()
        #m.ai.pprint()
        m.FloodAct.pprint()
        m.Flood.pprint()  
        m.ai.pprint()
        #m.ap.pprint()
        m.packfact.pprint()
        m.VelocityR.pprint()
        m.VelocityL.pprint()
        m.koga.pprint()
        #m.packsize.pprint()
        m.PackCost.pprint()
        #m.SpecAreaPacking.pprint()
        m.ReL.pprint()
        m.ReG.pprint()
        #m.packVoid.pprint()
        print(value(m.cRs[0]))
        print(value(m.cRs[1]))
        print(value(m.cLs[0]))
        print(value(m.cLs[1]))
        print(results)
        #results.pprint
        #q = m.FlowRm.value*(m.cRs[0].value-m.cRs[1].value)
        #print("mass exchanged R:  ", q )
        #q = m.FlowLm.value*(m.cLs[0].value-m.cLs[1].value)
        #print("mass exchanged L:  ", q )
        success_solve = bool

        print("results type: ",type(results))
        if results == 'failed epically':
            print("The exchanger could not be solved. This means that for this exchanger no model is stored. Could result in failure to produce correction factors.")
            success_solve = False
        elif not isinstance(results, str):
            if isinstance(results, pyomo.core.base.PyomoModel.ConcreteModel):
                print("model did not solve correctly, so it is skipped")
                success_solve = False
            elif (results.solver.status == SolverStatus.ok) and (results.solver.termination_condition == TerminationCondition.optimal):
                success_solve=True
            elif (results.solver.status == SolverStatus.ok) and (results.solver.termination_condition == TerminationCondition.locallyOptimal):
                success_solve=True
            else:
                #Should add way to deal with unsolved NLPs (increase elements?)
                print("NLP1 failed.")
                success_solve = False
        else:
            success_solve = False
        print("solve success = ", success_solve)     
                                
        return m, success_solve, presolve_clone
    
    def Construct_pyomo_model_5(self,m, success_solve, m2):
        """ Constructs the the 5th pyomo model of 5. Contains all variables and model information.
        
        Builds on previous model by adding a few equations and variables in order to obtain initializations 
        for subsequent more detailed models.
        
        Args:
            m (Concrete pyomo model): model from Construct_pyomo_model_4
            success_solve (bool): passed from previous solve and tells the model whether it should provide 
                                    a different initial point as the previous model failed (from pre-solved clone above)
            m2 (clone of concrete pyomo model): clone of previous NLP model from before the solve statement. Used if 
                                            previous model did not solve correctly
            
        Returns:
            m (Concrete pyomo model): final solution.
            results (solver results): ipopt solver output.
            pre_solve_clone (clone of concrete model before solve statement): should only be used if solve failed
        
        """
        print("Setting up the 5th NLP subp-problem, pack in GAMS")
        #=========================================
        #Variables from Previous NLP
        #=========================================
        old_solve_clone = m.clone()
        
        if success_solve:
            height_init=old_solve_clone.height.value
        else:
            height_init=m2.height.value
            
        m.del_component(m.height)
        m.height = Var(initialize = height_init,bounds = (0.0000001,None))
        
        
        flux_init = {}
        if success_solve:
            for h in m.h:
                flux_init[h]=old_solve_clone.flux[h].value
        else:
            for h in m.h:
                flux_init[h]=m2.flux[h].value
                
        m.del_component(m.flux)
        m.flux = Var(m.tau,initialize = flux_init)

        cRs_init = {}
        if success_solve:
            for h in m.h:
                cRs_init[h]=old_solve_clone.cRs[h].value 
        else:
            for h in m.h:
                cRs_init[h]=m2.cRs[h].value 
        #m.del_component(m.cRs)
        #m.cRs = Var(m.tau, initialize = cRs_init, within = NonNegativeReals)

        cLs_init = {}
        if success_solve:
            for h in m.h:
                cLs_init[h]=old_solve_clone.cLs[h].value  
        else:
            for h in m.h:
                cLs_init[h]=m2.cLs[h].value
            
        #m.del_component(m.cLs)
        #m.cLs = Var(m.tau, initialize = cLs_init, within = NonNegativeReals)
        
        if success_solve:
            diameter_init=old_solve_clone.diameter.value
        else:
            diameter_init=m2.diameter.value
        m.del_component(m.diameter)
        m.diameter = Var(initialize = diameter_init, bounds = (0.00000001, None))

        #m.del_component(m.dheight)
        #m.dheight = DerivativeVar(m.h)
        #m.del_component(m.dCRdh)
        #m.dCRdh= DerivativeVar(m.cRs, withrespectto=m.tau)
        #m.del_component(m.dCLdh)
        #m.dCLdh= DerivativeVar(m.cLs, withrespectto=m.tau)
        area_init = 0
        if success_solve:
            area_init=old_solve_clone.area.value
        else:
            area_init=m2.area.value
            
        m.del_component(m.area)
        m.area = Var(initialize = area_init, within = NonNegativeReals)

        koga_init = 0
        if success_solve:
            koga_init=old_solve_clone.koga.value
        else:
            koga_init=m2.koga.value
            
        m.del_component(m.koga)
        m.koga = Var(initialize = koga_init, within = NonNegativeReals)
        
        VelocityR_init = 0
        if success_solve:
            VelocityR_init=old_solve_clone.VelocityR.value
        else:
            VelocityR_init=m2.VelocityR.value
            
        #VelocityR_init=m.VelocityR.value
        m.del_component(m.VelocityR)
        m.VelocityR = Var(initialize =VelocityR_init, bounds=(0.00000000001,None))
        
        VelocityL_init = 0
        if success_solve:
            VelocityL_init=old_solve_clone.VelocityL.value
        else:
            VelocityL_init=m2.VelocityL.value
        
        m.del_component(m.VelocityL)
        m.VelocityL = Var(initialize = VelocityL_init, within = NonNegativeReals) 
        
        ReL_init=0
        if success_solve:
            ReL_init=old_solve_clone.ReL.value
        else:
            ReL_init=m2.ReL.value
            
        m.del_component(m.ReL)
        m.ReL = Var(initialize = ReL_init, within = NonNegativeReals) 
        
        ReG_init=0
        if success_solve:
            ReG_init=old_solve_clone.ReG.value
        else:
            ReG_init=m2.ReG.value

        m.del_component(m.ReG)
        m.ReG = Var(initialize = ReG_init, bounds = (0.00000001,None))

        Flood_init=0
        if success_solve:
            Flood_init=old_solve_clone.Flood.value
        else:
            Flood_init=m2.Flood.value

        m.del_component(m.Flood)
        m.Flood = Var(initialize = Flood_init, within = NonNegativeReals)

        FloodAct_init=0
        if success_solve:
            FloodAct_init=old_solve_clone.FloodAct.value
        else:
            FloodAct_init=m2.FloodAct.value

        m.del_component(m.FloodAct)
        m.FloodAct = Var(initialize = FloodAct_init, within = NonNegativeReals)
        
        packfact_init=0
        if success_solve:
            packfact_init=old_solve_clone.packfact.value
        else:
            packfact_init=m2.packfact.value
            
        m.del_component(m.packfact)
        m.packfact = Var(initialize = packfact_init, bounds =(0,100000))

        ai_init=0
        if success_solve:
            ai_init=old_solve_clone.ai.value
        else:
            ai_init=m2.ai.value

        m.del_component(m.ai)
        m.ai = Var(initialize = ai_init, within = NonNegativeReals) 
        
        #=========================================
        #New Variables
        #=========================================      
        #These can have more thoughtful inits
        m.packsize = Var(initialize = 0.05, bounds=(0.003, None))
        m.SpecAreaPacking = Var(initialize = ai_init, within = NonNegativeReals)
        m.packVoid = Var(initialize=0.68,bounds = (0.5, None))
        
        m.del_component(m.PackCost)
        m.PackCost = Var(initialize = (self.ME_inits["packcost"]*self.ME_inits["packcostcor"]), within = NonNegativeReals)
        
        #========================================
        #OLD CONSTRAINTS
        #========================================
        #Differential Equations
        m.del_component(m.ODECR)
        def ODECR_(m, h):
            if h==0:
                return Constraint.Skip
            else:
                return m.dCRdh[h] == m.flux[h]/m.FlowRm
        m.ODECR = Constraint(m.tau, rule = ODECR_)

        m.del_component(m.ODECL)
        def ODECL_(m, h):
            if h==0:
                return Constraint.Skip
            else:
                return m.dCLdh[h] == m.flux[h]/m.FlowLm
        m.ODECL = Constraint(m.tau, rule = ODECL_)        
        
        m.del_component(m.ode_h)
        def ode_h_ (m,i):
            if i == 0:
                return Constraint.Skip
            else:
                return m.dheight[i] == m.height
        m.ode_h = Constraint(m.tau, rule= ode_h_)
        
        #m.del_component(m.initcon)
        def _init(m):
            yield m.cRs[0] == self.rich_in[self.rich_stream_name]
            yield m.cRs[1] == self.rich_out[self.rich_stream_name]
            yield m.cLs[0] == self.rich_in[self.lean_stream_name]
            yield m.cLs[1] == self.rich_out[self.lean_stream_name]
            yield m.h[0] == 0
        #m.initcon = ConstraintList(rule=_init)  
        
        m.del_component(m.VelocityREq)
        def VelocityREq_(m):
            return m.VelocityR*m.area == m.FlowRVlat
            
        m.VelocityREq = Constraint(rule=VelocityREq_)

        m.del_component(m.VelocityLEq)
        def VelocityLEq_(m):
            return m.VelocityL*m.area == m.FlowLVlat
            
        m.VelocityLEq = Constraint(rule=VelocityLEq_)

        m.del_component(m.AreaEq)
        def AreaEq_(m):
            return m.area == pi/4*(m.diameter**2)
            
        m.AreaEq = Constraint(rule=AreaEq_)
        
        #Flooding equations
        m.del_component(m.Flood1)
        def Flood1_(m):
            return m.Flood == 249.089/0.3048*(0.12*(m.packfact*0.3048)**0.7)  
        m.Flood1 = Constraint(rule = Flood1_) 
        
        m.del_component(m.Flood3)
        def Flood3_(m):
            return m.Flood >=  m.FloodAct
        
        m.Flood3 = Constraint(rule = Flood3_) 
        
        m.del_component(m.loverdup)
        
        def loverdup_(m):
            return m.height <= 40*m.diameter
            
        m.loverdup = Constraint(rule=loverdup_)
        
        m.del_component(m.loverdlo)
        
        def loverdlo_(m):
            return m.height >= 2*m.diameter
            
        m.loverdlo = Constraint(rule=loverdlo_)
       
        #========================================
        # MODIFIED CONSTRAINTS
        #========================================
        m.del_component(m.TRateVap)

        def TRateVap_(m, h):
            if h==0:
                return Constraint.Skip
            else:
                return m.flux[h] == -m.koga*m.ai*m.area*(m.cRs[h]-m.henry*m.cLs[h])
        m.TRateVap = Constraint(m.tau, rule = TRateVap_)

        m.del_component(m.KogaEq)
        def KogaEq_(m):
            return m.koga == (m.VelocityR)/(m.packVoid)*m.ag*(((m.packsize*m.VelocityR)/(m.packVoid*m.visRich))**(-0.25))*(0.7**(-0.677))*(1)
        m.KogaEq = Constraint(rule=KogaEq_)

        m.del_component(m.Flood2)
        def Flood2_(m):
            return m.FloodAct ==(94*((m.ReL**1.11)/(m.ReG**1.8))+4.4)*6*(1-m.packVoid)/(m.packsize*((m.packVoid)**3))*m.RHOG*(m.VelocityR**2)
        
        m.Flood2 = Constraint(rule = Flood2_)

        m.del_component(m.ReynoldsG)
        def ReynoldsG_(m):
            return m.ReG ==   m.RHOG*m.VelocityR/(m.visRich*m.SpecAreaPacking);
        m.ReynoldsG = Constraint(rule = ReynoldsG_) 
        
        m.del_component(m.ReynoldsL)
        def ReynoldsL_(m):
            return m.ReL ==   m.RHOL*m.VelocityL/(m.vis*m.ai);
        m.ReynoldsL = Constraint(rule = ReynoldsL_) 
        
        m.del_component(m.Aid)
        def Aid_(m):
            return m.ai ==  m.SpecAreaPacking*(1-exp(-1.45*((0.075/m.surften)**0.75)*((m.RHOL*m.VelocityR/(m.vis*m.SpecAreaPacking))**0.1)*((m.SpecAreaPacking*(m.VelocityR**2)/9.81)**(-0.05))*((m.RHOL*(m.VelocityR**2)/(m.SpecAreaPacking*m.surften))**0.2)));

        m.Aid = Constraint(rule = Aid_) 

        def packingFactorEq_(m):
            return m.packfact == (2.0034)*(m.packsize**(-1.564))
        
        m.packingFactorEq = Constraint(rule=packingFactorEq_)
        
        def AreaofPackingEq_(m):
            return m.SpecAreaPacking == (5.0147)*(m.packsize**(-0.978))
        
        m.AreaofPackingEq = Constraint(rule=AreaofPackingEq_)  
        
        #def PackingDensityEq_(m):
        #    return m.packDens == (-4E+06)*(m.packsize**(3))+ 653592*(m.packsize**(2))-31489*m.packsize + 1146.5
        
        #m.PackingDensityEq = Constraint(rule=PackingDensityEq_)
        
        def PackVoidEq_(m):
            return m.packVoid == 0.0569*log(m.packsize)+0.9114
        
        m.PackVoidEq = Constraint(rule=PackVoidEq_)
        
        def PackCostEq_(m):
            return m.PackCost == 397431*(m.packsize**(2)) - 53449*(m.packsize) + 2366.1
        
        m.PackCostEq = Constraint(rule=PackCostEq_)   
        
        
        def PackSizeCons_(m):
            return m.packsize *20 >= m.diameter
        m.PackSizeCons = Constraint(rule=PackCostEq_)
        #========================================
        # OBJECTIVE and SOLVE
        #======================================== 
        m.del_component(m.Obj3)        
        def Obj4_(model):
           return m.AF*23805*(m.diameter**0.57)*1.15*m.height + m.AF*pi*(m.diameter**2)/4*m.height*m.PackCost
       #m.AF*23805*(m.diameter**0.57)*1.15*m.height+\
       #                         m.AF*pi*(m.diameter**2)/4*m.height*m.PackCost

        m.Obj4 = Objective( rule = Obj4_,sense=minimize)
        #m.Obj3.deactivate()
        m.Obj4.activate() 
        m.height.pprint()
        presolve_clone = m.clone()
        results = self.solve_until_feas(m)
        #========================================
        # POST PROCESSING AND PRINT
        #======================================== 
        #display(m)
        
        print(type(results))
        if results == "Failed epically":
            print("The exchanger problem could not be solved")
            
        success_solve = bool

        print("results type: ",type(results))
        if results == 'failed epically':
            print("The exchanger could not be solved. This means that for this exchanger no model is stored. Could result in failure to produce correction factors.")
            success_solve = False
        elif not isinstance(results, str):
            if isinstance(results, pyomo.core.base.PyomoModel.ConcreteModel):
                print("model did not solve correctly, so it is skipped")
                success_solve = False
            elif (results.solver.status == SolverStatus.ok) and (results.solver.termination_condition == TerminationCondition.optimal):
                success_solve=True
            elif (results.solver.status == SolverStatus.ok) and (results.solver.termination_condition == TerminationCondition.locallyOptimal):
                success_solve=True
            else:
                #Should add way to deal with unsolved NLPs (increase elements?)
                print("NLP1 failed.")
                success_solve = False
        else:
            success_solve = False
        print("solve success = ", success_solve) 
       
        q= m.AF*23805*(m.diameter**0.57)*1.15*m.height()
        w=m.AF*pi*(m.diameter()**2)/4*m.height()*m.PackCost
        print(m.FixCost, "shell",q,"packing   ", w)
        #m.CapCost.pprint()
        m.height.pprint()
        m.diameter.pprint()
        #m.ai.pprint()
        m.FloodAct.pprint()
        m.Flood.pprint()  
        m.ai.pprint()
        #m.ap.pprint()
        m.packfact.pprint()
        m.VelocityR.pprint()
        m.VelocityL.pprint()
        m.koga.pprint()
        m.packsize.pprint()
        m.PackCost.pprint()
        m.SpecAreaPacking.pprint()
        m.ReL.pprint()
        m.ReG.pprint()
        m.packVoid.pprint()
        print(value(m.cRs[0]))
        print(value(m.cRs[1]))
        print(value(m.cLs[0]))
        print(value(m.cLs[1]))
        #m.display()
        print('=============================================================================================')
        print(results)
        #m.load(results)
        #elif (results.solver.termination_condition == TerminationCondition.infeasible) or (results.solver.termination_condition == TerminationCondition.maxIterations):  
        #    print("The exchanger problem could not be solved")
            #raise Exception("Could not find a valid model to continue iterations")
        return m, results, presolve_clone, success_solve
    
    def Construct_pyomo_model_6 (self,m, success_solve, m2):
        """ Constructs the the 6th pyomo model of 6. Contains all variables and model information.
        
        Builds on previous model by adding a few equations and variables in order to obtain initializations 
        for subsequent more detailed models.
        
        Args:
            m (Concrete pyomo model): model from Construct_pyomo_model_5
            success_solve (bool): passed from previous solve and tells the model whether it should provide 
                                    a different initial point as the previous model failed (from pre-solved clone above)
            m2 (clone of concrete pyomo model): clone of previous NLP model from before the solve statement. Used if 
                                            previous model did not solve correctly
            
        Returns:
            m (Concrete pyomo model): final solution.
            results (solver results): ipopt solver output.
            pre_solve_clone (clone of concrete model before solve statement): should only be used if solve failed
        
        """
        print("Setting up the 6th NLP subp-problem, pack2 in GAMS")
        #=========================================
        #Variables from Previous NLP
        #=========================================
        if success_solve:
            height_init=m.height.value
        else:
            height_init=m2.height.value
            
        m.del_component(m.height)
        m.height = Var(initialize = height_init,bounds = (0.0000001,None))
        
        
        flux_init = {}
        if success_solve:
            for h in m.h:
                flux_init[h]=m.flux[h].value
        else:
            for h in m.h:
                flux_init[h]=m2.flux[h].value
                
        m.del_component(m.flux)
        m.flux = Var(m.tau,initialize = flux_init)

        cRs_init = {}
        if success_solve:
            for h in m.h:
                cRs_init[h]=m.cRs[h].value 
        else:
            for h in m.h:
                cRs_init[h]=m2.cRs[h].value 
        #m.del_component(m.cRs)
        #m.cRs = Var(m.tau, initialize = cRs_init, within = NonNegativeReals)

        cLs_init = {}
        if success_solve:
            for h in m.h:
                cLs_init[h]=m.cLs[h].value  
        else:
            for h in m.h:
                cLs_init[h]=m2.cLs[h].value
            
        #m.del_component(m.cLs)
        #m.cLs = Var(m.tau, initialize = cLs_init, within = NonNegativeReals)
        
        if success_solve:
            diameter_init=m.diameter.value
        else:
            diameter_init=m2.diameter.value
        m.del_component(m.diameter)
        m.diameter = Var(initialize = diameter_init, bounds = (0.0001, None))

        #m.del_component(m.dheight)
        #m.dheight = DerivativeVar(m.h)
        #m.del_component(m.dCRdh)
        #m.dCRdh= DerivativeVar(m.cRs, withrespectto=m.tau)
        #m.del_component(m.dCLdh)
        #m.dCLdh= DerivativeVar(m.cLs, withrespectto=m.tau)
        area_init = 0
        if success_solve:
            area_init=m.area.value
        else:
            area_init=m2.area.value
            
        m.del_component(m.area)
        m.area = Var(initialize = area_init, within = NonNegativeReals)

        koga_init = 0
        if success_solve:
            koga_init=m.koga.value
        else:
            koga_init=m2.koga.value
            
        m.del_component(m.koga)
        m.koga = Var(initialize = koga_init, within = NonNegativeReals)
        
        VelocityR_init = 0
        if success_solve:
            VelocityR_init=m.VelocityR.value
        else:
            VelocityR_init=m2.VelocityR.value
            
        #VelocityR_init=m.VelocityR.value
        m.del_component(m.VelocityR)
        m.VelocityR = Var(initialize =VelocityR_init, bounds = (0.000000000001,None))
        
        VelocityL_init = 0
        if success_solve:
            VelocityL_init=m.VelocityL.value
        else:
            VelocityL_init=m2.VelocityL.value
        
        m.del_component(m.VelocityL)
        m.VelocityL = Var(initialize = VelocityL_init, within = NonNegativeReals) 
        
        ReL_init=0
        if success_solve:
            ReL_init=m.ReL.value
        else:
            ReL_init=m2.ReL.value
            
        m.del_component(m.ReL)
        m.ReL = Var(initialize = ReL_init, within = NonNegativeReals) 
        
        ReG_init=0
        if success_solve:
            ReG_init=m.ReG.value
        else:
            ReG_init=m2.ReG.value

        m.del_component(m.ReG)
        m.ReG = Var(initialize = ReG_init, within = NonNegativeReals)

        Flood_init=0
        if success_solve:
            Flood_init=m.Flood.value
        else:
            Flood_init=m2.Flood.value

        m.del_component(m.Flood)
        m.Flood = Var(initialize = Flood_init, within = NonNegativeReals)

        FloodAct_init=0
        if success_solve:
            FloodAct_init=m.FloodAct.value
        else:
            FloodAct_init=m2.FloodAct.value

        m.del_component(m.FloodAct)
        m.FloodAct = Var(initialize = FloodAct_init, within = NonNegativeReals)
        
        packfact_init=0
        if success_solve:
            packfact_init=m.packfact.value
        else:
            packfact_init=m2.packfact.value
            
        m.del_component(m.packfact)
        m.packfact = Var(initialize = packfact_init, within = NonNegativeReals)

        ai_init=0
        if success_solve:
            ai_init=m.ai.value
        else:
            ai_init=m2.ai.value

        m.del_component(m.ai)
        m.ai = Var(initialize = ai_init, within = NonNegativeReals) 
        
        packsize_init=0
        if success_solve:
            packsize_init=m.packsize.value
        else:
            packsize_init=m2.packsize.value 
        m.del_component(m.packsize)
        m.packsize = Var(initialize = packsize_init, within = NonNegativeReals)
        
        SpecAreaPacking_init=0
        if success_solve:
            SpecAreaPacking_init=m.SpecAreaPacking.value
        else:
            SpecAreaPacking_init=m2.SpecAreaPacking.value 
        m.del_component(m.SpecAreaPacking)
        m.SpecAreaPacking = Var(initialize = ai_init, within = NonNegativeReals)
        
        packVoid_init=0
        if success_solve:
            packVoid_init=m.packVoid.value
        else:
            packVoid_init=m2.packVoid.value 
        m.del_component(m.packVoid)
        m.packVoid = Var(initialize=packVoid_init,within = NonNegativeReals)
        
        PackCost_init=0
        if success_solve:
            PackCost_init=m.PackCost.value
        else:
           PackCost_init=m2.PackCost.value 

        m.del_component(m.PackCost)
        m.PackCost = Var(initialize=PackCost_init, within = NonNegativeReals)
        
        #========================================
        #OLD CONSTRAINTS
        #========================================
        #Differential Equations
        m.del_component(m.ODECR)
        def ODECR_(m, h):
            if h==0:
                return Constraint.Skip
            else:
                return m.dCRdh[h] == m.flux[h]/m.FlowRm
        m.ODECR = Constraint(m.tau, rule = ODECR_)

        m.del_component(m.ODECL)
        def ODECL_(m, h):
            if h==0:
                return Constraint.Skip
            else:
                return m.dCLdh[h] == m.flux[h]/m.FlowLm
        m.ODECL = Constraint(m.tau, rule = ODECL_)        
        
        m.del_component(m.ode_h)
        def ode_h_ (m,i):
            if i == 0:
                return Constraint.Skip
            else:
                return m.dheight[i] == m.height
        m.ode_h = Constraint(m.tau, rule= ode_h_)
        
        #m.del_component(m.initcon)
        def _init(m):
            yield m.cRs[0] == self.rich_in[self.rich_stream_name]
            yield m.cRs[1] == self.rich_out[self.rich_stream_name]
            yield m.cLs[0] == self.rich_in[self.lean_stream_name]
            yield m.cLs[1] == self.rich_out[self.lean_stream_name]
            yield m.h[0] == 0
        #m.initcon = ConstraintList(rule=_init)  
        
        m.del_component(m.VelocityREq)
        def VelocityREq_(m):
            return m.VelocityR*m.area == m.FlowRVlat
            
        m.VelocityREq = Constraint(rule=VelocityREq_)

        m.del_component(m.VelocityLEq)
        def VelocityLEq_(m):
            return m.VelocityL*m.area == m.FlowLVlat
            
        m.VelocityLEq = Constraint(rule=VelocityLEq_)

        m.del_component(m.AreaEq)
        def AreaEq_(m):
            return m.area == pi/4*(m.diameter**2)
            
        m.AreaEq = Constraint(rule=AreaEq_)
        
        #Flooding equations
        m.del_component(m.Flood1)
        def Flood1_(m):
            return m.Flood == 249.089/0.3048*0.12*((m.packfact*0.3048)**0.7)  
        m.Flood1 = Constraint(rule = Flood1_) 
        
        m.del_component(m.Flood3)
        def Flood3_(m):
            return m.Flood >=  m.FloodAct
        
        m.Flood3 = Constraint(rule = Flood3_) 
        
        m.del_component(m.loverdup)
        
        def loverdup_(m):
            return m.height <= 80*m.diameter
            
        m.loverdup = Constraint(rule=loverdup_)
        
        m.del_component(m.loverdlo)
        
        def loverdlo_(m):
            return m.height >= 0.5*m.diameter
            
        m.loverdlo = Constraint(rule=loverdlo_)
       
        m.del_component(m.TRateVap)

        def TRateVap_(m, h):
            if h==0:
                return Constraint.Skip
            else:
                return m.flux[h] == -m.koga*m.ai*m.area*(m.cRs[h]-m.henry*m.cLs[h])
        m.TRateVap = Constraint(m.tau, rule = TRateVap_)

        m.del_component(m.KogaEq)
        def KogaEq_(m):
            return m.koga == (m.VelocityR)/(m.packVoid)*m.ag*(((m.packsize*m.VelocityR)/(m.packVoid*m.visRich))**(-0.25))*(0.7**(-0.677))*(1)
        m.KogaEq = Constraint(rule=KogaEq_)

        m.del_component(m.Flood2)
        def Flood2_(m):
            return m.FloodAct ==(94*((m.ReL**1.11)/(m.ReG**1.8))+4.4)*6*(1-m.packVoid)/(m.packsize*((m.packVoid)**3))*m.RHOG*(m.VelocityR**2)
        
        m.Flood2 = Constraint(rule = Flood2_)

        m.del_component(m.ReynoldsG)
        def ReynoldsG_(m):
            return m.ReG ==   m.RHOG*m.VelocityR/(m.visRich*m.SpecAreaPacking);
        m.ReynoldsG = Constraint(rule = ReynoldsG_) 
        
        m.del_component(m.ReynoldsL)
        def ReynoldsL_(m):
            return m.ReL ==   m.RHOL*m.VelocityL/(m.vis*m.ai);
        m.ReynoldsL = Constraint(rule = ReynoldsL_) 
        
        m.del_component(m.Aid)
        def Aid_(m):
            return m.ai ==  m.SpecAreaPacking*(1-exp(-1.45*((0.075/m.surften)**0.75)*((m.RHOL*m.VelocityR/(m.vis*m.SpecAreaPacking))**0.1)*((m.SpecAreaPacking*(m.VelocityR**2)/9.81)**(-0.05))*((m.RHOL*(m.VelocityR**2)/(m.SpecAreaPacking*m.surften))**0.2)));

        m.Aid = Constraint(rule = Aid_) 

        m.del_component(m.packingFactorEq)
        def packingFactorEq_(m):
            return m.packfact == (2.0034)*(m.packsize**(-1.564))
        
        m.packingFactorEq = Constraint(rule=packingFactorEq_)
        
        m.del_component(m.AreaofPackingEq)
        def AreaofPackingEq_(m):
            return m.SpecAreaPacking == (5.0147)*(m.packsize**(-0.978))
        
        m.AreaofPackingEq = Constraint(rule=AreaofPackingEq_)  
        
        #def PackingDensityEq_(m):
        #    return m.packDens == (-4E+06)*(m.packsize**(3))+ 653592*(m.packsize**(2))-31489*m.packsize + 1146.5
        
        #m.PackingDensityEq = Constraint(rule=PackingDensityEq_)
        
        m.del_component(m.PackVoidEq)
        def PackVoidEq_(m):
            return m.packVoid == 0.0569*log(m.packsize)+0.9114
        
        m.PackVoidEq = Constraint(rule=PackVoidEq_)
        
        m.del_component(m.PackCostEq)
        def PackCostEq_(m):
            return m.PackCost == 397431*(m.packsize**(2)) - 53449*(m.packsize) + 2366.1
        
        m.PackCostEq = Constraint(rule=PackCostEq_)   
        
        #m.del_component(m.m.del_component(m.Obj4))
        #def PackSizeCons_(m):
        #    return m.packsize *10 >= m.diameter
        m.del_component(m.PackSizeCons)
        #========================================
        # OBJECTIVE and SOLVE
        #======================================== 
        m.del_component(m.Obj4)        
        def Obj4_(model):
           return m.AF*23805*(m.diameter**0.57)*1.15*m.height + m.AF*pi*(m.diameter**2)/4*m.height*m.PackCost
       #m.AF*23805*(m.diameter**0.57)*1.15*m.height+\
       #                         m.AF*pi*(m.diameter**2)/4*m.height*m.PackCost

        m.Obj4 = Objective( rule = Obj4_,sense=minimize)
        #m.Obj3.deactivate()
        m.Obj4.activate() 
        m.height.pprint()
        presolve_clone = m.clone()
        results = self.solve_until_feas(m)
        #========================================
        # POST PROCESSING AND PRINT
        #======================================== 
        #display(m)
        
        print(type(results))
        if results == "Failed epically":
            print("The exchanger problem could not be solved")
            
        success_solve = bool

        print("results type: ",type(results))
        if results == 'failed epically':
            print("The exchanger could not be solved. This means that for this exchanger no model is stored. Could result in failure to produce correction factors.")
            success_solve = False
        elif not isinstance(results, str):
            if isinstance(results, pyomo.core.base.PyomoModel.ConcreteModel):
                print("model did not solve correctly, so it is skipped")
                success_solve = False
            elif (results.solver.status == SolverStatus.ok) and (results.solver.termination_condition == TerminationCondition.optimal):
                success_solve=True
            elif (results.solver.status == SolverStatus.ok) and (results.solver.termination_condition == TerminationCondition.locallyOptimal):
                success_solve=True
            else:
                #Should add way to deal with unsolved NLPs (increase elements?)
                print("NLP1 failed.")
                success_solve = False
        else:
            success_solve = False
        print("solve success = ", success_solve) 
       
        q= m.AF*23805*(m.diameter**0.57)*1.15*m.height()
        w=m.AF*pi*(m.diameter()**2)/4*m.height()*m.PackCost
        print(m.FixCost, "    ",q,"   ", w)
        #m.CapCost.pprint()
        m.height.pprint()
        m.diameter.pprint()
        #m.ai.pprint()
        m.FloodAct.pprint()
        m.Flood.pprint()  
        m.ai.pprint()
        #m.ap.pprint()
        m.packfact.pprint()
        m.VelocityR.pprint()
        m.VelocityL.pprint()
        m.koga.pprint()
        m.packsize.pprint()
        m.PackCost.pprint()
        m.SpecAreaPacking.pprint()
        m.ReL.pprint()
        m.ReG.pprint()
        m.packVoid.pprint()
        #m.display()
        print('=============================================================================================')
        print(results)
        #m.load(results)
        #elif (results.solver.termination_condition == TerminationCondition.infeasible) or (results.solver.termination_condition == TerminationCondition.maxIterations):  
        #    print("The exchanger problem could not be solved")
            #raise Exception("Could not find a valid model to continue iterations")
        return m, results, presolve_clone, success_solve
#CRin_Side = {}
#CRin_Side['R1'] = 0.07
#CRin_Side['L2'] = 0.045

#CRout_Side = {}
#CRout_Side['R1'] = 0.017
#CRout_Side['L2'] = 0.013680236

#FlowM = {}
#FlowM['R1'] = 0.9
#FlowM['L2'] = 1.523
#i = 'R1'
#j='L2'
#mx = mass_exchanger(rich_stream_name = i, lean_stream_name=j,rich_in_side=CRin_Side, rich_out_side=CRout_Side,flowrates=FlowM,me_inits=None)
#ME1 = mx.Construct_pyomo_model()
#ME2 = mx.Construct_pyomo_model_2(ME1)
#ME3 = mx.Construct_pyomo_model_3(ME2)
#ME4 = mx.Construct_pyomo_model_4(ME3)
#ME5 = mx.Construct_pyomo_model_5(ME4)