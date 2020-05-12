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
__copyright__ = "Copyright 2020"
__credits__ = ["Michael Short, Lorenz T. Biegler, Adeniyi J. Isafiade"]
__license__ = "GPL-3"
__version__ = "0.9"
__maintainer__ =  "Michael Short"
__email__ = "m.short@surrey.ac.uk"
__status__ = "Development"
 
# This is the name that will be displayed in any of the outputs
example_name = 'Example1'

# These do not need to be changed
start = time.clock()   
    
sys.stdout = open(example_name+'.txt','w')

# This is for data reading - point to folder and identify the data required
dataDirectory = os.path.abspath(
    os.path.join( os.path.dirname(os.path.abspath(inspect.getfile(
        inspect.currentframe() ) ) ),'example_data'))

filenameR =  os.path.join(dataDirectory,'Rich_Ex_1.csv')
Rich_data = read_stream_data(filenameR)

filenameL = os.path.join(dataDirectory,'Lean_Ex_1.csv')
Lean_data = read_stream_data(filenameL)

filenameP = os.path.join(dataDirectory,'problem_parameters.csv')
problem_parameters = read_stream_data(filenameP)

filenameSP = os.path.join(dataDirectory,'stream_properties.csv')
stream_properties = read_stream_data(filenameSP)  

# Here we can identify the number of stages (SWS only) and superstructure type
stages = 3
ss = 'SBS'

#Finally we create the HybridStrategy class and run the algorithm with all the appropriate options selected
# Please look into the documentation within the functions and classes to view all options and potential 
# arguments. 
Example1 = HybridStrategy()

Example1.run_hybrid_strategy(cor_filter_size=0.05, max_iter=50,rich_data=Rich_data,lean_data=Lean_data, correction_factors = None, parameter_data=problem_parameters,\
                             stream_properties = stream_properties, exname = example_name, tol = 0.000001, non_iso = True, stages = stages, superstruct = ss, bin_cuts = False)

stop = time.clock()
ex_time = stop - start 

print("Total time: ", ex_time )
sys.exit()