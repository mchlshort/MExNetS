# -*- coding: utf-8 -*-
"""
Created on Sun Apr 21 10:48:43 2019

This file aims to provide a selection of solver options and types to ensure
that a certain NLP or MINLP will find a feasible solution, with no guarantee on
optimality. The file is useful for when a program contains many optimization
problems that rely on each other to find solutions. It ensures that the
solver never terminates your program through a set of try - except clauses.

You need to have GAMS installed and added to the PATH with licences for CONOPT, DICOPT
and BARON. Additionally, it is useful to have separate installs of IPOPT and BARON.

It may be clumsy, but it works!

@author: mchlshort
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

#should possibly include more solvers, solver options and user options to choose exe location and solver
def solve_until_feas_NLP(m):
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
        results = solver.solve(m1,tee=False, solver = 'conopt')
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

def solve_until_feas_MINLP_BARON(m):
    """The solve function for the MINLP when seeking global solution.
    
    This function solves the MINLP Pyomo model using BARON. If BARON fails then it attempts
    to use DICOPT to solve and finally, if DICOPT fails we use Bonmin. It has many try and 
    except statements in order to try to use many different solver options to solve the problem.
    Ensures that the iterative procedure does not exit if an infeasible model is found and 
    increases the likelihood that a feasible solution is found.
    
    Args:
        m (pyomo model, concrete): the pyomo model of the MEN with all potential matches selected
        
    returns:
        results (solver results): returns the solved model and results from the solve.
        solversolved (str): returns None if no solver else returns name of solver that successfully solved
        globalsol (bool): This only returns True if we solved to global with BARON
        
    """
    opt = SolverFactory('baron')
    options={}
    #options['bonmin.algorithm']='B-BB'
    #BARON SECTION
    BARONsolved = False
    DICOPTsolved = False
    BONMINsolved = False
    globalsol = False
    print("==================ATTEMPTING TO SOLVE WITH BARON==========================")
    try:
        options['MaxTime'] = 1000
        results = opt.solve(m,options = options,tee=True)
        if (results.solver.status == SolverStatus.ok) and (results.solver.termination_condition == TerminationCondition.optimal):
            print("successfully solved")
            BARONsolved = True
            globalsol = True
            
        elif (results.solver.termination_condition == TerminationCondition.infeasible) or  (results.solver.termination_condition == TerminationCondition.maxIterations):
            print("First solve was infeasible, solving with changed match options")
            options['EpsR']= 0.02
            results = opt.solve(m,options = options,tee=True)
            
            if (results.solver.status == SolverStatus.ok) and (results.solver.termination_condition == TerminationCondition.optimal):
                print("successfully solved")
                BARONsolved = True
            
            elif (results.solver.termination_condition == TerminationCondition.infeasible) or  (results.solver.termination_condition == TerminationCondition.maxIterations):
                print("Second solve was infeasible, solving with changed match options")
                options['EpsR']= 0.05
                results = opt.solve(m,options = options,tee=False)
                if (results.solver.status == SolverStatus.ok) and (results.solver.termination_condition == TerminationCondition.optimal):
                    print("successfully solved")
                    BARONsolved = True
                
                else:
                    print("Cannot determine cause of fault")
                    print("Solver Status: ",  results.solver.status) 
            else:
                print("Cannot determine cause of fault")
                print("Solver Status: ",  results.solver.status)     
        else:
            print("Cannot determine cause of fault")
            print("Solver Status: ",  results.solver.status)        
    except:
         print("Could not solve with BARON")
                
                
    #opt = SolverFactory('bonmin',executable='./../../../../cygwin64/home/Michael/Bonmin-1.8.6/build/bin/bonmin')
    #opt = SolverFactory('./../../Bonmin/build/bin/bonmin')
    try:
        if BARONsolved == True:
            print("Solved using one of the global solvers")
        else:
            print("==================ATTEMPTING TO SOLVE WITH DICOPT==========================")
            solver=SolverFactory('gams')
            options={}
            m1 = m
            results = solver.solve(m1,tee=True, solver = 'dicopt')
            if (results.solver.status == SolverStatus.ok) and (results.solver.termination_condition == TerminationCondition.optimal):
                print("successfully solved")
                DICOPTsolved = True
            
            elif (results.solver.termination_condition == TerminationCondition.infeasible) or  (results.solver.termination_condition == TerminationCondition.maxIterations):
                print("First solve was infeasible, solving with feasibility pump")
                options['feaspump']= 2
                results = opt.solve(m,options = options,tee=False)
            
                if (results.solver.status == SolverStatus.ok) and (results.solver.termination_condition == TerminationCondition.optimal):
                    print("successfully solved")
                    DICOPTsolved = True
                
                elif (results.solver.termination_condition == TerminationCondition.infeasible) or  (results.solver.termination_condition == TerminationCondition.maxIterations):
                    print("Second solve was infeasible, solving with changed match options")
                    options1['optcr']= 0.05
                    results = opt.solve(m,options = options1,tee=False)
                    if (results.solver.status == SolverStatus.ok) and (results.solver.termination_condition == TerminationCondition.optimal):
                        print("successfully solved")
                        DICOPTsolved = True
                
                    else:
                        print("Cannot determine cause of fault")
                        print("Solver Status: ",  results.solver.status) 
                else:
                    print("Cannot determine cause of fault")
                    print("Solver Status: ",  results.solver.status)     
            else:
                print("Cannot determine cause of fault")
                print("Solver Status: ",  results.solver.status)        
    except:
         print("Could not solve with DICOPT")
        
    try:
        if BARONsolved == True or DICOPTsolved:
            print("Solved using either Dicopt or Baron")
        else:
            print("==================ATTEMPTING TO SOLVE WITH GAMS BARON==========================")
            solver=SolverFactory('gams')
            options={}
            m1 = m
            results = solver.solve(m1,tee=True, solver = 'baron')
            if (results.solver.status == SolverStatus.ok) and (results.solver.termination_condition == TerminationCondition.optimal):
                print("successfully solved")
                BARONsolved = True
                globalsol = True
            
            elif (results.solver.termination_condition == TerminationCondition.infeasible) or  (results.solver.termination_condition == TerminationCondition.maxIterations):
                print("First solve was infeasible, solving with changed match options")
                options['EpsR']= 0.02
                results = opt.solve(m,options = options,tee=True, solver = 'baron')
                
                if (results.solver.status == SolverStatus.ok) and (results.solver.termination_condition == TerminationCondition.optimal):
                    print("successfully solved")
                    BARONsolved = True
                
                elif (results.solver.termination_condition == TerminationCondition.infeasible) or  (results.solver.termination_condition == TerminationCondition.maxIterations):
                    print("Second solve was infeasible, solving with changed match options")
                    options['EpsR']= 0.05
                    results = opt.solve(m,options = options,tee=False, solver = 'baron')
                    if (results.solver.status == SolverStatus.ok) and (results.solver.termination_condition == TerminationCondition.optimal):
                        print("successfully solved")
                        BARONsolved = True
                
                    else:
                        print("Cannot determine cause of fault")
                        print("Solver Status: ",  results.solver.status) 
                else:
                    print("Cannot determine cause of fault")
                    print("Solver Status: ",  results.solver.status)     
            else:
                print("Cannot determine cause of fault")
                print("Solver Status: ",  results.solver.status)        
    except:
         print("Could not solve with DICOPT")   
         
         
    try:
        if BARONsolved == True or DICOPTsolved:
            print("Solved using either Dicopt or Baron")
        else:
            print("==================ATTEMPTING TO SOLVE WITH BARON WITH BAD GAP==========================")
            solver=SolverFactory('baron')
            options={}
            options['MaxTime'] = 1000
            options['EpsR']= 0.1
            m1 = m
            results = solver.solve(m1,tee=True, options = options)
            if (results.solver.status == SolverStatus.ok) and (results.solver.termination_condition == TerminationCondition.optimal):
                print("successfully solved")
                BARONsolved = True
                
            else:
                print("Cannot determine cause of fault")
                print("Solver Status: ",  results.solver.status)        
    except:
         print("Could not solve with DICOPT")            

         
    print("BARONsolved:", BARONsolved)
    print("DICOPTsolved:", DICOPTsolved)
    
    if BARONsolved == True:
        print("Solved using one of the global solvers")
    elif DICOPTsolved == True:
        print("Solved using DICOPT")
    else:
        #Need to add bonmin to PATH!
        opt = SolverFactory('gams')
        options={}
        options['bonmin.algorithm']='B-BB'
        
        #This can probably be greatly improved        
        print("==================ATTEMPTING TO SOLVE WITH BONMIN==========================")
        try:
            results = opt.solve(m,options = options,tee=False, solver = 'bonmin')
            if (results.solver.status == SolverStatus.ok) and (results.solver.termination_condition == TerminationCondition.optimal):
                print("successfully solved")
                BONMINsolved = True
                
            elif (results.solver.termination_condition == TerminationCondition.infeasible) or  (results.solver.termination_condition == TerminationCondition.maxIterations):
                print("First solve was infeasible, solving with changed match options")
                options={}
                options['mu_strategy'] = 'monotone'
                options['mu_init'] = 1e-6
                options['bonmin.algorithm']='B-BB'
                options['bonmin.allowable_fraction_gap']= 0.05
                results = opt.solve(m,options = options,tee=False, solver = 'bonmin')
                
                if (results.solver.status == SolverStatus.ok) and (results.solver.termination_condition == TerminationCondition.optimal):
                    print("successfully solved")
                    BONMINsolved = True
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
                        BONMINsolved = True
                    elif (results.solver.termination_condition == TerminationCondition.infeasible) or  (results.solver.termination_condition == TerminationCondition.maxIterations):
                        options2['mu_strategy'] = 'monotone'
                        options2['mu_init'] = 1e-5
                        options2['bound_relax_factor'] = 0
                        options2['bonmin.algorithm']='B-BB'
                        options2['bonmin.num_resolve_at_node']=5
                        results = opt.solve(m,options = options2,tee=False)
                        
                        if (results.solver.status == SolverStatus.ok) and (results.solver.termination_condition == TerminationCondition.optimal):
                            print("successfully solved")
                            BONMINsolved = True
                        elif (results.solver.termination_condition == TerminationCondition.infeasible) or  (results.solver.termination_condition == TerminationCondition.maxIterations):
                            options3['mu_strategy'] = 'monotone'
                            options3['mu_init'] = 1e-5
                            options3['bound_push'] = 1e-5
                            #options3['bound_relax_factor'] = 0
                            options3['bonmin.algorithm']='B-BB'
                            results = opt.solve(m, options = options3, tee=False)
                            if (results.solver.status == SolverStatus.ok) and (results.solver.termination_condition == TerminationCondition.optimal):
                                print("successfully solved")
                                BONMINsolved = True
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
                                    BONMINsolved = True
                                elif (results.solver.termination_condition == TerminationCondition.infeasible) or  (results.solver.termination_condition == TerminationCondition.maxIterations):
                                    options11['bonmin.algorithm']='B-OA'
                                    results = opt.solve(m, options = options4, tee=False)
                                    if(results.solver.status == SolverStatus.ok) and (results.solver.termination_condition == TerminationCondition.optimal):
                                        print("successfully solved")
                                        BONMINsolved = True
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
                    
            else:
                print("Cannot determine cause of fault")
                print("Solver Status: ",  result.solver.status)

        except:
            print("First try encountered an error") 
            results = opt.solve(m,options = options,tee=True)
    
    if (results.solver.termination_condition == TerminationCondition.infeasible) or (results.solver.termination_condition == TerminationCondition.maxIterations):  
        print("The MINLP problem could not be solved")
        solversolved = None

        return results, solversolved, globalsol
    else:  
        solversolved = None
        if BARONsolved:
            solversolved = 'baron'
        elif DICOPTsolved:
            solversolved = 'dicopt'
        else:
            solversolved = 'bonmin'
        return results, solversolved, globalsol    

        
def solve_until_feas_MINLP_DICOPT(m):
    """The solve function for the MINLP.
    
    This function solves the MINLP Pyomo model using DICOPT first as it gives the fastest solution times.
    It has many try and except statements in case the solver fails to find a solution and throws an exception 
    rather than an infeasible or sub-optimal solution. We also try to use many different solver options to 
    solve the problem. Ensures that the iterative procedure does not exit if an infeasible model is found and increases the likelihood that a feasible 
    solution is found. This is the first algorithm's solve procedure as it cannot guarantee 
    
    Args:
        m (pyomo model, concrete): the pyomo model of the MEN with all potential matches selected
        
    returns:
        results (solver results): returns the solved model and results from the solve.
        solversolved (str): returns None if no solver else returns name of solver that successfully solved
        globalsol (bool): This only returns True if we solved to global with BARON
    """
    opt = SolverFactory('gams')
    options={}
    BARONsolved = False
    DICOPTsolved = False
    BONMINsolved = False
    globalsol = False
    try:
        if BARONsolved == True:
            print("Solved using one of the global solvers")
        else:
            print("==================ATTEMPTING TO SOLVE WITH DICOPT==========================")
            solver=SolverFactory('gams')
            options={}
            m1 = m
            results = solver.solve(m1,tee=True, solver = 'dicopt')
            
            if (results.solver.status == SolverStatus.ok) and (results.solver.termination_condition == TerminationCondition.optimal):
                print("successfully solved")
                DICOPTsolved = True
            
            elif (results.solver.termination_condition == TerminationCondition.infeasible) or  (results.solver.termination_condition == TerminationCondition.maxIterations):
                print("First solve was infeasible, solving with feasibility pump")
                options['feaspump']= 2
                results = opt.solve(m,options = options,tee=False)
            
                if (results.solver.status == SolverStatus.ok) and (results.solver.termination_condition == TerminationCondition.optimal):
                    print("successfully solved")
                    DICOPTsolved = True
                
                elif (results.solver.termination_condition == TerminationCondition.infeasible) or  (results.solver.termination_condition == TerminationCondition.maxIterations):
                    print("Second solve was infeasible, solving with changed match options")
                    options1['optcr']= 0.05
                    results = opt.solve(m,options = options1,tee=False)
                    if (results.solver.status == SolverStatus.ok) and (results.solver.termination_condition == TerminationCondition.optimal):
                        print("successfully solved")
                        DICOPTsolved = True
                
                    else:
                        print("Cannot determine cause of fault")
                        print("Solver Status: ",  results.solver.status) 
                else:
                    print("Cannot determine cause of fault")
                    print("Solver Status: ",  results.solver.status)     
            else:
                print("Cannot determine cause of fault")
                print("Solver Status: ",  results.solver.status)        
    except:
         print("Could not solve with DICOPT")
    
    print("==================ATTEMPTING TO SOLVE WITH BARON==========================")
    try:
        if DICOPTsolved == True:
            print("Solved using DICOPT")
        else:
            options['MaxTime'] = 10000
            results = opt.solve(m,options = options,tee=True)
            if (results.solver.status == SolverStatus.ok) and (results.solver.termination_condition == TerminationCondition.optimal):
                print("successfully solved")
                BARONsolved = True
                globalsol = True
                
            elif (results.solver.termination_condition == TerminationCondition.infeasible) or  (results.solver.termination_condition == TerminationCondition.maxIterations):
                print("First solve was infeasible, solving with changed match options")
                options['EpsR']= 0.02
                results = opt.solve(m,options = options,tee=True)
                
                if (results.solver.status == SolverStatus.ok) and (results.solver.termination_condition == TerminationCondition.optimal):
                    print("successfully solved")
                    BARONsolved = True
                
                elif (results.solver.termination_condition == TerminationCondition.infeasible) or  (results.solver.termination_condition == TerminationCondition.maxIterations):
                    print("Second solve was infeasible, solving with changed match options")
                    options['EpsR']= 0.05
                    results = opt.solve(m,options = options,tee=False)
                    if (results.solver.status == SolverStatus.ok) and (results.solver.termination_condition == TerminationCondition.optimal):
                        print("successfully solved")
                        BARONsolved = True
                    
                    else:
                        print("Cannot determine cause of fault")
                        print("Solver Status: ",  results.solver.status) 
                else:
                    print("Cannot determine cause of fault")
                    print("Solver Status: ",  results.solver.status)     
            else:
                print("Cannot determine cause of fault")
                print("Solver Status: ",  results.solver.status)        
    except:
         print("Could not solve with BARON")
                
    try:
        if BARONsolved == True or DICOPTsolved:
            print("Solved using either Dicopt or Baron")
        else:
            print("==================ATTEMPTING TO SOLVE WITH GAMS BARON==========================")
            solver=SolverFactory('gams')
            options={}
            m1 = m
            results = solver.solve(m1,tee=True, solver = 'baron')
            if (results.solver.status == SolverStatus.ok) and (results.solver.termination_condition == TerminationCondition.optimal):
                print("successfully solved")
                BARONsolved = True
                globalsol = True
            
            elif (results.solver.termination_condition == TerminationCondition.infeasible) or  (results.solver.termination_condition == TerminationCondition.maxIterations):
                print("First solve was infeasible, solving with changed match options")
                options['EpsR']= 0.02
                results = opt.solve(m,options = options,tee=True)
                
                if (results.solver.status == SolverStatus.ok) and (results.solver.termination_condition == TerminationCondition.optimal):
                    print("successfully solved")
                    BARONsolved = True
                
                elif (results.solver.termination_condition == TerminationCondition.infeasible) or  (results.solver.termination_condition == TerminationCondition.maxIterations):
                    print("Second solve was infeasible, solving with changed match options")
                    options['EpsR']= 0.05
                    results = opt.solve(m,options = options,tee=False)
                    if (results.solver.status == SolverStatus.ok) and (results.solver.termination_condition == TerminationCondition.optimal):
                        print("successfully solved")
                        BARONsolved = True

                
                    else:
                        print("Cannot determine cause of fault")
                        print("Solver Status: ",  results.solver.status) 
                else:
                    print("Cannot determine cause of fault")
                    print("Solver Status: ",  results.solver.status)     
            else:
                print("Cannot determine cause of fault")
                print("Solver Status: ",  results.solver.status)        
    except:
         print("Could not solve with GAMS BARON")   
         
         
    try:
        if BARONsolved == True or DICOPTsolved:
            print("Solved using either Dicopt or Baron")
        else:
            print("==================ATTEMPTING TO SOLVE WITH BARON WITH BAD GAP==========================")
            solver=SolverFactory('baron')
            options={}
            options['MaxTime'] = 1000
            options['EpsR']= 0.1
            m1 = m
            results = solver.solve(m1,tee=True, solver = 'baron')
            if (results.solver.status == SolverStatus.ok) and (results.solver.termination_condition == TerminationCondition.optimal):
                print("successfully solved")
                BARONsolved = True
                
            else:
                print("Cannot determine cause of fault")
                print("Solver Status: ",  results.solver.status)        
    except:
         print("Could not solve with DICOPT")            

         
    print("BARONsolved:", BARONsolved)
    print("DICOPTsolved:", DICOPTsolved)
    
    if BARONsolved == True:
        print("Solved using one of the global solvers")
    elif DICOPTsolved == True:
        print("Solved using DICOPT")
    else:
        opt = SolverFactory('bonmin')
        options={}
        options['bonmin.algorithm']='B-BB'
        
        #This can probably be greatly improved
        
        print("==================ATTEMPTING TO SOLVE WITH BONMIN==========================")
        try:
            results = opt.solve(m,options = options,tee=False)
            if (results.solver.status == SolverStatus.ok) and (results.solver.termination_condition == TerminationCondition.optimal):
                print("successfully solved")
                BONMINsolved= True
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
                    BONMINsolved= True
                    
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
                        BONMINsolved= True
                        
                    elif (results.solver.termination_condition == TerminationCondition.infeasible) or  (results.solver.termination_condition == TerminationCondition.maxIterations):
                        options2['mu_strategy'] = 'monotone'
                        options2['mu_init'] = 1e-5
                        options2['bound_relax_factor'] = 0
                        options2['bonmin.algorithm']='B-BB'
                        options2['bonmin.num_resolve_at_node']=5
                        results = opt.solve(m,options = options2,tee=False)
                        
                        if (results.solver.status == SolverStatus.ok) and (results.solver.termination_condition == TerminationCondition.optimal):
                            print("successfully solved")
                            BONMINsolved= True
                        elif (results.solver.termination_condition == TerminationCondition.infeasible) or  (results.solver.termination_condition == TerminationCondition.maxIterations):
                            options3['mu_strategy'] = 'monotone'
                            options3['mu_init'] = 1e-5
                            options3['bound_push'] = 1e-5
                            #options3['bound_relax_factor'] = 0
                            options3['bonmin.algorithm']='B-BB'
                            results = opt.solve(m, options = options3, tee=False)
                            if (results.solver.status == SolverStatus.ok) and (results.solver.termination_condition == TerminationCondition.optimal):
                                print("successfully solved")
                                BONMINsolved= True
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
                                    BONMINsolved= True
                                elif (results.solver.termination_condition == TerminationCondition.infeasible) or  (results.solver.termination_condition == TerminationCondition.maxIterations):
                                    options11['bonmin.algorithm']='B-OA'
                                    results = opt.solve(m, options = options4, tee=False)
                                    if(results.solver.status == SolverStatus.ok) and (results.solver.termination_condition == TerminationCondition.optimal):
                                        print("successfully solved")
                                        BONMINsolved= True
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
                    
            else:
                print("Cannot determine cause of fault")
                print("Solver Status: ",  result.solver.status)

        except:
            print("First try encountered an error") 
            results = opt.solve(m,options = options,tee=True)
    
    if (results.solver.termination_condition == TerminationCondition.infeasible) or (results.solver.termination_condition == TerminationCondition.maxIterations):  
        print("The MINLP problem could not be solved")

        return results, solversolved, globalsol
    else:  
        solversolved = None
        if BARONsolved:
            solversolved = 'baron'
        elif DICOPTsolved:
            solversolved = 'dicopt'
        else:
            solversolved = 'bonmin'
        return results, solversolved, globalsol   