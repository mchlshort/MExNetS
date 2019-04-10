#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 28 14:45:18 2019

The Trust region optimization method for the mass exchanger network synthesis problem inside of the MExNetS package. 

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
import library.MassExchanger
import library.MENS_MINLP
import library.HybridStrategyTR

__author__ = "Michael Short"
__copyright__ = "Copyright 2018"
__credits__ = ["Michael Short, Lorenz T. Biegler, Isafiade, AJ."]
__license__ = "GPL-3"
__version__ = "0.9"
__maintainer__ =  "Michael Short"
__email__ = "shortm@andrew.cmu.edu"
__status__ = "Development"

class TrustRegionMENS(object):
    def __init__(self, model, ncp =3, nfe =100):
        # type: dict,dict, dict,
        """This is the main class for the trust region filter algorithm applied to the mass exchanger network
        synthesis problem. In this class are the tools with which to build the full network formulation using
        the trust region tools and then also the tools to call the truth models and construct the black boxes

        The input is the solved MINLP model that will form the basis of the NLP network synthesis. We will look
        to optimize mass flawrates, species absorbed, sizes of columns, etc. in the network topology that is
        passed down from the MINLP network synthesis, using the black box functions to represent individual
        exchangers.

        Args:
            model (pyomo model): the solved MINLP from the previous step.
            ncp (int, optional):number of collocation points. Default is 3, must be an odd number for Radau roots (preferably under 10)
            nfe (int, optional): number of finite elements. Default is 100, must be a whole number.
            
        Return:
            model:
        """
        #check that args are actually of the right types

        self.minlp = model
        self.ncp = ncp
        self.nfe = nfe

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

        
    def run_TR_algorithm(self):
        """this method builds the NLP formulation based on the results to the MINLP and then calls the "truth models"
        from the individual mass exchangers.
            
        Args: 
            None
            
        Returns: 
            Solved NLP model
        
        """
        model = self.minlp
        
        y ={}
        for i in model.i:
            for j in model.j:
                for k in model.k:
                    y[i,j,k] = model.y[i,j,k].value
                   
        model.del_component(model.y)
        model.del_component(model.y_index)
        model.del_component(model.y_index_index_0)
        
        model.y = Param(model.i,model.j,model.k, initialize = y)

        model.del_component(model.y1)
        model.del_component(model.y1_index)
        model.del_component(model.y1_index_index_0)
        
        model.y1 = Param(model.i,model.j,model.k, initialize = y)
       
        dcininit ={}
        for i in model.i:
            for j in model.j:
                for k in model.k:
                    dcininit[i,j,k] = model.dcin[i,j,k].value

        def dcin_bounds_rule(model,i,j,k):
            if model.y[i,j,k] ==1:
                return (model.EMAC,1)
            else:
                return (model.EMAC,None)
        model.del_component(model.dcin)
        model.del_component(model.dcin_index)
        model.del_component(model.dcin_index_index_0)
        
        dcoutinit ={}
        for i in model.i:
            for j in model.j:
                for k in model.k:
                    dcoutinit[i,j,k] = model.dcout[i,j,k].value

        def dcout_bounds_rule(model,i,j,k):
            if k>=2:
                if model.y[i,j,k-1] == 1:
                    return (model.EMAC,1)
                else:
                    return (model.EMAC,None) 
            else:
                return (model.EMAC,None)
            
        model.del_component(model.dcout)
        model.del_component(model.dcout_index)
        model.del_component(model.dcout_index_index_0)

        model.dcin = Var(model.i,model.j,model.k, initialize=dcininit,bounds=dcin_bounds_rule)
        model.dcout= Var(model.i,model.j,model.k, initialize=dcoutinit,bounds=dcout_bounds_rule)
        
        model.im = {}
        for i in model.i:
            for j in model.j:
                for k in model.k:
                    if model.y[i,j,k] == 1:
                        model.im [i,j,k] = model.M[i,j,k].value
                    else:
                        model.im [i,j,k] = 0
                        
        def M_bounds(model, i,j,k):
            if model.y[i,j,k] ==1:
                return (0.0,None)
            else:
                return (0.0,0.0)       
            
        model.del_component(model.M)
        model.del_component(model.M_index)
        model.del_component(model.M_index_index_0)  
        
        model.M = Var(model.i,model.j,model.k, initialize=model.im, bounds = M_bounds)


        def L_bounds(model,j):
            if model._lean_data.at[j,'F']>0:
                #print("LEAN DATA:   ",self._lean_data.at[j,'F'])
                return (0.0000000001,model._lean_data.at[j,'F'])
        
            else:
                #print("LEAN DATA:   ",0,2)
                return (0.000000001, 100)
        
        #model.L.pprint()
        l_init={}
        for j in model.j:
            l_init[j] = model.L1[j].value
            #print(model.L[j].value)
        #print(l_init)
        model.del_component(model.L1)
        model.del_component(model.L)
        
        model.L1 = Var(model.j, initialize=l_init,bounds = L_bounds)
        #model.L.pprint()
    
       
        
        
     
        #Variables for design of network
        #Composition at each interval boundary
        cl_init={}
        for j in model.j:
            for k in model.k:
                cl_init[j,k] = model.cl[j,k].value
        
        cr_init={}
        for i in model.i:
            for k in model.k:
                cr_init[i,k] = model.cr[i,k].value

        def cr_bounds(model,i,k):
            lb = model._rich_data.at[i,'Cout']
            ub = model._rich_data.at[i,'Cin']
            return (lb,ub)

        def cl_bounds(model,j,k):
            lb = model._lean_data.at[j,'Cin']
            ub = model._lean_data.at[j,'Cout']
            return (lb,ub)
        
        model.del_component(model.cr)
        model.del_component(model.cr_index)
                
        model.del_component(model.cl)
        model.del_component(model.cl_index) 
        
        model.cr = Var(model.i,model.k, initialize= cr_init, bounds = cr_bounds)
        model.cl = Var(model.j,model.k, initialize= cl_init, bounds = cl_bounds)
        
        #Composition at each interval boundary before mixing
        #enables non sio-compositional mixing
        
        def crin_bounds(model,i,j,k):
            lb = 0.0
            #Rich_data.at[i,'Cout']
            ub = 1
            return (lb,ub)

        def clin_bounds(model,i,j,k):
            lb = 0
            #Lean_data.at[j,'Cin']
            ub = 1
            return (lb,ub)

        def clin_init(model,i,j,k):
            return model.cl[j,k].value
        def crin_init(model,i,j,k):
            return model.cr[i,k].value

        #THESE HERE SHOULD BE INCLUDED VIA AN OPTION TO THE USER AS TO WHETHER THEY WOULD LIKE TO INCLUDE 
        #NON-ISOCOMPOSITIONAL MIXING

        model.crin = Var(model.i,model.j,model.k, initialize = crin_init, bounds=crin_bounds)
        model.clin = Var(model.i,model.j,model.k, initialize = clin_init, bounds=clin_bounds)
        
        #Amount of lean stream utilized
        model.del_component(model.avlean)
        model.avlean = Var(model.j, initialize=0.3, within=NonNegativeReals)
        
        #   Flowrate of splits for non iso-compositional mixing
        def Flrich_bounds(model,i,j,k):
            if model.y[i,j,k] ==1:
                return (0.00000000000000001, model._rich_data.at[i,'F'])
            else:
                return (0.000000,50)
    
        def Flrich_init(model,i,j,k):
            if k <= (model.nstages+1):
                return Constraint.Skip
            elif y(i,j,k)==1:
                if k in model.stages:
                    return (model.M[i,j,k].value/(model.cr[i,k].value-model.cr[i,k+1].value))
            else:
                return 0
            
         
        def Flean_bounds(model,i,j,k):
            if model.y[i,j,k] ==1:
                return (0.0,20.0)
            else:
                return (0.00,20.0)
    
        def Flean_init(model,i,j,k):
            if k == (model.nstages+1):
                return Constraint.Skip
            elif  y(i,j,k)==1 and k in model.stages == 1:
                return (model.M[i,j,k].value/(model.cl[j,k].value-model.cl[j,k+1].value))
            else:
                return 0   
            
        model.Flrich = Var(model.i,model.j,model.k, bounds= Flrich_bounds)
        
        model.Flean = Var(model.i,model.j,model.k, bounds=Flean_bounds)
        
        # non-isocompositional mixing flows in branches - Turn on with option
        def flv_init(model,i,j,k):
            if model.y[i,j,k] ==1:
                return 0.01
            #(model.Flean[i,j,k].value/model.Flrich[i,j,k].value)*((model.RHOG[i,j]/model.RHOL[j])**0.5)
            else:
                return 0.0 
        
        def flv_bounds(model,i,j,k):
            if model.y[i,j,k] ==1:
                return (0.0000000001,None)
            else:
                return 0.0 
        
        #model.flv = Var(model.i,model.j,model.k, within = NonNegativeReals)
        
        #positive/negative tolerance
        model.del_component(model.pnhc)
        model.del_component(model.pnhc_index)
        model.del_component(model.pnhc_index_index_0)
        model.del_component(model.snhc)
        model.del_component(model.snhc_index)
        model.del_component(model.snhc_index_index_0)
        model.pnhc=Var(model.i,model.j,model.k, initialize= 1e-6,within = NonNegativeReals)
        model.snhc=Var(model.i,model.j,model.k, initialize= 1e-6,within = NonNegativeReals)

        #mass transfer coefficient
        model.del_component(model.kya)
        model.del_component(model.kya_index)
        model.del_component(model.kya_index_index_0)
        model.kya=Var(model.i,model.j,model.k, initialize = 1, bounds = (0.00, None))
        
        #height of column
        model.hi = {}
        for i in model.i:
            for j in model.j:
                for k in model.k:
                    if model.y[i,j,k] == 1:
                        model.hi [i,j,k] = model.height[i,j,k].value
                    else:
                        model.hi [i,j,k] = 0
    
        def height_bounds(model, i,j,k):
            if model.y[i,j,k] ==1:
                return (0.0,None)
            else:
                return (0.0,None)

        model.del_component(model.height)
        model.del_component(model.height_index)
        model.del_component(model.height_index_index_0)
        model.height =  Var(model.i,model.j,model.k, initialize=model.hi, bounds=height_bounds)
        
        
        #==================================================================================
        #   CONSTRAINTS
        #==================================================================================
        #===============================================================================
        #===============================================================================
        model.del_component(model.CRichIn) 
        model.del_component(model.CRichIn_index)

        def CRichIn_(model, i,k):
            if model.first[k] == True:
                return model.cr[i,k] == (model._rich_data.at[i,'Cin'])

            else:
                return Constraint.Skip

        model.CRichIn = Constraint(model.i,model.k, rule=CRichIn_)
        
        model.del_component(model.CLeanIn) 
        model.del_component(model.CLeanIn_index)
        def CLeanIn_(model, j,k):
            if model.last[k] == True:
                return model.cl[j,k] == float(model._lean_data.at[j,'Cin'])
            else:
                return Constraint.Skip

        model.CLeanIn = Constraint(model.j, model.k, rule=CLeanIn_)

        model.del_component(model.CRichOut) 
        model.del_component(model.CRichOut_index)
        
        def CRichOut_(model, i,k):
            if (model.last[k])==True:
                return model.cr[i,k] == float(model._rich_data.at[i,'Cout'])
            else:
                return Constraint.Skip

        model.CRichOut = Constraint(model.i,model.k, rule=CRichOut_)
             
        model.del_component(model.CLeanOut) 
        model.del_component(model.CLeanOut_index)
        
        def CLeanOut_(model, j,k):
            if model.first[k] == True:
                return model.cl[j,k] == float(model._lean_data.at[j,'Cout'])        
            else:
                return Constraint.Skip

        model.CLeanOut = Constraint(model.j,model.k,rule=CLeanOut_)
        #EQUATIONS FOR NON_ISOCOMP MIXING
        #def FlowLV_(model,i,j,k):
        #    if y[i,j,k] == 1:
        #        return model.flv[i,j,k] == (model.Flean[i,j,k]/model.Flrich[i,j,k])*((model.RHOG[i]/model.RHOL[j])**0.5)
        #    else:
        #        return Constraint.Skip
    
        #model.FlowLV = Constraint(model.i, model.j, model.k, rule = FlowLV_)    
        
        
        model.del_component(model.Total_Mass_Rich) 
        def Total_Mass_Rich_(model,i):   
            f=(model._rich_data.at[i,'F'])*((model._rich_data.at[i,'Cin'])-(model._rich_data.at[i,'Cout'])) 
            return float(f)== sum(model.M[i,j,k] for j in model.j for k in model.k if model.y[i,j,k] == 1)                     
        
        model.Total_Mass_Rich = Constraint(model.i, rule = Total_Mass_Rich_)
        #for i in model.i:    
        #    print((self._rich_data.at[i,'F'])*((self._rich_data.at[i,'Cin'])-(self._rich_data.at[i,'Cout'])))
            
        model.del_component(model.Total_Mass_Lean) 
      
        def Total_Mass_Lean_(model,j):
            f=model.L1[j]*(((model._lean_data.at[j,'Cout'])-(model._lean_data.at[j,'Cin'])))
            c=f
            return model.L1[j]*(((model._lean_data.at[j,'Cout'])-(model._lean_data.at[j,'Cin']))) == sum(model.M[i,j,k] for i in model.i for k in model.k if model.y[i,j,k] == 1)
            
        model.Total_Mass_Lean = Constraint(model.j, rule = Total_Mass_Lean_)

        # stage stream overall mass balance
        model.del_component(model.Stage_Mass_Rich) 
        model.del_component(model.Stage_Mass_Rich_index)
        def Stage_Mass_Rich_(model,i,k):
    
            if k == (model.nstages+1):
                return Constraint.Skip
            elif k in model.stages:
    
                f =(model._rich_data.at[i,'F'])
                c=f
                return float(model._rich_data.at[i,'F'])*(model.cr[i,k]-model.cr[i,(k+1)])== sum(model.M[i,j,k] for j in model.j if model.y[i,j,k] == 1)

            else:
                return Constraint.Skip
    
        model.Stage_Mass_Rich = Constraint(model.i, model.k, rule = Stage_Mass_Rich_)
        
        model.del_component(model.Stage_Mass_Lean) 
        model.del_component(model.Stage_Mass_Lean_index)
        
        def Stage_Mass_Lean_(model,j,k):
    
            if k == (model.nstages+1):
                return Constraint.Skip
    
            elif k in model.stages:
                return model.L1[j]*(model.cl[j,k] - model.cl[j,(k+1)]) == \
                    sum(model.M[i,j,k] for i in model.i if model.y[i,j,k] == 1)
                
            else:
                return Constraint.Skip 
            
        model.Stage_Mass_Lean = Constraint(model.j,model.k, rule = Stage_Mass_Lean_)

        #Available mass in lean stream j
        model.del_component(model.AvLean)
        def AvLean_(model,j):
            a = (model._lean_data.at[j,'Cout'])-(model._lean_data.at[j,'Cin'])
            return model.avlean[j] == model.L1[j]*(a)

        model.AvLean = Constraint(model.j, rule=AvLean_)


        model.del_component(model.Monot_Rich) 
        model.del_component(model.Monot_Rich_index)

        # Checking that concentrations move in one direction
        def Monot_Rich_(model,i,k):
            if k == (model.nstages+1):
                return Constraint.Skip
            else:
                return model.cr[i,k] >= model.cr[i,(k+1)]

        model.Monot_Rich = Constraint(model.i, model.k, rule = Monot_Rich_)

        model.del_component(model.Monot_Lean) 
        model.del_component(model.Monot_Lean_index)

        def Monot_Lean_(model,j,k):
            if k == (model.nstages+1):
                return Constraint.Skip
            else:
                return model.cl[j,k] >= model.cl[j,(k+1)]

        model.Monot_Lean = Constraint(model.j, model.k, rule = Monot_Lean_)

        #Equations for non-isocomp mixing
        def Monot_RichSub_(model,i,j,k):
            if k == (model.nstages+1):
                return Constraint.Skip
            else:
                return model.cr[i,k] >= model.crin[i,j,(k+1)]

        model.Monot_RichSub = Constraint(model.i, model.j, model.k, rule = Monot_RichSub_)
    
        def Monot_LeanSub_(model,i,j,k):
            if k == (model.nstages+1):
                return Constraint.Skip
            else:
                return model.clin[i,j,k] >= model.cl[j,(k+1)]
    
        model.Monot_LeanSub = Constraint(model.i,model.j, model.k, rule = Monot_LeanSub_)

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




        # Mass balances over streams for non-iso-comp mixing
        def FlowRich_(model,i,k):
            if k == (model.nstages+1):
                return Constraint.Skip
            elif k in model.stages and model.y[i,j,k] == 1:
                #c = float(model._rich_data.at[i,'F'])
                print("We do get here.")
                print(model._rich_data.at[i,'F'])
                #print()
                return float(model._rich_data.at[i,'F']) == sum(model.Flrich[i,j,k] for j in model.j if model.y[i,j,k] == 1)
            else:
                return Constraint.Skip
    
        model.FlowRich = Constraint(model.i, model.k, rule = FlowRich_)
    
        def FlowLean_(model,j,k):
            if k == (model.nstages+1):
                return Constraint.Skip
            elif k in model.stages and model.y[i,j,k] == 1:
                return model.L1[j]== sum(model.Flean[i,j,k] for i in model.i if model.y[i,j,k]==1)
            else:
                return Constraint.Skip
    
        model.FlowLean = Constraint(model.j, model.k,  rule = FlowLean_)

        #Unit mass balances
        def ExUnitR_(model,i,j,k):
            if model.y[i,j,k] == 1:
              return model.Flrich[i,j,k]*(model.cr[i,k]-model.crin[i,j,(k+1)])== model.M[i,j,k]
            else:
                return Constraint.Skip
                
        model.ExUnitR = Constraint(model.i, model.j, model.k, rule = ExUnitR_)

        def ExUnitL_(model,i,j,k):
            if model.y[i,j,k] == 1:   
                return model.Flean[i,j,k]*(model.clin[i,j,k]-model.cl[j,(k+1)])== model.M[i,j,k]
            else:
                return Constraint.Skip    
        model.ExUnitL = Constraint(model.i, model.j, model.k, rule = ExUnitL_)
       
        model.del_component(model.Log_M_RPS_LPS) 
        model.del_component(model.Log_M_RPS_LPS_index)
        model.del_component(model.Log_M_RPS_LPS_index_index_0)
        
        def Log_M_RPS_LPS_(model,i,j,k):    
            c = ((model._rich_data.at[i,'F'])*((model._rich_data.at[i,'Cin'])-(model._rich_data.at[i,'Cout'])))
            c=(c)
            d=(model.L1[j]*(((model._lean_data.at[j,'Cout'])-((model._lean_data.at[j,'Cin'])))))
            if k in model.stages and model.y[i,j,k] == 1:
                if value(c) >=value(d):
                    return model.M[i,j,k] <= (model.L1[j]*(((model._lean_data.at[j,'Cout'])-((model._lean_data.at[j,'Cin'])))))*model.y[i,j,k]
                else:
                    return model.M[i,j,k] <= ((model._rich_data.at[i,'F'])*((model._rich_data.at[i,'Cin'])-(model._rich_data.at[i,'Cout'])))*model.y[i,j,k]
            else:
                return Constraint.Skip
    
        model.Log_M_RPS_LPS = Constraint(model.i, model.j, model.k, rule = Log_M_RPS_LPS_)
        
        #LOGICAL CONSTRAINT ON RICH SIDE COMPOSITION DIFFERENCE BETWEEN RPS(I) AND LPS(J)
        model.del_component(model.Log_DC_RPS_LPS_RS)
        model.del_component(model.Log_DC_RPS_LPS_RS_index)
        model.del_component(model.Log_DC_RPS_LPS_RS_index_index_0)
        def Log_DC_RPS_LPS_RS_(model,i,j,k):
            if k in model.stages and model.y[i,j,k] == 1:
                return model.dcin[i,j,k] <= model.cr[i,k] - model.clin[i,j,k]+ model.omega[i,j]*(1-model.y[i,j,k])
            else:
                return Constraint.Skip

        model.Log_DC_RPS_LPS_RS = Constraint(model.i, model.j, model.k, rule = Log_DC_RPS_LPS_RS_)

        model.del_component(model.Log_DC_RPS_LPS_RS1)
        model.del_component(model.Log_DC_RPS_LPS_RS1_index)
        model.del_component(model.Log_DC_RPS_LPS_RS1_index_index_0)        
        def Log_DC_RPS_LPS_RS1_(model,i,j,k):
            if k in model.stages and model.y[i,j,k] == 1:
                return model.dcin[i,j,k] >= model.cr[i,k] - model.clin[i,j,k]- model.omega[i,j]*(1-model.y[i,j,k])
            else:
                return Constraint.Skip
        model.Log_DC_RPS_LPS_RS1 = Constraint(model.i, model.j, model.k, rule = Log_DC_RPS_LPS_RS1_)

        #LOGICAL CONSTRAINT ON Lean SIDE COMPOSITION DIFFERENCE BETWEEN RPS(I) AND LPS(J)
        model.del_component(model.Log_DC_RPS_LPS_LS)
        model.del_component(model.Log_DC_RPS_LPS_LS_index)
        model.del_component(model.Log_DC_RPS_LPS_LS_index_index_0)
        def Log_DC_RPS_LPS_LS_(model,i,j,k):
            if k in model.stages and model.y[i,j,(k)] == 1:
                return model.dcout[i,j,(k+1)] <= model.crin[i,j,(k+1)] - model.cl[j,(k+1)]+\
                                                 model.omega[i,j]*(1-model.y[i,j,k])
            else:
                return Constraint.Skip
        model.Log_DC_RPS_LPS_LS = Constraint(model.i, model.j, model.k, rule = Log_DC_RPS_LPS_LS_)
        
        model.del_component(model.Log_DC_RPS_LPS_LS1)
        model.del_component(model.Log_DC_RPS_LPS_LS1_index)
        model.del_component(model.Log_DC_RPS_LPS_LS1_index_index_0)
        def Log_DC_RPS_LPS_LS1_(model,i,j,k):
            if model.y[i,j,k] == 1:
                return model.dcout[i,j,(k+1)] >= model.crin[i,j,(k+1)] - model.cl[j,(k+1)] -\
                                     model.omega[i,j]*(1-model.y[i,j,k])
            else:
                return Constraint.Skip

        model.Log_DC_RPS_LPS_LS1 = Constraint(model.i, model.j, model.k, rule = Log_DC_RPS_LPS_LS1_)        
        
        model.del_component(model.KYTransferMass)
        model.del_component(model.KYTransferMass_index)
        model.del_component(model.KYTransferMass_index_index_0)
        def KYTransferMass_(model, i,j,k):
            if model.y[i,j,k]==1:
                return model.kya[i,j,k]==model.kw*model.surfA[i,j,k]*model.surfAcor[i,j,k]*model.kwcor[i,j,k]
            else:
                return Constraint.Skip
    
        model.KYTransferMass = Constraint(model.i, model.j, model.k, rule = KYTransferMass_) 
        
        model.del_component(model.HeightColumn)
        model.del_component(model.HeightColumn_index)
        model.del_component(model.HeightColumn_index_index_0)
        def HeightColumn_(model,i,j,k):
            if model.y[i,j,k] == 1:
                return model.height[i,j,k] == model.y[i,j,k]*model.M[i,j,k]/(((model.kya[i,j,k]*np.pi/4*((model.dia[i,j,k]*model.diacor[i,j,k])**2))) *\
                                          (((1e-8+model.dcin[i,j,k]*model.dcout[i,j,(k+1)])*\
                                           (model.dcin[i,j,k]+model.dcout[i,j,(k+1)])*0.5 + 1e-8)**(0.33333)+1e-8))
            else:
                return Constraint.Skip

        model.HeightColumn = Constraint(model.i, model.j, model.k, rule = HeightColumn_)
        
        #def massexchanger():
            #In here we will call the mass exchanger function and return the height
            
        #heightEx = ExternalFunction(massexchanger)
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
                        tac += model.AF*np.pi*((model.dia[i,j,k]*model.diacor[i,j,k])**2)/4*model.height[i,j,k]*model.heightcor[i,j,k]*model.packcost[i,j,k]*model.packcostcor[i,j,k]
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
        
        #results = self.solve_until_feas_MINLP(model)
        #==================================================================================
        #   POSTPROCESSING AND DISPLAY AND RETURN
        #==================================================================================
        #model.write(filename="MENS1", format = ProblemFormat.nl,io_options={"symbolic_solver_labels":True})
        #results.pprint
        
        #display (model)
        #model.display()

 
        #Use this line for solving:
        # pyomo solve synheat.py --solver=./../../Couenne/build/bin/couenne
        #opt = SolverFactory('./../../Couenne/build/bin/couenne')
        #opt = SolverFactory('./../../BARON/baron')
        #opt = SolverFactory('bonmin')
        
        #options = {}
        #options['max_iter'] =20000
        print ("BEGINNING THE NLP SUBOPTIMIZATION")
        #model.pprint()
        #solver=SolverFactory('gams')

        #results = solver.solve(model,tee=True, solver = 'baron')
        #opt = SolverFactory('baron')
        #instance = model.create_instance()
        #model.write("MENS_nlp_nl.nl", format=ProblemFormat.nl)
        
        
        #optTRF = SolverFactory('trustregion')
        #optTRF.solve(m, [heightEx])
        
        
        results= self.solve_until_feas_NLP(model)
        #results = opt.solve(model)
        #model.write(filename="MENS1", format = ProblemFormat.nl,io_options={"symbolic_solver_labels":True})
        results.pprint
        print(results)
        #model.display()
        #model.height.pprint()
        #model.M.pprint()
        #model.L.pprint()
        #model.cr.pprint()
        #model.cl.pprint()
        #model.dcin.pprint()
        #model.dcout.pprint()
        print("THIS IS THE END OF THE NLP SUBOPTIMIZATION")
        
        return model
        
        
        
        
        