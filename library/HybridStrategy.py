#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 28 14:18:39 2018

Mass exchanger network synthesis in Pyomo

This script is for the wrapping and iterations of the 2-step synthesis of
Mass Exchanger Networks, as published by Short, M., Isafiade, AJ., Biegler, LT.,
Kravanja, Z., 2018, Synthesis of mass exchanger networks in a two-step hybrid 
optimization strategy, Chem Eng Sci, 178, 118-135

@author: mchlshort
"""
from __future__ import division
from pyomo.environ import *
import pandas as pd
import os
import inspect
import numpy
import time
import sys

from pyomo.opt import SolverFactory, ProblemFormat, TerminationCondition
from library.MassExchanger import *
from library.MENS_MINLP import *
from library.SubOptMENS import *

__author__ = "Michael Short"
__copyright__ = "Copyright 2020"
__credits__ = ["Michael Short, Lorenz T. Biegler, Adeniyi J. Isafiade"]
__license__ = "GPL-3"
__version__ = "0.9"
__maintainer__ =  "Michael Short"
__email__ = "m.short@surrey.ac.uk"
__status__ = "Development"

def write_to_csv(filename, data):
    """
    writes the data provided (in form of dictionary) to a csv. CSV will be outputted into folder
    that the program is run in.
        
    Args:
        filename: filename provided by user eg ("costs.csv")
        data (dict): dictionary data to be written
            
    returns:
        None
            
    """
    df = pd.DataFrame.from_dict(data, orient="index")
    df.to_csv(filename)

class HybridStrategy(object):
    """Implements the hybrid strategy for MENS proposed by Short et al. (2018). 
    
    This class includes all the functions required to call the Mass exchanger
    network synthesis, MENS_MINLP, as well as the individual exchanger class, MassExchangerNLP.
    The class perform the passing of information between, saving, and iterating of
    the two-step hybrid starteg detailed in the aforementioned paper.    
    """
    def __init__(self):
        """
        __init__ method for HybridStrategy class.
        
        Args:
            None    
        """  
        self.corrections = dict()
        self.best_network_MINLP = None
        self.best_exchangers = dict()
        self.best_objective_real = None
        self.best_objective_MINLP = None
        self.MENval_log = dict()
        self.NLP_log = dict()
        self.iter_count = 0
        self.diff_NLP_MINLP_log = dict()
        self.correction_log = dict()
        self.best_net_iter = 0
        self.tol = 0.02
        self.solution_log = dict()
        self.MINLP_TAC_log = dict()
        self.exchanger_log = dict()
        self.capcost_log_MINLP= dict()
        self.capcost_log_nlp = dict()
        self.failed_exchanger = dict()
        self.utility_cost = dict()
        self.binary_cuts = dict()
        self.symmetry_cuts = dict()
        
    def _obtain_initializations(self, MENS_model,i,j,k):
        """This function is used to get the initializations for the individual mass exchanger 
        optimization from the solutions of the MINLP
        
            Args:
                MENS_model (Pyomo model): the solved MINLP model from MENS_MINLP module
                i (str): name of the rich process stream
                j (str): name of the lean process stream
                k (int): the interval of the match
                
            Returns:
                dict: dictionary containing index of the name of the parameter/var and the value of the initialization
    
        """ 
        ME_inits = dict()
        ME_inits["height"]=MENS_model.height[i,j,k].value*MENS_model.heightcor[i,j,k]
        ME_inits["kw"]=float(value(MENS_model.kw))
        ME_inits["kwcor"]=float(value(MENS_model.kwcor[i,j,k]))
        ME_inits["surfarea"]=float(value(MENS_model.surfA[i,j,k]))
        ME_inits["surfacor"]=float(value(MENS_model.surfAcor[i,j,k]))
        ME_inits["diameter"]=float(value(MENS_model.dia[i,j,k]))
        ME_inits["diacor"]=float(value(MENS_model.diacor[i,j,k]))
        ME_inits["packcostcor"]=float(value(MENS_model.packcostcor[i,j,k]))
        ME_inits["packcost"]=float(value(MENS_model.packcost[i,j,k]))
        return ME_inits
        
    def _apply_cor_filter(self, correction):
        """Ensures that the correction factor is filtered so that the value is not 
        over-corrected between successive iterations.
        
        Args:
            correction (float): value of correction obtained from _get_correction_factors
            
        returns:
            float: filtered correction factor
            
        """
        if correction >= (self.cor_filter_size +1):
            correction = self.cor_filter_size +1
        elif correction <= (1-self.cor_filter_size):  
            correction =1-self.cor_filter_size
        else:
            correction=correction
        return correction   
    
    def _get_correction_factors(self, MENS_model, ME_model, men_type = 'nlp'):
        """Obtains the correction factors by comparing the values from the MINLP and NLP suboptimization.
        
        The corrections are returned already filtered.
        
        Args:
            MENS_model (pyomo model): solved pyomo model from MENS_MINLP module
            ME_model (dict, pyomo models): a dictionary containing each of the solved pyomo models
                                            of the relevant NLP sub-optimization   
        
        returns:
            corrections (dict): returns a dictionary containing each of the relevant filtered corrections
                                with the index referring to the number of the match and the correction type and
                                the value being the filtered correction value.
                                
        """ 
        corrections = dict()
        kwcor = dict()
        diacor = dict()
        heightcor = dict()
        packcostcor=dict()
        surfAcor = dict()
        m = 0
        for i in MENS_model.i:
            for j in MENS_model.j:
                for k in MENS_model.k:
                    yvals = {}
                    if men_type == 'minlp':
                        yvals[i,j,k] = value(MENS_model.y[i,j,k])                            
                    else:
                        yvals[i,j,k] = MENS_model.y[i,j,k]
                        
                    if yvals[i,j,k]>=0.99 and MENS_model.M[i,j,k].value!=0 and m in ME_model:
                        if ME_model[m].success== True:
                            #should possibly have a way here to tell whether the exchanger model solved correctly
                            #if it didn't then we should set the correction to 1 for this iteration
                            kw_c = ME_model[m].koga.value/(MENS_model.kw*MENS_model.kwcor[i,j,k])
                            kwcor = self._apply_cor_filter(kw_c)
                            corrections[m,"kwcor"]=kwcor*MENS_model.kwcor[i,j,k]
                            dia_c = ME_model[m].diameter.value/(MENS_model.dia[i,j,k]*MENS_model.diacor[i,j,k])
                            diacor = self._apply_cor_filter(dia_c) 
                            corrections[m,"diacor"] = diacor*MENS_model.diacor[i,j,k]
                            height_c = ME_model[m].height.value/(MENS_model.height[i,j,k].value*MENS_model.heightcor[i,j,k])
                            heightcor = self._apply_cor_filter(height_c) 
                            corrections[m,"heightcor"] = heightcor*MENS_model.heightcor[i,j,k]
                            packcost_c = ME_model[m].PackCost.value/(MENS_model.packcost[i,j,k]*MENS_model.packcostcor[i,j,k])
                            x = self._apply_cor_filter(packcost_c)
                            corrections[m,"packcostcor"] = x*MENS_model.packcostcor[i,j,k]
                            surfA_c = ME_model[m].SpecAreaPacking.value/(MENS_model.surfAcor[i,j,k]*MENS_model.surfA[i,j,k])
                            surfAcor = self._apply_cor_filter(surfA_c)
                            corrections[m,"surfAcor"] = surfAcor*MENS_model.surfAcor[i,j,k]
                        else:
                            corrections[m,"kwcor"] = MENS_model.kwcor[i,j,k]
                            corrections[m,"diacor"] = MENS_model.diacor[i,j,k]
                            corrections[m,"heightcor"] = MENS_model.heightcor[i,j,k]
                            corrections[m,"packcostcor"] = MENS_model.packcostcor[i,j,k]
                            corrections[m,"surfAcor"] = MENS_model.surfAcor[i,j,k] 
                        
                    else:
                        corrections[m,"kwcor"] = MENS_model.kwcor[i,j,k]
                        corrections[m,"diacor"] = MENS_model.diacor[i,j,k]
                        corrections[m,"heightcor"] = MENS_model.heightcor[i,j,k]
                        corrections[m,"packcostcor"] = MENS_model.packcostcor[i,j,k]
                        corrections[m,"surfAcor"] = MENS_model.surfAcor[i,j,k]   
                    m += 1
                    
        return corrections   
  
    def _check_convergence(self, MENS_model, exchanger_models, m, tol = 0.02, previous_corrections=None, men_type = 'nlp'):
        """Convergence checking for the iterative procedure.
        
        This function compares the previous solutions 2 solutions as well as the globally best solution
        thus far attained. It decides whether to continue iterating or whether to return the best
        network to the user.
        
        Args:
            MENS_model (pyomo model):   solved pyomo model from MENS_MINLP module
            ME_model (dict, pyomo models): a dictionary containing each of the solved pyomo models
                                            of the relevant NLP sub-optimization   
            m (int):                    number of matches
            tol (int, default= 0.02):   the tolerance set by the user for when to stop the iterations, refers
                                            to the percentage difference between all correction factors between 
                                            iterations
            previous_corrections (dict, optional): The dictionary containing corrections for each match.
                                            Only to be used in the case of restarting the problem after a failed
                                            iteration when the user knows the last sets of corrections
                                            
            men_type (str): tells us if we have the MINLP or NLP subopt as optimal
        
        Returns:
            bool (boolean): returns True if model is converged within tolerance or False if not 
            
        """
        #First we compare the old and new objective function values
        print("CHECKING FOR CONVERGENCE for iteration number: ", self.iter_count)
        MENval = MENS_model.TACeqn()
        print("MINLP objective function value is ",MENval)
        if self.best_objective_MINLP == None:
            self.best_network_MINLP = MENS_model
            self.best_objective_MINLP = MENval
        elif MENval <= self.best_objective_MINLP:
            self.best_objective_MINLP = MENval
            self.best_network_MINLP = MENS_model
        else:
            pass
        
        self.MENval_log[self.iter_count] = MENval
               
        #print(type(MENS_model.TACeqn()))
        capval = 0
        count = 0
        #print(exchanger_models)
        nlp_exshelval = 0
        nlp_packcost = 0
        discard = False
        exchangers = 0
        for i in MENS_model.i:
            for j in MENS_model.j:
                for k in MENS_model.k:
                    print("do we get here?")
                    yvals = {}
                    if men_type == 'minlp':
                        yvals[i,j,k] = value(MENS_model.y[i,j,k])                            
                    else:
                        yvals[i,j,k] = MENS_model.y[i,j,k]
                    
                    if yvals[i,j,k]>=0.99 and MENS_model.M[i,j,k].value!=0 and count in exchanger_models:
                        r=exchanger_models[count].Obj4()
                        nlp_exshelval += value(exchanger_models[count].AF)*23805*(value(exchanger_models[count].diameter)**0.57)*1.15*value(exchanger_models[count].height) 
                        nlp_packcost += value(exchanger_models[count].AF)*pi*(value(exchanger_models[count].diameter)**2)/4*value(exchanger_models[count].height)*value(exchanger_models[count].PackCost)
                        capval+=r
                        print("exchanger.success for exchanger ", i,j,k, "=", exchanger_models[count].success)
                        exchangers += 1
                        if exchanger_models[count].success == False:
                            discard = True
                            print("DISCARD THIS NLP SOLUTION. At least 1 model failed")
                    count+=1
        print("NLP MEX shell costs: ", nlp_exshelval) 
        print("NLP MEX pack costs: ", nlp_packcost) 
        print("NLP MEX cap costs: ", capval) 
        minlpcapcost=0 
        minlpshellcost=0
        minlppackcost=0
        for i in MENS_model.i:
            for j in MENS_model.j:
                for k in MENS_model.k:
                    minlpshellcost += value(MENS_model.AF)*23805*((value(MENS_model.diacor[i,j,k])*value(MENS_model.dia[i,j,k]))**0.57)*1.15*value(MENS_model.heightcor[i,j,k])*value(MENS_model.height[i,j,k]) 
                    minlppackcost += value(MENS_model.AF)*numpy.pi*((value(MENS_model.dia[i,j,k])*value(MENS_model.diacor[i,j,k]))**2)/4*value(MENS_model.height[i,j,k])*value(MENS_model.heightcor[i,j,k])*value(MENS_model.packcost[i,j,k])*value(MENS_model.packcostcor[i,j,k])                      
        
        print("MINLP shell costs:", minlpshellcost)
        print("MINLP pack costs:", minlppackcost)
        minlpcapcost=minlppackcost+minlpshellcost
        print("MINLP cap costs:", minlpcapcost)
        
        fixcosts = 0
        for i in MENS_model.i:
            for j in MENS_model.j:
                for k in MENS_model.k:
                    fixcosts+=(value(MENS_model.fixcost)*value(MENS_model.y[i,j,k]))
        print("NLP MEX fix costs: ", fixcosts) 
        utilitycosts = 0
        for j in MENS_model.j:
            utilitycosts += value(MENS_model.L1[j])*value(MENS_model.AC[j])
        print("NLP MEX utility costs: ", utilitycosts)     
        realval = capval+ fixcosts+ utilitycosts
        
        print("NLP objective function value is ",realval)
        if discard == False:
            
            if self.best_objective_real == None:
                self.best_objective_real = realval
                self.best_exchangers = exchanger_models
                self.best_net_iter = self.iter_count
            elif realval <= self.best_objective_real:
                self.best_objective_real = realval
                self.best_net_iter = self.iter_count
                self.best_exchangers = exchanger_models
            else:
                pass
        else:
            print("THIS NLP WAS NOT SOLVED CORRECTLY AND THESE VALUES CAN THEREFORE NOT BE INcLUDED")
        self.NLP_log[self.iter_count] = realval
        
        per_diff = ((realval-MENval)/realval)*100
        print("difference between real solution and MINLP solution is (%):", per_diff)
        
        
        self.solution_log[self.iter_count] = realval
        self.MINLP_TAC_log [self.iter_count] = MENval
        self.exchanger_log[self.iter_count] = exchangers
        self.capcost_log_MINLP[self.iter_count] = minlpcapcost
        self.capcost_log_nlp[self.iter_count] = capval
        self.failed_exchanger[self.iter_count] = discard
        self.utility_cost[self.iter_count] = utilitycosts
        
        self.diff_NLP_MINLP_log[self.iter_count]=per_diff
        stop_flag1 = False

        if abs(per_diff) <= tol*100:
            stop_flag1 = True
        
        previous_corrections=self.corrections
        new_cors = self._get_correction_factors(MENS_model,exchanger_models, men_type = men_type)
        self.correction_log[self.iter_count]=new_cors
        if bool(previous_corrections) == False:
            print("Is this false?")
            for i in new_cors:
                previous_corrections[i] = 1
        
        # second we compare the correction factors 
        stop_flag2 = False
        stop_dict = dict()
        if self.iter_count>=2:
            stop_flag2 = True
            for i in new_cors:

                comp = new_cors[i]/previous_corrections[i]

                if comp >= 1 + tol:
                    stop_dict[i] = False

                elif comp <= 1 - tol:
                    stop_dict[i] = False

                else:
                    stop_dict[i] = True
                    
        for k,v in stop_dict.items():
            if v == False:
                stop_flag2 = False
                
        print("Stop_flag 1 = difference between MINLP and NLP", stop_flag1)   
        print("Stop_flag 2 = difference between correction factors", stop_flag2)          
        if stop_flag2 == True or stop_flag1 == True and self.best_objective_real != None:
            print("either flag is true. This means that the solution was found")
            return True
        else:
            return False
        
    def _generate_binary_cut(self, MENS_model, iteration):
        """Binary cut generator for the MINLP model
        
        This function removes the specific binary combination from the previous iterations and stores them
        a dictionary. This dictionary is then used in subsequent MINLP steps to remove the specific binary
        combination.
        
        Args:
            MENS_model (pyomo model):   solved pyomo model from HENS_MINLP module
            interation (int): iteration number
        
        Returns:
            None 
        """
        cut_pack = dict()
        for i in MENS_model.i:
            for j in MENS_model.j:
                for k in MENS_model.stages:
                    cut_pack[i,j,k] = MENS_model.y[i,j,k].value
        print("cut_pack",cut_pack)

        print("Trying to detect equivalent networks:")
        canplus1 = True
        canminus1 = True
        for i in MENS_model.i:
            for j in MENS_model.j:
                for k in MENS_model.stages:
                    if MENS_model.y[i,j,k].value == 1 and k == 1:
                        canminus1 = False
                        print("Can minus 1? ", canminus1)
                    elif MENS_model.y[i,j,k].value == 1 and MENS_model.nstages == k:
                        canplus1 = False
                        print("Can plus 1? ", canplus1)
                        
        print("Can minus 1? ", canminus1)
        print("Can plus 1? ", canplus1)                
        sym_cuts = None
        '''
        if canplus1:   
            sym_cuts  = dict()                
            for i in HENS_model.i:
                for j in HENS_model.j:
                    for k in HENS_model.stages:
                        if HENS_model.first[k] == True:
                            sym_cuts[i,j,k] = 0
                        else:
                            sym_cuts[i,j,k] = HENS_model.z[i,j,k-1].value
        
        if canminus1:
            sym_cuts  = dict() 
            for i in HENS_model.i:
                for j in HENS_model.j:
                    for k in HENS_model.stages:
                        if HENS_model.last[k] == True:
                            sym_cuts[i,j,k] = 0
                        else:
                            sym_cuts[i,j,k] = HENS_model.z[i,j,k+1].value
                            
        print("sym_cut_pack",sym_cuts)  
        '''              
        self.binary_cuts[iteration] = cut_pack
        self.symmetry_cuts[iteration] = sym_cuts
        
        
    def run_hybrid_strategy(self, max_iter=None, cor_filter_size=None,rich_data=None,lean_data=None, correction_factors = None, parameter_data=None, stream_properties = None, tol = 0.02, exname = None, non_iso = True, stages = None, superstruct = 'SBS', bin_cuts = False):
        """Starts the hybrid strategy iterative procedure by solving MINLP and NLP problems
        
        This function will be called by the user when they want to run the 
        full strategy. It will run sequential problems of the MENS and NLP MEs 
        until convergence, or there is an infeasible subproblem, or a maximum number 
        of iterations is reached
        
        Args:
            max_iter (int, optional):       default = 100. The number of maximum iterations for the solve, if
                                            no convergence was attained
            cor_filter_size (int, optional): default = 0.5. User should input small number (0.02). 
                                            Represents the allowable change as a percentage between runs (0.02=2%)
                                            default value means corrections are essentially not filtered.
            rich_data (pandas DataFrame):   DataFrame of rich stream name, concentration in, concentration out and flowrates.
            lean_data (pandas DataFrame):   DataFrame of lean stream name, concentration in, concentration out and flowrates.
            correction_factors (dictionary): Dictionary of all correction factors
            parameter_data (pandas DataFrame): DataFrame of problem-specific parameters.
            tol (int,optional):             default = 0.02. Number that represents the maximum change of correction factors required between 
                                            iterations to terminate the program 
            non_iso (bool, optional):       True/False for whether to solve the suboptimization with non-isocompositional mixing. Default = True
            stages (int, optional):         Number of stages for the stagewise superstructure
            superstructure (str,optional):  The type of superstructure to be used. SBS and SWS currently supported
            bin_cut (bool, optional):       If True, binary cut is generated to exclude a particular set of binary variables from all 
                                            future iterations. Default is False.
        
        Returns:
            print that tells the user that the iterations have ended
            
        """
        if isinstance(max_iter, int):
            pass
        elif max_iter == None:
            print("No maximum iterations set! Default value is 100")
            max_iter=100
        else:
            raise RuntimeError("Must input an integer or leave to default")
            
        if isinstance(stages, int):
            pass
        elif stages == None:
            print("No stages set so default is chosen i.e. max(process streams)+1")
            stages = None
        else:
            raise RuntimeError("Must input an integer or leave to default for stages")
        
        if isinstance(non_iso, bool):
            pass
        else:
            raise RuntimeError("Must input an integer or leave to default for stages")
        
        self.cor_filter_size = cor_filter_size    
        if isinstance(self.cor_filter_size, (int, float)):
            pass
        elif self.cor_filter_size == None:
            print("No filter size is given by user! This means that the correction factors change drastically between iterations. This could result in solutions being excluded.")
            self.cor_filter_size=0.5
        else:
            raise RuntimeError("Must input a number or leave to default")
        print(type(superstruct))
        print(superstruct)
        if not isinstance(superstruct, str):
            raise RuntimeError("Must input superstructure type as string")
        #elif superstruct != 'SBS' or superstruct != 'SWS':
        #    raise RuntimeError("Must input superstructure type as string as 'SWS' or 'SBS'")
        else:
            pass
        
        print('User-defined tolerance for correction factors: ', tol)
        print('User-defined maximum number of iterations: ', max_iter)
        print('User-defined correction factor filter: ', self.cor_filter_size)
        self.tol = tol
        #initialize the MENS class here with the data from files. Replace this with values from provide_problem_data eventually
        Ex1MEN = MENS(rich_data=rich_data,lean_data=lean_data, correction_factors = correction_factors, parameter_data=parameter_data, stream_properties = stream_properties, stages = stages, superstruct = superstruct)

        #begin the iterative procedure
        for ic in range(max_iter):
            print("------------------------------------------------------------------------------------------------------------------------------------")
            print("------------------------------------------------------------------------------------------------------------------------------------")
            print("------------------------------------------ITERATION NUMBER: ", ic, "-----------------------------------------------------------")
            print("------------------------------------------------------------------------------------------------------------------------------------")
            print("------------------------------------------------------------------------------------------------------------------------------------")
            iter_time = time.clock()
            #these values are the initial values used to select matches between the NLP initialization of the MINLP and the MINLP
            min_height=0.01
            #min_mass_ex = 1e-7
            #initialize the MINLP with the NLP
            MEN_init, success_init = Ex1MEN.NLP_MENS_init(correction_factors=self.corrections)
            print("Values used in the initialisation")
            MEN_init.height.pprint()
            MEN_init.M.pprint()
            MEN_init.L.pprint()
            MEN_init.cr.pprint()
            MEN_init.cl.pprint()
            MEN_init.dcin.pprint()
            MEN_init.dcout.pprint()
            MEN_init.y.pprint()
            #attempt to solve the first MINLP
            currentOmega = MEN_init.omega
            if success_init == True:
                MENS_solved,results = Ex1MEN.MINLP_MENS_full(MEN_init, min_height_from_nlp=min_height, bin_cuts = self.binary_cuts)
            else:
                MENS_solved,results = Ex1MEN.MINLP_MENS_full(MEN_init, bin_cuts = self.binary_cuts)
            #the aim of this loop is to make the MINLP more robust by changing which heights from the NLP are included in the MINLP
            #not sure how rigorous this really is as it only changes the selected matches by lowering the heights and masses
            #exchanged between the NLP and MINLP. Exits the program if no solution is found to MINLP.
            #would like to include more options and solvers for this (and different OMEGAs and EMACs)
            
            if (results.solver.termination_condition == TerminationCondition.infeasible) or (results.solver.termination_condition == TerminationCondition.maxIterations):  
                #change for a while loop with a max iter
                for i in range(20):
                    print("MINLP didn't solve, attempting new matches")  
                    mh=min_height/((i+1)*5)
                    #print("mh",mh)
                    MEN_init = Ex1MEN.NLP_MENS_init(correction_factors=self.corrections)
                    MENS_solved,results = Ex1MEN.MINLP_MENS_full(MEN_init,min_height_from_nlp=(mh), bin_cuts = self.binary_cuts)
                    
                    if (results.solver.status == SolverStatus.ok) and (results.solver.termination_condition == TerminationCondition.optimal):
                        print("MINLP solved")
                        if bin_cuts ==True:
                            self._generate_binary_cut(MENS_solved, ic)
                        break
                    #elif (results.solver.termination_condition == TerminationCondition.infeasible) or (results.solver.termination_condition == TerminationCondition.maxIterations):  
                    #    print("MINLP didn't solve, attempting new matches")  
                    #    mm=min_mass_ex/((i+1)*10)
                    #    #print("mm", mm)
                    #    MEN_init = Ex1MEN.NLP_MENS_init(correction_factors=self.corrections)
                    #    MENS_solved,results = Ex1MEN.MINLP_MENS_full(MEN_init,min_height_from_nlp=(mh),min_mass_ex_from_nlp=mm)
                    #    if (results.solver.status == SolverStatus.ok) and (results.solver.termination_condition == TerminationCondition.optimal):
                    #        print("MINLP solved")
                    #        break
                    for i in range(50):
                        if (results.solver.termination_condition == TerminationCondition.infeasible) or (results.solver.termination_condition == TerminationCondition.maxIterations):  
                            print("MINLP didn't solve, attempting new matches with diff omega")
                            omegaNew = currentOmega/1.5
                            MEN_init = Ex1MEN.NLP_MENS_init(correction_factors=self.corrections, omega = omegaNew)
                            MENS_solved,results = Ex1MEN.MINLP_MENS_full(MEN_init, omega=omegaNew)
                            
                            print("new Omega", omegaNew)
                            if (results.solver.status == SolverStatus.ok) and (results.solver.termination_condition == TerminationCondition.optimal):
                                print("MINLP solved")
                                if bin_cuts ==True:
                                    self._generate_binary_cut(MENS_solved, ic)
                                break
                            else: 
                                currentOmega = omegaNew 
            else:
                print("The first solve of the MINLP is feasible")
                if bin_cuts ==True:
                    self._generate_binary_cut(MENS_solved, ic)
            
            #print(MENS_solved)
            #print(results)
            MENS_solved.height.pprint()
            MENS_solved.M.pprint()
            MENS_solved.L1.pprint()
            MENS_solved.cr.pprint()
            MENS_solved.cl.pprint()
            MENS_solved.dcin.pprint()
            MENS_solved.dcout.pprint()
            MENS_solved.y.pprint()
            print("Original objective func")
            print(MENS_solved.TACeqn())
            orig_ob = MENS_solved.TACeqn()
            con = True
            if  (results.solver.termination_condition == TerminationCondition.infeasible) or (results.solver.termination_condition == TerminationCondition.maxIterations): 
                print("The MINLP model for iteration ", ic, "failed to solve. Without a valid network model the program will terminate")
                print("The current best solution for the NLP was found at iteration: ", self.best_net_iter)
                print("Optimal solution for NLP: ", self.best_objective_real) 
                con = False

            #Now we build the NLP from the MINLP solution
            orig=True
            if non_iso and con:
                MENS_solved1 =MENS_solved.clone()
                MENS_solvedclone = MENS_solved1
                Ex1TR=SubOptMENS(MENS_solvedclone)
                MENS_solvedsub, results, success_subopt = Ex1TR.run_suboptimization()
                MENS_solvedsub.height.pprint()
                MENS_solvedsub.M.pprint()
                MENS_solvedsub.L1.pprint()
                MENS_solvedsub.avlean.pprint()
                MENS_solvedsub.cr.pprint()
                MENS_solvedsub.cl.pprint()
                MENS_solvedsub.dcin.pprint()
                MENS_solvedsub.dcout.pprint()
                MENS_solvedsub.Flrich.pprint()
                MENS_solvedsub.Flean.pprint()
                #MENS_solved.flv.pprint()
                MENS_solvedsub.clin.pprint()
                MENS_solvedsub.crin.pprint()
                MENS_solvedsub.y.pprint()
                if success_subopt == False: 
                    print("The NLP subopt model for iteration ", ic, "failed to solve. Without a valid network model the original MINLP is taken as solution")
                    print("The current best solution for the NLP was found at iteration: ", self.best_net_iter)
                    print("Optimal solution for NLP: ", self.best_objective_real) 
                    if con == False:
                        sys.exit()
                    con = True
                print("Subopt objective func")
                if success_subopt == True:
                    print(MENS_solvedsub.TACeqn())
                    subobj = MENS_solvedsub.TACeqn()
                else:
                    subobj = 1000000000000000
                print("Original objective func")
                print(MENS_solved.TACeqn())
                orig = False
                men_type = str()
                if con == True:
                    if subobj < MENS_solved.TACeqn():
                        orig = False
                        men_type = 'nlp'
                        print("SUBOPT with non isocomp is better")
                        #Replace original model with sub
                        MENS_solved = MENS_solvedsub
                    else:
                        orig = True
                        men_type = 'minlp'
                        print("ORIGINAL MINLP BETTER THAN SUBOPT, so orig is chosen")
                
                print(orig_ob)
            #m is the counter for all possible matches and also is the key for correction factors
            m = 0
            exchanger_models=dict()
            
            #This loop runs the individual exchanger model optimizations
            for i in MENS_solved.i:
                for j in MENS_solved.j:
                    for k in MENS_solved.k:
                        yvals = {}
                        if orig == True:
                            yvals[i,j,k] = value(MENS_solved.y[i,j,k])                            
                        else:
                            yvals[i,j,k] = MENS_solved.y[i,j,k]
                            
                        if yvals[i,j,k]>=0.99 and MENS_solved.M[i,j,k].value!=0 and con:
                            print("SETTING UP THE PROBLEM FOR MATCH [i,j,k] = ", i,j,k)
                            CRin_Side = {}
                            if orig == True:
                                CRin_Side[i] = MENS_solved.cr[i,k].value
                                CRin_Side[j] = MENS_solved.cl[j,k].value                                
                            else:
                                CRin_Side[i] = MENS_solved.cr[i,k].value
                                CRin_Side[j] = MENS_solved.clin[i,j,k].value

                            CRout_Side = {}                            
                            if orig == True:
                                CRout_Side[i] = MENS_solved.cr[i,(k+1)].value
                                CRout_Side[j] = MENS_solved.cl[j,(k+1)].value                                
                            else:
                                CRout_Side[i] = MENS_solved.crin[i,j,(k+1)].value
                                CRout_Side[j] = MENS_solved.cl[j,(k+1)].value

                            FlowM = {}
                            if orig == True:
                                FlowM[i] = MENS_solved.M[i,j,k].value/(MENS_solved.cr[i,k].value-MENS_solved.cr[i,(k+1)].value)
                                FlowM[j] = MENS_solved.M[i,j,k].value/(MENS_solved.cl[j,k].value-MENS_solved.cl[j,(k+1)].value)                                
                            else:
                                FlowM[i] = MENS_solved.M[i,j,k].value/(MENS_solved.cr[i,k].value-MENS_solved.crin[i,j,(k+1)].value)
                                FlowM[j] = MENS_solved.M[i,j,k].value/(MENS_solved.clin[i,j,k].value-MENS_solved.cl[j,(k+1)].value)
                            
                            ME_inits = self._obtain_initializations(MENS_solved,i,j,k)   #, me_inits=ME_inits
                            finiteels = [20,50,100,200]
                            count = 0
                            while count <= 3:
                                nfe = finiteels[count]
                                print("solving for ", nfe, "number of elements")
                                mx = mass_exchanger(rich_stream_name = i, lean_stream_name=j, rich_in_side=CRin_Side, rich_out_side=CRout_Side,flowrates = FlowM, me_inits = ME_inits, stream_properties = stream_properties, nfe =nfe)
    
                                ME5, ME5results = mx.find_detailed_exchanger_design()
                                print(ME5results)
                                print("ME5 results type: ",type(ME5results))
                                print(ME5.success)
                                if ME5results == 'failed epically':
                                    print("The exchanger could not be solved. This means that for this exchanger no model is stored. Could result in failure to produce correction factors.")
                                    exchanger_models[m]=ME5
                                    #exchanger_models[m].success = False
                                elif not isinstance(ME5results, str):
                                    if isinstance(ME5results, pyomo.core.base.PyomoModel.ConcreteModel):
                                        print("model did not solve correctly, so it is skipped")
                                        exchanger_models[m]=ME5
                                    elif (ME5results.solver.status == SolverStatus.ok) and (ME5results.solver.termination_condition == TerminationCondition.optimal):
                                        exchanger_models[m]=ME5
                                    elif (ME5results.solver.status == SolverStatus.ok) and (ME5results.solver.termination_condition == TerminationCondition.locallyOptimal):
                                        exchanger_models[m]=ME5
                                else:
                                    #Should add way to deal with unsolved NLPs (increase elements?)
                                    print("The exchanger could not be solved. This means that for this exchanger no model is stored. Could result in failure to produce correction factors.")
                                    pass
                                if ME5.success == False:
                                    print("try to increase number of FEs")
                                elif ME5.success == True:
                                    break
                                count = count + 1
                        elif con ==True:
                            #print("MATCH: ", m, " match ", i, "with ", j, " is not a selected match in ", k)
                            if m in exchanger_models:
                                pass
                            else:
                                exchanger_models[m]=None
                       
                        else:
                            pass
                                           
                        m+=1
            self.iter_count = ic
            if con == True:
                stop = self._check_convergence(MENS_solved,exchanger_models,m,tol = self.tol, men_type = men_type)
            else:
                stop = True
            #print("These are the previous corrections")
            #print(self.corrections)
            self.corrections=self._get_correction_factors(MENS_solved,exchanger_models, men_type = men_type)    
            #print("These are the current corrections")
            #print(self.corrections)
            iter_end = time.clock()
            print("Iteration time: ", iter_end - iter_time)
            if stop:
                break
        print("=======================================================================")
        print("\\\\\\\\\\\\\\\\\\\\\\CORRECTION LOG///////////////////////////////////")
        print("Every correction factor at every iteration logged")
        print("=======================================================================")
        print(self.correction_log)
        write_to_csv('correction_log'+exname+'.csv', self.correction_log)
        print("=======================================================================")
        print("\\\\\\\\\\\\\\\\\\\\\\  Solution Log  ///////////////////////////////////")  
        print("EVERY NLP OBJECTIVE FUNCTION SOLUTION AT EVERY ITERATION LOGGED")
        print("=======================================================================")
        print(self.solution_log)
        write_to_csv('solution_log'+exname+'.csv', self.solution_log)
        print("=======================================================================")
        print("\\\\\\\\\\\\\\\\\\\\\\  MINLP TAC Solution Log  ///////////////////////")  
        print("EVERY MINLP OBJECTIVE FUNCTION SOLUTION AT EVERY ITERATION LOGGED")
        print("=======================================================================")
        print(self.MINLP_TAC_log)
        write_to_csv('MINLP_TAC_log'+exname+'.csv', self.MINLP_TAC_log)
        print("=======================================================================")
        print("\\\\\\\\\\\\\\\\\\\\\\  Exchanger log  ///////////////////////")  
        print("How many binary variables were selected in every iteration")
        print("=======================================================================")
        print(self.exchanger_log)
        write_to_csv('exchanger_log'+exname+'.csv', self.exchanger_log)
        print("=======================================================================")
        print("\\\\\\\\\\\\\\\\\\\\\\  Capital costs for MINLP Solution Log  ///////////////////////")  
        print("            EVERY MINLP Capital cost logged               ")
        print("=======================================================================")
        print(self.capcost_log_MINLP)
        write_to_csv('capcost_log_MINLP'+exname+'.csv', self.capcost_log_MINLP)
        print("=======================================================================")
        print("\\\\\\\\\\\\\\\\\\\\\\  capital costs nlp Solution Log  ///////////////////////")  
        print("EVERY NLP OBJECTIVE FUNCTION SOLUTION AT EVERY ITERATION LOGGED")
        print("=======================================================================")
        print(self.capcost_log_nlp)
        write_to_csv('capcost_log_nlp'+exname+'.csv', self.capcost_log_nlp)
        print("=======================================================================")
        print("\\\\\\\\\\\\\\\\\\\\\\  exchanger failed during the NLP solution ///////////////////////")  
        print("Whether an NLP failed AT EVERY ITERATION LOGGED")
        print("=======================================================================")
        print(self.failed_exchanger)
        write_to_csv('failed_exchanger'+exname+'.csv', self.failed_exchanger)
        print("=======================================================================")
        print("\\\\\\\\\\\\\\\\\\\\\\  UTILITIES Solution Log  ///////////////////////")  
        print("         UTILITY COSTS AT EACH ITERATION LOGGED         ")
        print("=======================================================================")
        print(self.utility_cost)
        write_to_csv('utility_cost'+exname+'.csv', self.utility_cost)
        print("=======================================================================")
        print("=======================================================================")
        print("=======================================================================")
        print("CONVERGENCE ACHIEVED AFTER ", self.iter_count, " iterations")
        print("Best network found at iteration: ", self.best_net_iter)
        print("Optimal solution for NLP: ", self.best_objective_real) 

        print("Hopefully the optimal solution is somewhere in the jumbled mess above")
        
    def provide_problem_data(self, rich_data, lean_data, parameter_data, stream_properties):
        """
        provides the problem data in a DataFrame format and sets them as attributes to the class
        Not currently used. Just an idea for users to easily pass data
        
        Args:
            rich_data (DataFrame): rich stream data including stream name, Cin, Cout, flowrate 
            lean_data(DataFrame): lean stream data including stream name, Cin, Cout, flowrate 
            parameter_data(DataFrame): parameter data including costs, mass transfer coefficients, etc. 
            stream_properties(DataFrame): stream properties including RHO and costs
        """
        pass
