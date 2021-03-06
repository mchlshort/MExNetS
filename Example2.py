# -*- coding: utf-8 -*-
"""
Created on Sat Oct 20 18:08:02 2018

Mass exchanger network synthesis in Pyomo Example 2 from the paper

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

start = time.clock()    

# This is the name that will be displayed in any of the outputs 
example_name = 'Example2'

# This is for data reading - point to folder and identify the data required         
sys.stdout = open(example_name+'.txt','w')
dataDirectory = os.path.abspath(
    os.path.join( os.path.dirname(os.path.abspath(inspect.getfile(
        inspect.currentframe() ) ) ),'example_data'))

filenameR =  os.path.join(dataDirectory,'Rich_Ex_2.csv')
Rich_data = read_stream_data(filenameR)

filenameL = os.path.join(dataDirectory,'Lean_Ex_2.csv')
Lean_data = read_stream_data(filenameL)

filenameP = os.path.join(dataDirectory,'problem_parameters2.csv')
problem_parameters = read_stream_data(filenameP)

filenameSP = os.path.join(dataDirectory,'stream_properties2.csv')
stream_properties = read_stream_data(filenameSP)  

Example1 = HybridStrategy()
#p_data = Example1.provide_problem_data(rich_data=Rich_data,lean_data=Lean_data, parameter_data=problem_parameters, stream_properties = stream_properties)

Example1.run_hybrid_strategy(cor_filter_size=0.05, max_iter=100,rich_data=Rich_data,lean_data=Lean_data, correction_factors = None, parameter_data=problem_parameters, \
                             stream_properties = stream_properties, exname = example_name, tol = 0.01, stages = 2, bin_cuts = True)
stop = time.clock()
ex_time = stop - start 

print("Total time: ", ex_time )
sys.stdout.close()
sys.exit()