# -*- coding: utf-8 -*-
"""
Created on Sat Oct 20 18:08:02 2018

Mass exchanger network synthesis in Pyomo Example 1 from the paper

This is an example script that utilizes the functions and classes contained in
the library folder in the main repository. The aim of this is to be able to read
in the data and call all the necessary functions from outside the main classes.

@author: shortm
"""
from __future__ import division
from pyomo.environ import *
import pandas as pd
import os
import inspect
import numpy
import time
import timeit
import sys
from pyomo.opt import SolverFactory, ProblemFormat, TerminationCondition
from library.MassExchanger import *
from library.MENS_MINLPauto import *
from library.HybridStrategySubOpt import *

__author__ = "Michael Short"
__copyright__ = "Copyright 2018"
__credits__ = ["Michael Short, Lorenz T. Biegler, Adeniyi J. Isafiade"]
__license__ = "GPL-3"
__version__ = "0.9"
__maintainer__ =  "Michael Short"
__email__ = "shortm@andrew.cmu.edu"
__status__ = "Development"

start = timeit.default_timer()   
example_name = 'Ex1SWStryOmegabig'

         
sys.stdout = open(example_name+'.txt','w')
dataDirectory = os.path.abspath(
    os.path.join( os.path.dirname(os.path.abspath(inspect.getfile(
        inspect.currentframe() ) ) ),'example_data'))

filenameR =  os.path.join(dataDirectory,'Rich_Ex_1.csv')
Rich_data = read_stream_data(filenameR)
print(Rich_data)
filenameL = os.path.join(dataDirectory,'Lean_Ex_1.csv')
Lean_data = read_stream_data(filenameL)

filenameP = os.path.join(dataDirectory,'problem_parametersSWS.csv')
problem_parameters = read_stream_data(filenameP)

filenameSP = os.path.join(dataDirectory,'stream_properties.csv')
stream_properties = read_stream_data(filenameSP)  

stages = 2
#ss = 'SBS'
#Ex1MEN = MENS(rich_data=Rich_data,lean_data=Lean_data, correction_factors = None)
Example1 = HybridStrategy()
#p_data = Example1.provide_problem_data(rich_data=Rich_data,lean_data=Lean_data, parameter_data=problem_parameters, stream_properties = stream_properties)

Example1.run_hybrid_strategy(cor_filter_size=0.05, max_iter=1,rich_data=Rich_data,lean_data=Lean_data, correction_factors = None, parameter_data=problem_parameters, stream_properties = stream_properties, exname = example_name, tol = 0.00001, non_iso = True, stages = stages, superstruct = 'SWS')
#MEN_init = Ex1MEN.NLP_MENS_init() 
stop = timeit.default_timer()
ex_time = stop - start 

print("timeit says: ", ex_time )
sys.stdout.close()
#MENS = Ex1MEN.MINLP_MENS_full(MEN_init) 