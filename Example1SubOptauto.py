# -*- coding: utf-8 -*-
"""
Created on Sat Oct 20 18:08:02 2018

Mass exchanger network synthesis in Pyomo Example 1 from the paper

This is an example script that utilizes the functions and classes contained in
the library folder in the main repository. The aim of this is to be able to read
in the data and call all the necessary functions from outside the main classes.

@author: mchlshort
"""
from __future__ import division
from pyomo.environ import *
import pandas as pd
import os
import inspect
import time
import numpy
import sys
from pyomo.opt import SolverFactory, ProblemFormat, TerminationCondition
from library.HybridStrategy import *

__author__ = "Michael Short"
__copyright__ = "Copyright 2018"
__credits__ = ["Michael Short, Lorenz T. Biegler, Adeniyi J. Isafiade"]
__license__ = "GPL-3"
__version__ = "0.9"
__maintainer__ =  "Michael Short"
__email__ = "shortm@andrew.cmu.edu"
__status__ = "Development"
 
example_name = 'Test_clean3'

# in the polished version we need to have here the tweakable params
# omega and EMAT
# additionally, we can have options to run the FE analysis or not (seeing how many elements we need)

# We also should have solver options to only use BARON or DICOPT and to point to them for the user

# There should also be options for different cuts to be added

start = time.clock()   
    
sys.stdout = open(example_name+'.txt','w')
dataDirectory = os.path.abspath(
    os.path.join( os.path.dirname(os.path.abspath(inspect.getfile(
        inspect.currentframe() ) ) ),'example_data'))

filenameR =  os.path.join(dataDirectory,'Rich_Ex_1.csv')
Rich_data = read_stream_data(filenameR)
print(Rich_data)
filenameL = os.path.join(dataDirectory,'Lean_Ex_1.csv')
Lean_data = read_stream_data(filenameL)

filenameP = os.path.join(dataDirectory,'problem_parameters.csv')
problem_parameters = read_stream_data(filenameP)

filenameSP = os.path.join(dataDirectory,'stream_properties.csv')
stream_properties = read_stream_data(filenameSP)  

stages = 3
ss = 'SBS'

Example1 = HybridStrategy()

#A future call to set the problem data up. More sense than a loooong arg list as below
#p_data = Example1.provide_problem_data(rich_data=Rich_data,lean_data=Lean_data, parameter_data=problem_parameters, stream_properties = stream_properties)

Example1.run_hybrid_strategy(cor_filter_size=0.5, max_iter=2,rich_data=Rich_data,lean_data=Lean_data, correction_factors = None, parameter_data=problem_parameters, stream_properties = stream_properties, exname = example_name, tol = 0.00001, non_iso = True, stages = stages, superstruct = ss)

stop = time.clock()
ex_time = stop - start 

print("Total time: ", ex_time )
sys.stdout.close()