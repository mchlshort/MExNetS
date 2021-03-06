#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Fri Jun  1 10:35:31 2018

Individual Mass Exchanger optimization model in Pyomo. To be used in conjunction with the
MENS package developed. 

@author: mchlshort
"""

from __future__ import division
from math import pi
from pyomo.environ import *
from pyomo.dae import *
from pyomo.opt import SolverFactory, ProblemFormat, TerminationCondition, SolverStatus
from library.FeasibleSolver import *
import pandas as pd
import os
import inspect
import numpy as np
import sys

__author__ = "Michael Short"
__copyright__ = "Copyright 2020"
__credits__ = ["Michael Short, Lorenz T. Biegler, Isafiade, AJ."]
__license__ = "GPL-3"
__version__ = "0.9"
__maintainer__ =  "Michael Short"
__email__ = "m.short@surrey.ac.uk"
__status__ = "Development"

class mass_exchanger(object):
    def __init__(self, rich_stream_name, lean_stream_name, rich_in_side, rich_out_side, flowrates, me_inits, stream_properties, ncp =3, nfe =200):
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
        m = ConcreteModel()

        #sets
        m.ii = RangeSet((self.nfe))
        m.jj = RangeSet((self.ncp))
        # way to move from unscaled time to scaled time
        #m.tau = ContinuousSet(bounds=(0,1))
        #m.h = Var(m.tau)
        #Table a(jj,jj) First order derivatives collocation matrix
        a = {}
        a[1,1] = 0.19681547722366
        a[1,2] = 0.39442431473909
        a[1,3] = 0.37640306270047
        a[2,1] = -0.06553542585020
        a[2,2] = 0.29207341166523
        a[2,3] = 0.51248582618842
        a[3,1] = 0.02377097434822
        a[3,2] = -0.04154875212600
        a[3,3] = 0.11111111111111
        m.a = Param(m.jj,m.jj, initialize = a)
        
        
        
        
        m.height = Var(initialize = self.ME_inits["height"],bounds = (0.00001, None))
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
        m.PackCost = Param(initialize = (self.ME_inits["packcost"]*self.ME_inits["packcostcor"]))
        m.AF = Param(initialize = 0.2)
        #=========================================
        #Variables
        #=========================================

        #flux of the contaminant from vapour
        m.flux =Var(m.ii,m.jj)
        m.cRs = Var(m.ii,m.jj,within = NonNegativeReals)
        m.cLs = Var(m.ii,m.jj,within = NonNegativeReals)
        m.cR0 = Var(m.ii,within = NonNegativeReals)
        m.cL0 = Var(m.ii,within = NonNegativeReals)
        m.h0 = Var(m.ii,within = NonNegativeReals)
        
        m.cdotR = Var(m.ii,m.jj)
        m.cdotL = Var(m.ii,m.jj)
        
        m.hs = Var(m.ii,m.jj,within = NonNegativeReals)
        
        d = self.ME_inits["diameter"]*self.ME_inits["diacor"]
        m.diameter = Param(initialize =d)

        #DIFFERENTIAL VAR
        #m.dheight = DerivativeVar(m.h)
        #m.dCRdh= DerivativeVar(m.cRs, withrespectto=m.tau)
        #m.dCLdh= DerivativeVar(m.cLs, withrespectto=m.tau)
        #========================================
        #CONSTRAINTS
        #========================================
        def TRateVap_(m, ii,jj):
            return m.flux[ii,jj] == -m.kw*m.kwcor*m.surfarea*m.surfacor*pi/4*(m.diameter**2)*(m.cRs[ii,jj]-m.henry*m.cLs[ii,jj])
        m.TRateVap = Constraint(m.ii,m.jj, rule = TRateVap_)

        #Differential Equations
        print('Number of finite elements' ,self.nfe)
        def FECOLcr_(m, ii,jj):
            #if ii >= self.nfe:
            #    return Constraint.Skip
            #else:
            return m.cRs[ii,jj] ==  m.cR0[ii] + m.height/self.nfe*sum(m.a[kk,jj]*m.cdotR[ii,jj] for kk in m.jj)
        m.FECOLcr = Constraint(m.ii,m.jj, rule = FECOLcr_)

        def FECOLcl_(m, ii,jj):
            #if ii >= self.nfe:
            #    return Constraint.Skip
            #else:
            return m.cLs[ii,jj] ==  m.cL0[ii] + m.height/self.nfe*sum(m.a[kk,jj]*m.cdotL[ii,jj] for kk in m.jj)
        m.FECOLcl = Constraint(m.ii,m.jj, rule = FECOLcl_)
        
        def FECOLch_(m, ii,jj):
            #if ii >= self.nfe:
            #    return Constraint.Skip
            #else:
            return m.hs[ii,jj] ==  m.h0[ii] + m.height/self.nfe*sum(m.a[kk,jj] for kk in m.jj)
        m.FECOLch = Constraint(m.ii,m.jj, rule = FECOLch_)
        
        #CONTINUITY EQUNS
        def CONcR_(m, ii):
            #if ii >= self.nfe:
            #    return Constraint.Skip
            if ii == 1:
                return Constraint.Skip
            else:
                return m.cR0[ii] ==  m.cR0[ii-1] + m.height/self.nfe*sum(m.cdotR[ii-1,jj]*m.a[jj,3] for jj in m.jj)
        m.CONcR = Constraint(m.ii, rule = CONcR_)
        
        def CONcL_(m, ii):
            #if ii >= self.nfe:
            #    return Constraint.Skip
            if ii == 1:
                return Constraint.Skip
            else:
                return m.cL0[ii] ==  m.cL0[ii-1] + m.height/self.nfe*sum(m.cdotL[ii-1,jj]*m.a[jj,3] for jj in m.jj)
        m.CONcL = Constraint(m.ii, rule = CONcL_)
        
        def CONtt_(m, ii):
            #if ii >= self.nfe:
            #    return Constraint.Skip
            if ii == 1:
                return Constraint.Skip
            else:
                return m.h0[ii] ==  m.h0[ii-1] + m.height/self.nfe*sum(m.a[jj,3] for jj in m.jj)
        m.CONtt = Constraint(m.ii, rule = CONtt_)
        
        # DIFFERENTIAL EQUATIONS
        
        def ODECL_(m, ii,jj):
            return m.cdotL[ii,jj] ==  m.flux[ii,jj]/m.FlowLm
        m.ODECL = Constraint(m.ii,m.jj, rule = ODECL_)
        
        
        def ODECR_(m, ii,jj):
            return m.cdotR[ii,jj] ==  m.flux[ii,jj]/m.FlowRm
        m.ODECR = Constraint(m.ii,m.jj, rule = ODECR_)

        #initial conditions
        def _init1(m):
            return m.cR0[1] == self.rich_in[self.rich_stream_name]
        m.initcon1 = Constraint(rule=_init1)
        def _init2(m):
            return m.cRs[self.nfe, 3] == self.rich_out[self.rich_stream_name]
        m.initcon2 = Constraint(rule=_init2)
        def _init3(m):
            return m.cL0[1] == self.rich_in[self.lean_stream_name]
        m.initcon3 = Constraint(rule=_init3)
        def _init4(m):
            return m.cLs[self.nfe, 3] == self.rich_out[self.lean_stream_name]
        m.initcon4 = Constraint(rule=_init4)        
        def _init5(m):
            return m.h0[1] == 0
        m.initcon5 = Constraint(rule=_init5)  

        #Need to do discretization before the objective
        #discretizer = TransformationFactory('dae.collocation')
        #discretizer.apply_to(m, nfe = self.nfe, ncp =self.ncp, scheme = 'LAGRANGE-RADAU')

        def Obj_(model):
            return 1 
        #m.AF*23805*(m.diameter**0.57)*1.15*m.height + m.AF*pi*(m.diameter**2)/4*m.height*m.PackCost

        m.Obj = Objective( rule = Obj_, sense=minimize)
        options = {}
        #options['mu_init'] = 1e-5
        #options['bound_push'] =1e-5
        #options['mu_strategy'] = 'adaptive'
        presolved_clone = m.clone()
        results = solve_until_feas_NLP(m)        
        #display(m)
        #print(results)

        m.height.pprint()
        m.diameter.pprint()
        q = m.FlowRm.value*(m.cR0[1].value-m.cRs[self.nfe,self.ncp].value)
        print("mass exchanged R:  ", q )
        
        q = m.FlowLm.value*(m.cL0[1].value-m.cLs[self.nfe, self.ncp].value)
        print("mass exchanged L:  ", q )
        #print("All inlet and outlet concs:")
        #print(m.cR0[1].value, self.rich_in[self.rich_stream_name])
        #print(m.cRs[self.nfe,self.ncp].value, self.rich_out[self.rich_stream_name])
        #print(m.cL0[1].value, self.rich_in[self.lean_stream_name])
        #print(m.cLs[self.nfe,self.ncp].value, self.rich_out[self.lean_stream_name])
        #m.cLs.pprint()
        #m.cRs.pprint()
        success_solve = bool
        #m.display()
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
            if old_solve_clone.diameter.value == 0:
                diameter_init=1
            else:
                diameter_init=old_solve_clone.diameter.value
        else:
            if m2.diameter.value == 0:
                diameter_init=1
            else:
                diameter_init=m2.diameter.value
        m.del_component(m.diameter)
        m.diameter = Var(initialize = diameter_init, bounds = (0.000001,None))
        
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
        FlowLVcor = (self.mass_flows[self.lean_stream_name]/self.mass_flows[self.rich_stream_name])*((m.RHOG/m.RHOL)**0.5)
        
        m.FlowRVlat =Param(initialize=FlowRVlat)
        m.FlowLVlat =Param(initialize=FlowLVcor)
                
        m.FixCost = Param(initialize = 30000) # need to read from data
        
        #=========================================
        #New Variables
        #=========================================

        def init_area(m):
            return pi/4*(m.diameter.value**2)
        
        m.area = Var(initialize=init_area,  bounds = (0.0001,None))
        
        #m.area.pprint()

        def init_koga(m):
            return m.kw*m.kwcor
        
        m.koga = Var(initialize = init_koga, bounds = (0.000000000001,None))
        
        def init_velocityR(m):
            if m.area.value == 0:
                return 5
            else:
                return (m.FlowRVlat/m.area.value)
        
        def init_velocityL(m):
            if m.area.value == 0:
                return 5
            else:
                return (m.FlowLVlat/m.area.value)
        
        m.VelocityR = Var(initialize = init_velocityR, bounds = (0.00000001,20))
        m.VelocityL = Var(initialize = init_velocityL, bounds = (0.00000001,100))
        
        #========================================
        #MODIFIED CONSTRAINTS
        #========================================
        
        m.del_component(m.TRateVap)
        m.del_component(m.TRateVap_index)
        def TRateVap_(m, ii,jj):

            return m.flux[ii,jj] == -m.koga*m.area*m.surfarea*m.surfacor*(m.cRs[ii,jj]-m.henry*m.cLs[ii,jj])
        
        m.TRateVap = Constraint(m.ii,m.jj, rule = TRateVap_)
        
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
            return m.height <= 200*m.diameter
            
        m.loverdup = Constraint(rule=loverdup_)
        
        def loverdlo_(m):
            return m.height >= 0.01*m.diameter
            
        m.loverdlo = Constraint(rule=loverdlo_)

        #========================================
        # OBJECTIVE and SOLVE
        #========================================             
        m.del_component(m.Obj)
        def Obj1_(m):
            #return m.AF*23805*(m.diameter**0.57)*1.15*m.height + m.AF*pi*(m.diameter**2)/4*m.height*m.PackCost
            return m.AF*23805*(m.diameter**0.57)*1.15*m.height + m.AF*pi*(m.diameter**2)/4*m.height*m.PackCost
        #m.AF*23805*(m.diameter**0.57)*1.15*m.height + m.AF*pi*(m.diameter**2)/4*m.height*m.PackCost

        m.Obj1 = Objective(rule = Obj1_,sense=minimize)
        #m.Obj.deactivate()
        m.Obj1.activate()
        
        presolved_clone = m.clone()
        results = solve_until_feas_NLP(m)
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
        m.height.pprint()
        m.diameter.pprint()
        m.VelocityL.pprint()
        m.VelocityR.pprint()
        m.koga.pprint()
        #m.flux.pprint()
        q = m.FlowRm.value*(m.cR0[1].value-m.cRs[self.nfe,self.ncp].value)
        print("mass exchanged R:  ", q )
        
        q = m.FlowLm.value*(m.cL0[1].value-m.cLs[self.nfe, self.ncp].value)
        print("mass exchanged L:  ", q )
        #print("All inlet and outlet concs:")
        #print(m.cR0[1].value, self.rich_in[self.rich_stream_name])
        #print(m.cRs[self.nfe,self.ncp].value, self.rich_out[self.rich_stream_name])
        #print(m.cL0[1].value, self.rich_in[self.lean_stream_name])
        #print(m.cLs[self.nfe,self.ncp].value, self.rich_out[self.lean_stream_name])
        #.cLs.pprint()
        #m.cRs.pprint()
        
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
        
        #m.del_component(m.koga)
        #m.koga = Var(initialize = 0.05, bounds = (0.000000000001,None))
        
        VelocityR_init = 0
        if success_solve:
            VelocityR_init=old_solve_clone.VelocityR.value
        else:
            VelocityR_init=m2.VelocityR.value
            
        VelocityR_init=m.VelocityR.value
        #m.del_component(m.VelocityR)
        
        #m.VelocityR = Var(initialize = VelocityR_init, bounds = (0.00000001,20))
        
        VelocityL_init = 0
        if success_solve:
            VelocityL_init=old_solve_clone.VelocityL.value
        else:
            VelocityL_init=m2.VelocityL.value
        
        #m.del_component(m.VelocityL)
        #m.VelocityL = Var(initialize =  VelocityL_init, bounds = (0.0000001,100)) 
        
        area_init = 0
        if success_solve:
            area_init=old_solve_clone.area.value
        else:
            area_init=m2.area.value
            
        #m.del_component(m.area)
        
        #m.area = Var(initialize = area_init, bounds = (0.0001,100))
        
        diameter_init = 0.35
        if success_solve:
            diameter_init=old_solve_clone.diameter.value
        else:
            diameter_init=m2.diameter.value
        #m.del_component(m.diameter)
        
        #m.diameter = Var(initialize = 0.35, bounds = (0.0001,None))
        
        #=========================================
        #NEW Parameters
        #=========================================        
        
        m.vis = Param(initialize= m.visL[self.lean_stream_name])
        
        #=========================================
        #NEW Variables
        #=========================================
        m.packfact = Var(initialize=120, bounds = (80.0,None))
        
        ReLini = m.RHOL*m.VelocityL.value*0.05/m.vis.value
        ReGini = m.RHOG*m.VelocityR.value*0.05/m.visRich.value
        
        m.ReL = Var(initialize = ReLini,bounds = (0.00000000001,None))
        m.ReG = Var(initialize = ReGini,bounds = (0.00000000001,None))
                
        Floodini = 249.089/0.3048*0.12*((m.packfact.value*0.3048)**0.7)
        FloodActini = 22.3*(m.packfact.value)*(m.vis**0.2)*((m.VelocityR.value)**2)*((10**(0.035*m.VelocityL.value))/(9.81*m.RHOG))

        m.Flood= Var(initialize = Floodini, bounds = (0.000000001,None))
        m.FloodAct= Var(initialize = FloodActini, bounds = (0.000000001,None))

        #========================================
        #OLD CONSTRAINTS
        #========================================

        #========================================
        #MODIFIED CONSTRAINTS
        #========================================
            
        m.del_component(m.loverdup)        
        def loverdup_(m):
            return m.height <= 250*m.diameter
            
        m.loverdup = Constraint(rule=loverdup_)
        
        m.del_component(m.loverdlo)
        def loverdlo_(m):
            return m.height >= 0.2*m.diameter
            
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
        #m.del_component(m.Obj1)
        #m.del_component(m.Obj)
        #def Obj2_(m):
        #    return m.AF*23805*(m.diameter**0.57)*1.15*m.height + m.AF*pi*(m.diameter**2)/4*m.height*m.PackCost
        #m.AF*23805*(m.diameter**0.57)*1.15*m.height + m.AF*pi*(m.diameter**2)/4*m.height*m.PackCost
        #m.AF*23805*(m.diameter**0.57)*1.15*m.height + m.AF*pi*(m.diameter**2)/4*m.height*m.PackCost
                                
        #m.Obj2 = Objective(rule = Obj2_, sense=minimize)
        #m.Obj1.deactivate()
        #m.Obj2.activate()   
        #solver = SolverFactory('./../../BARON/baron')
        presolve_clone = m.clone()
        results = simple_NLP_solve(m)
        
        #========================================
        # POST PROCESSING AND PRINTING
        #======================================== 
        #print(results)
        #display(m)
        #results = solver_manager.solve(m,opt=solver)
        #q= m.AF*23805*(m.diameter**0.57)*1.15*m.height()
        #w=m.AF*pi*(m.diameter()**2)/4*m.height()*m.PackCost
        #print(m.FixCost, "    ",q,"   ", w)
        #m.CapCost.pprint()
        m.height.pprint()
        #m.heightp.pprint()
        m.diameter.pprint()
        m.ReG.pprint()
        m.ReL.pprint()
        m.Flood.pprint()
        m.FloodAct.pprint()
        m.VelocityR.pprint()
        m.VelocityL.pprint()
        m.packfact.pprint()
        m.koga.pprint()
        m.de.pprint()
        #m.display()
        #print(results)
        #results.pprint
        q = m.FlowRm.value*(m.cR0[1].value-m.cRs[self.nfe,self.ncp].value)
        print("mass exchanged R:  ", q )
        
        q = m.FlowLm.value*(m.cL0[1].value-m.cLs[self.nfe, self.ncp].value)
        print("mass exchanged L:  ", q )
        #print("All inlet and outlet concs:")
        #print(m.cR0[1].value, self.rich_in[self.rich_stream_name])
        #print(m.cRs[self.nfe,self.ncp].value, self.rich_out[self.rich_stream_name])
        #print(m.cL0[1].value, self.rich_in[self.lean_stream_name])
        #print(m.cLs[self.nfe,self.ncp].value, self.rich_out[self.lean_stream_name])
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

        packfact_init=0
        if success_solve:
            packfact_init=old_solve_clone.packfact.value
        else:
            packfact_init=m2.packfact.value
            
        #m.del_component(m.packfact)
        #m.packfact = Var(initialize = packfact_init, bounds = (1, 10000))

        #=========================================
        #NEW Parameters
        #=========================================   
        # this could be the init self.ME_inits["surfarea"]*self.ME_inits["surfacor"])
        m.ap = Param(initialize =300)
        m.surften = Param(initialize = m.surft[self.lean_stream_name])

        #=========================================
        #New Variables
        #=========================================

        p = m.ap.value*m.surfacor.value*(1-exp(-1.45*((0.075/m.surften.value)**0.75)*((m.RHOL.value*m.VelocityR.value/(m.vis.value*m.ap.value))**0.1)*((m.ap.value*(m.VelocityR.value**2)/9.81)**(-0.05))*((m.RHOL.value*(m.VelocityR.value**2)/(m.ap.value*m.surften.value))**0.2)))
        p = m.ap.value*m.surfacor.value*(1-exp(-1.45*((0.075/m.surften.value)**0.75)*((m.RHOL.value*m.VelocityL.value/(m.vis.value*m.ap.value))**0.1)*(((m.ap.value*((m.RHOL.value*m.VelocityL.value)**2))/((m.RHOL.value**2)*9.81))**(-0.05))*((((m.RHOL.value*m.VelocityL.value)**2)/((m.RHOL.value**2)*m.ap.value*m.surften.value))**0.2)))
        #print("Ai initial value=", p)
        m.ai = Var(initialize = p, within = NonNegativeReals)
        
        #========================================
        #OLD CONSTRAINTS
        #========================================
        #Differential Equations
    
        #========================================
        # MODIFIED CONSTRAINTS
        #========================================
            
        m.del_component(m.TRateVap)
        m.del_component(m.TRateVap_index)
        def TRateVap_(m, ii,jj):
            return m.flux[ii,jj] == -m.koga*m.area*m.ai*(m.cRs[ii,jj]-m.henry*m.cLs[ii,jj])
        m.TRateVap = Constraint(m.ii,m.jj, rule = TRateVap_)
        
        m.del_component(m.loverdup)
        
        def loverdup_(m):
            return m.height <= 25*m.diameter
            
        m.loverdup = Constraint(rule=loverdup_)
        
        m.del_component(m.loverdlo)
        
        def loverdlo_(m):
            return m.height >= 2*m.diameter
            
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

        #m.del_component(m.Obj2)
        #def Obj3_(m):
        #    return m.AF*23805*(m.diameter**0.57)*1.15*m.height + m.AF*pi*(m.diameter**2)/4*m.height*m.PackCost*2
        #m.AF*23805*(m.diameter**0.57)*1.15*m.height + m.AF*pi*(m.diameter**2)/4*m.height*m.PackCost
        #23805*(m.diameter**0.57)*1.15*m.height + pi*(m.diameter**2)/4*m.height*m.PackCost

        #m.Obj3 = Objective(rule = Obj3_,sense=minimize)
        
        #m.Obj2.deactivate()
        #m.Obj3.activate()  
        #solver = SolverFactory('./../../BARON/baron')
        #solver= SolverFactory('ipopt')
        #results = solver.solve(m,tee=True)
        presolve_clone = m.clone()
        results = simple_NLP_solve(m)
        
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
        m.ap.pprint()
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
        print("All inlet and outlet concs:")
        q = m.FlowRm.value*(m.cR0[1].value-m.cRs[self.nfe,self.ncp].value)
        print("mass exchanged R:  ", q )
        
        q = m.FlowLm.value*(m.cL0[1].value-m.cLs[self.nfe, self.ncp].value)
        print("mass exchanged L:  ", q )
        #print("All inlet and outlet concs:")
        #print(m.cR0[1].value, self.rich_in[self.rich_stream_name])
        #print(m.cRs[self.nfe,self.ncp].value, self.rich_out[self.rich_stream_name])
        #print(m.cL0[1].value, self.rich_in[self.lean_stream_name])
        #print(m.cLs[self.nfe,self.ncp].value, self.rich_out[self.lean_stream_name])
        #print(results)
        #m.display()
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
        m1 = ConcreteModel()
        
        #sets
        m1.ii = RangeSet((self.nfe))
        m1.jj = RangeSet((self.ncp))
        # way to move from unscaled time to scaled time
        #m.tau = ContinuousSet(bounds=(0,1))
        #m.h = Var(m.tau)
        #Table a(jj,jj) First order derivatives collocation matrix
        a = {}
        a[1,1] = 0.19681547722366
        a[1,2] = 0.39442431473909
        a[1,3] = 0.37640306270047
        a[2,1] = -0.06553542585020
        a[2,2] = 0.29207341166523
        a[2,3] = 0.51248582618842
        a[3,1] = 0.02377097434822
        a[3,2] = -0.04154875212600
        a[3,3] = 0.11111111111111
        m1.a = Param(m1.jj,m.jj, initialize = a)
        
        m1.ag = Param(initialize = 0.123)
        
        
        m1.height = Var(initialize = m.height.value,bounds = (0.15, None))
        #=========================================
        #Parameters
        #=========================================
        #I will fix these here for now, but the plan is to load these from a seperate file
        #preferably for each component
        #m1.kw = Param(initialize = self.ME_inits["kw"])
        #m1.kwcor = Param(initialize = self.ME_inits["kwcor"])
        #m.surfarea = Param(initialize =self.ME_inits["surfarea"])
        #m.surfacor = Param(initialize = self.ME_inits["surfacor"])
        #Henry for mol SO2 per mol H2O = 0.0234, but in this eg, it is already inc
        m1.henry = Param(initialize = 1)
        #print("mTHIS IS THE MASS_FLOWS", self.mass_flows)
        m1.FlowRm = Param(initialize = self.mass_flows[self.rich_stream_name])
        m1.FlowLm = Param (initialize = self.mass_flows[self.lean_stream_name])
        #m.PackCost = Param(initialize = (self.ME_inits["packcost"]*self.ME_inits["packcostcor"]))
        m1.AF = Param(initialize = 0.2)
        m1.surften = Param(initialize = m.surft[self.lean_stream_name])
        m1.visRich = Param(initialize = m.visR[self.rich_stream_name])
        #m.visRich.pprint()
        #m.de = Param(initialize=0.02)        
        m1.vis = Param(initialize= m.visL[self.lean_stream_name])
        #These need to come from data
        m1.RHOG = Param(initialize = m.RHOG)
        #m.RHOG.pprint()
        m1.RHOL = Param(initialize = m.RHOL)
        #m.RHOL.pprint()
        #sys.exit()
        #Henry for mol SO2 per mol H2O = 0.0234, but in this eg, it is already inc
        #m.henry = Param(initialize = 1)
        #m.FlowRm = Param(initialize = self.mass_flows['R1'])
        #m.FlowLm = Param (initialize = self.mass_flows['L2'])
        
        FlowRVlat = self.mass_flows[self.rich_stream_name]/m.RHOG
        FlowLVlat = self.mass_flows[self.lean_stream_name]/m.RHOL
        FlowLVcor = (self.mass_flows[self.lean_stream_name]/self.mass_flows[self.rich_stream_name])*((m.RHOG/m.RHOL)**0.5)
        
        m1.FlowRVlat =Param(initialize=FlowRVlat)
        m1.FlowLVlat =Param(initialize=FlowLVcor)
        #=========================================
        #Variables
        #=========================================
        flux_init = {}
        if success_solve:
            for i in m.ii:
                for j in m.jj:
                    flux_init[i,j]=m.flux[i,j].value
        else:
            for i in m.ii:
                for j in m.jj:
                    flux_init[i,j]=m2.flux[i,j].value

        cRs_init = {}
        if success_solve:
            for i in m.ii:
                for j in m.jj:
                    cRs_init[i,j]=m.cRs[i,j].value
        else:
            for i in m.ii:
                for j in m.jj:
                    cRs_init[i,j]=m2.cRs[i,j].value

        cLs_init = {}

        if success_solve:
            for i in m.ii:
                for j in m.jj:
                    cLs_init[i,j]=m.cLs[i,j].value
        else:
            for i in m.ii:
                for j in m.jj:
                    cLs_init[i,j]=m2.cLs[i,j].value
            
        cL0_init = {}

        if success_solve:
            for i in m.ii:
                cL0_init[i]=m.cL0[i].value
        else:
            for i in m.ii:
                for j in m.jj:
                    cL0_init[i]=m2.cL0[i].value
                                        
        cR0_init = {}

        if success_solve:
            for i in m.ii:
                cR0_init[i]=m.cR0[i].value
        else:
            for i in m.ii:
                for j in m.jj:
                    cR0_init[i]=m2.cR0[i].value
                    
        h0_init = {}

        if success_solve:
            for i in m.ii:
                h0_init[i]=m.h0[i].value
        else:
            for i in m.ii:
                for j in m.jj:
                    h0_init[i]=m2.h0[i].value
                    
        cdotR_init = {}

        if success_solve:
            for i in m.ii:
                for j in m.jj:
                    cdotR_init[i,j]=m.cdotR[i,j].value
        else:
            for i in m.ii:
                for j in m.jj:
                    cdotR_init[i,j]=m2.cdotR[i,j].value
                    
        cdotL_init = {}

        if success_solve:
            for i in m.ii:
                for j in m.jj:
                    cdotL_init[i,j]=m.cdotL[i,j].value
        else:
            for i in m.ii:
                for j in m.jj:
                    cdotL_init[i,j]=m2.cdotL[i,j].value
                    
        hs_init = {}

        if success_solve:
            for i in m.ii:
                for j in m.jj:
                    hs_init[i,j]=m.hs[i,j].value
        else:
            for i in m.ii:
                for j in m.jj:
                    hs_init[i,j]=m2.hs[i,j].value
                    
        #flux of the contaminant from vapour
        m1.flux =Var(m1.ii,m1.jj, initialize = flux_init)
        m1.cRs = Var(m1.ii,m1.jj,within = NonNegativeReals, initialize = cRs_init)
        m1.cLs = Var(m1.ii,m1.jj,within = NonNegativeReals, initialize = cLs_init)
        m1.cR0 = Var(m1.ii,within = NonNegativeReals, initialize = cR0_init)
        m1.cL0 = Var(m1.ii,within = NonNegativeReals, initialize = cL0_init)
        m1.h0 = Var(m1.ii,within = NonNegativeReals, initialize = h0_init)
        
        m1.cdotR = Var(m1.ii,m1.jj, initialize = cdotR_init)
        m1.cdotL = Var(m1.ii,m1.jj, initialize = cdotL_init)
        
        m1.hs = Var(m1.ii,m1.jj,within = NonNegativeReals, initialize = hs_init)
        
        
        d = m.diameter.value
        m1.diameter = Var(initialize =d, within = NonNegativeReals)

        m1.area = Var(initialize = m.area.value, within = NonNegativeReals)

        #koga_init = 0
        #if success_solve:
        #    koga_init=old_solve_clone.koga.value
        #else:
        #    koga_init=m2.koga.value
            
        #m.del_component(m.koga)
        m1.koga = Var(initialize = m.koga.value, within = NonNegativeReals)
        
        VelocityR_init = 0
        if success_solve:
            VelocityR_init=old_solve_clone.VelocityR.value
        else:
            VelocityR_init=m2.VelocityR.value
            
        #VelocityR_init=m.VelocityR.value
        #m.del_component(m.VelocityR)
        m1.VelocityR = Var(initialize = m.VelocityR.value, bounds=(0.00001,None))
        
        VelocityL_init = 0
        if success_solve:
            VelocityL_init=old_solve_clone.VelocityL.value
        else:
            VelocityL_init=m2.VelocityL.value
        
        #m.del_component(m.VelocityL)
        m1.VelocityL = Var(initialize = m.VelocityL.value, bounds=(0.00001,None)) 
        
        ReL_init=0
        if success_solve:
            ReL_init=old_solve_clone.ReL.value
        else:
            ReL_init=m2.ReL.value
            
        #m.del_component(m.ReL)
        m1.ReL = Var(initialize = m.ReL.value, bounds = (0.00001,None)) 
        
        ReG_init=0
        if success_solve:
            ReG_init=old_solve_clone.ReG.value
        else:
            ReG_init=m2.ReG.value

        #m.del_component(m.ReG)
        m1.ReG = Var(initialize = m.ReG.value, bounds = (1,None))

        Flood_init=0
        if success_solve:
            Flood_init=old_solve_clone.Flood.value
        else:
            Flood_init=m2.Flood.value

        #m.del_component(m.Flood)
        m1.Flood = Var(initialize = m.Flood.value, within = NonNegativeReals)

        FloodAct_init=0
        if success_solve:
            FloodAct_init=old_solve_clone.FloodAct.value
        else:
            FloodAct_init=m2.FloodAct.value

        #m.del_component(m.FloodAct)
        m1.FloodAct = Var(initialize = m.FloodAct.value, within = NonNegativeReals)
        
        packfact_init=0
        if success_solve:
            packfact_init=old_solve_clone.packfact.value
        else:
            packfact_init=m2.packfact.value
            
        #m.del_component(m.packfact)
        m1.packfact = Var(initialize = m.packfact.value, bounds =(40,4000))

        ai_init=0
        if success_solve:
            ai_init=old_solve_clone.ai.value
        else:
            ai_init=m2.ai.value

        #m.del_component(m.ai)
        m1.ai = Var(initialize = m.ai.value, within = NonNegativeReals) 
        
        #=========================================
        #New Variables
        #=========================================      
        #These can have more thoughtful inits
        m1.packsize = Var(initialize = 0.05, bounds=(0.005, None))
        m1.SpecAreaPacking = Var(initialize = m1.ai.value, bounds=(5, None))
        m1.packVoid = Var(initialize=0.68,bounds = (0.5, None))
        
        #m.del_component(m.PackCost)
        m1.PackCost = Var(initialize = (self.ME_inits["packcost"]*self.ME_inits["packcostcor"]), within = NonNegativeReals)

        #========================================
        #CONSTRAINTS
        #========================================

        #Differential Equations
        print('Number of finite elements: ',self.nfe)
        def FECOLcr_(m, ii,jj):
            #if ii >= self.nfe:
            #    return Constraint.Skip
            #else:
            return m1.cRs[ii,jj] ==  m1.cR0[ii] + m1.height/self.nfe*sum(m1.a[kk,jj]*m1.cdotR[ii,jj] for kk in m1.jj)
        m1.FECOLcr = Constraint(m1.ii,m1.jj, rule = FECOLcr_)

        def FECOLcl_(m, ii,jj):
            #if ii >= self.nfe:
            #    return Constraint.Skip
            #else:
            return m1.cLs[ii,jj] ==  m1.cL0[ii] + m1.height/self.nfe*sum(m1.a[kk,jj]*m1.cdotL[ii,jj] for kk in m1.jj)
        m1.FECOLcl = Constraint(m1.ii,m1.jj, rule = FECOLcl_)
        
        def FECOLch_(m, ii,jj):
            #if ii >= self.nfe:
            #    return Constraint.Skip
            #else:
            return m1.hs[ii,jj] ==  m1.h0[ii] + m1.height/self.nfe*sum(m1.a[kk,jj] for kk in m1.jj)
        m1.FECOLch = Constraint(m1.ii,m1.jj, rule = FECOLch_)
        
        #CONTINUITY EQUNS
        def CONcR_(m, ii):
            #if ii >= self.nfe:
            #    return Constraint.Skip
            if ii == 1:
                return Constraint.Skip
            else:
                return m1.cR0[ii] ==  m1.cR0[ii-1] + m1.height/self.nfe*sum(m1.cdotR[ii-1,jj]*m1.a[jj,3] for jj in m1.jj)
        m1.CONcR = Constraint(m1.ii, rule = CONcR_)
        
        def CONcL_(m, ii):
            #if ii >= self.nfe:
            #    return Constraint.Skip
            if ii == 1:
                return Constraint.Skip
            else:
                return m1.cL0[ii] ==  m1.cL0[ii-1] + m1.height/self.nfe*sum(m1.cdotL[ii-1,jj]*m1.a[jj,3] for jj in m1.jj)
        m1.CONcL = Constraint(m1.ii, rule = CONcL_)
        
        def CONtt_(m, ii):
            #if ii >= self.nfe:
            #    return Constraint.Skip
            if ii == 1:
                return Constraint.Skip
            else:
                return m1.h0[ii] ==  m1.h0[ii-1] + m1.height/self.nfe*sum(m1.a[jj,3] for jj in m1.jj)
        m1.CONtt = Constraint(m1.ii, rule = CONtt_)
        
        # DIFFERENTIAL EQUATIONS
        
        def ODECL_(m, ii,jj):
            return m1.cdotL[ii,jj] ==  m1.flux[ii,jj]/m1.FlowLm
        m1.ODECL = Constraint(m1.ii,m1.jj, rule = ODECL_)
        
        
        def ODECR_(m, ii,jj):
            return m1.cdotR[ii,jj] ==  m1.flux[ii,jj]/m1.FlowRm
        m1.ODECR = Constraint(m1.ii,m1.jj, rule = ODECR_)

        #initial conditions
        def _init1(m):
            return m1.cR0[1] == self.rich_in[self.rich_stream_name]
        m1.initcon1 = Constraint(rule=_init1)
        def _init2(m):
            return m1.cRs[self.nfe, 3] == self.rich_out[self.rich_stream_name]
        m1.initcon2 = Constraint(rule=_init2)
        def _init3(m):
            return m1.cL0[1] == self.rich_in[self.lean_stream_name]
        m1.initcon3 = Constraint(rule=_init3)
        def _init4(m):
            return m1.cLs[self.nfe, 3] == self.rich_out[self.lean_stream_name]
        m1.initcon4 = Constraint(rule=_init4)        
        def _init5(m):
            return m1.h0[1] == 0
        m1.initcon5 = Constraint(rule=_init5)  
        
        #m.del_component(m.loverdup)
        
        def loverdup_(m):
            return m1.height <= 25*m1.diameter
            
        m1.loverdup = Constraint(rule=loverdup_)
        
        #m.del_component(m.loverdlo)
        
        def loverdlo_(m):
            return m1.height >= 2*m1.diameter
            
        m1.loverdlo = Constraint(rule=loverdlo_)
       
        #========================================
        # MODIFIED CONSTRAINTS
        #========================================
        #m.del_component(m.TRateVap)
        #m.del_component(m.TRateVap_index)

        def TRateVap_(m, ii,jj):
            return m1.flux[ii,jj] == -m1.koga*m1.ai*m1.area*(m1.cRs[ii,jj]-m1.henry*m1.cLs[ii,jj])
        m1.TRateVap = Constraint(m1.ii,m1.jj, rule = TRateVap_)

        #m.del_component(m.KogaEq)
        def KogaEq_(m):
            return m1.koga == (m1.VelocityR)/(m1.packVoid)*m1.ag*(((m1.packsize*m1.VelocityR)/(m1.packVoid*m1.visRich))**(-0.25))*(0.7**(-0.677))*(1)
        m1.KogaEq = Constraint(rule=KogaEq_)

        def VelocityREq_(m):
            return m1.VelocityR*m1.area == m1.FlowRVlat
            
        m1.VelocityREq = Constraint(rule=VelocityREq_)

        #m1.del_component(m.VelocityLEq)
        def VelocityLEq_(m):
            return m1.VelocityL*m1.area == m1.FlowLVlat
            
        m1.VelocityLEq = Constraint(rule=VelocityLEq_)

        def Flood1_(m):
            return m1.Flood == 249.089/0.3048*0.12*((m1.packfact*0.3048)**0.7)  
        m1.Flood1 = Constraint(rule = Flood1_) 
        
        def Flood3_(m):
            return m1.Flood >=  m1.FloodAct
        m1.Flood3 = Constraint(rule = Flood3_)
        
        def Flood2_(m):
            return m1.FloodAct ==(94*((m1.ReL**1.11)/(m1.ReG**1.8))+4.4)*6*(1-m1.packVoid)/(m1.packsize*((m1.packVoid)**3))*m1.RHOG*((m1.VelocityR)**2)
        
        m1.Flood2 = Constraint(rule = Flood2_)

        #m.del_component(m.ReynoldsG)
        def ReynoldsG_(m):
            return m1.ReG ==   m1.RHOG*m1.VelocityR/(m1.visRich*m1.SpecAreaPacking);
        m1.ReynoldsG = Constraint(rule = ReynoldsG_) 
        
        #m.del_component(m.ReynoldsL)
        def ReynoldsL_(m):
            return m1.ReL ==   m1.RHOL*m1.VelocityL/(m1.vis*m1.ai);
        m1.ReynoldsL = Constraint(rule = ReynoldsL_) 
        
        #m.del_component(m.Aid)
        def Aid_(m):
            return m1.ai ==  m1.SpecAreaPacking*(1-exp(-1.45*((0.075/m1.surften)**0.75)*((m1.RHOL*m1.VelocityR/(m1.vis*m1.SpecAreaPacking))**0.1)*((m1.SpecAreaPacking*(m1.VelocityR**2)/9.81)**(-0.05))*((m1.RHOL*(m1.VelocityR**2)/(m1.SpecAreaPacking*m1.surften))**0.2)));

        m1.Aid = Constraint(rule = Aid_) 

        def packingFactorEq_(m):
            return m1.packfact == (2.0034)*(m1.packsize**(-1.564))
        
        m1.packingFactorEq = Constraint(rule=packingFactorEq_)
        
        def AreaofPackingEq_(m):
            return m1.SpecAreaPacking == (5.0147)*(m1.packsize**(-0.978))
        
        m1.AreaofPackingEq = Constraint(rule=AreaofPackingEq_)  
        
        def AreaEq_(m):
            return m1.area == pi/4*(m1.diameter**2)
            
        m1.AreaEq = Constraint(rule=AreaEq_)
        
        #def PackingDensityEq_(m):
        #    return m.packDens == (-4E+06)*(m.packsize**(3))+ 653592*(m.packsize**(2))-31489*m.packsize + 1146.5
        
        #m.PackingDensityEq = Constraint(rule=PackingDensityEq_)
        
        def PackVoidEq_(m):
            return m1.packVoid == 0.0569*log(m1.packsize)+0.9114
        
        m1.PackVoidEq = Constraint(rule=PackVoidEq_)
        
        def PackCostEq_(m):
            return m1.PackCost == 397431*(m1.packsize**(2)) - 53449*(m1.packsize) + 2366.1
        
        m1.PackCostEq = Constraint(rule=PackCostEq_)   
        
        
        def PackSizeCons_(m):
            return m1.packsize *20 >= m1.diameter
        m1.PackSizeCons = Constraint(rule=PackSizeCons_)
        #========================================
        # OBJECTIVE and SOLVE
        #======================================== 
        #m.del_component(m.Obj3)        

        #print("is this the correct mass exchanger unit?")
        #print("Solve with proper objective")
        #m.del_component(m.Obj4)        
        def Obj4_(model):
           return m1.AF*23805*(m1.diameter**0.57)*1.15*m1.height + m1.AF*pi*(m1.diameter**2)/4*m1.height*m1.PackCost
       #m.AF*23805*(m.diameter**0.57)*1.15*m.height+\
       #                         m.AF*pi*(m.diameter**2)/4*m.height*m.PackCost

        m1.Obj4 = Objective( rule = Obj4_,sense=minimize)
        #m.Obj3.deactivate()
        #m.Obj4.activate() 
        presolve_clone = m1.clone()
        results = solve_until_feas_NLP(m1)
        #m.display()
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
       
        q= m1.AF*23805*(m1.diameter**0.57)*1.15*m1.height()
        w=m1.AF*pi*(m1.diameter()**2)/4*m1.height()*m1.PackCost
        print("fixcost",m.FixCost, "shell",q,"packing   ", w)
        print("results from 5th NLP")
        #m.CapCost.pprint()
        m1.height.pprint()
        m1.diameter.pprint()
        #m.ai.pprint()
        m1.area.pprint()
        m1.FloodAct.pprint()
        m1.Flood.pprint()  
        m1.ai.pprint()
        #m.ap.pprint()
        m1.packfact.pprint()
        m1.VelocityR.pprint()
        m1.VelocityL.pprint()
        m1.koga.pprint()
        m1.packsize.pprint()
        m1.PackCost.pprint()
        m1.SpecAreaPacking.pprint()
        m1.ReL.pprint()
        m1.ReG.pprint()
        m1.packVoid.pprint()
        print("All inlet and outlet concs:")
        q = m1.FlowRm.value*(m1.cR0[1].value-m1.cRs[self.nfe,self.ncp].value)
        print("mass exchanged R:  ", q )
        
        q = m1.FlowLm.value*(m1.cL0[1].value-m1.cLs[self.nfe, self.ncp].value)
        print("mass exchanged L:  ", q )
        #print("All inlet and outlet concs:")
        #print(m1.cR0[1].value, self.rich_in[self.rich_stream_name])
        #print(m1.cRs[self.nfe,self.ncp].value, self.rich_out[self.rich_stream_name])
        #print(m1.cL0[1].value, self.rich_in[self.lean_stream_name])
        #print(m1.cLs[self.nfe,self.ncp].value, self.rich_out[self.lean_stream_name])
        #print("number of variables", m1.nvariables())
        
        #print("number of constraints", m1.nconstraints())
        
        #m.display()
        print('=============================================================================================')
        print(results)
        #m.load(results)
        #elif (results.solver.termination_condition == TerminationCondition.infeasible) or (results.solver.termination_condition == TerminationCondition.maxIterations):  
        #    print("The exchanger problem could not be solved")
            #raise Exception("Could not find a valid model to continue iterations")
        m1.success = success_solve
        return m1, results, presolve_clone, success_solve
    
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
        m.del_component(m.loverdlo)
        
        def loverdlo_(m):
            return m.height >= 0.5*m.diameter
            
        m.loverdlo = Constraint(rule=loverdlo_)
        
        
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
        results = solve_until_feas_NLP(m)
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
        print("exchanger cost",q,"packing cost", w)
        print("All inlet and outlet concs:")
        print("All inlet and outlet concs:")
        q = m.FlowRm.value*(m.cR0[1].value-m.cRs[self.nfe,self.ncp].value)
        print("mass exchanged R:  ", q )
        
        q = m.FlowLm.value*(m.cL0[1].value-m.cLs[self.nfe, self.ncp].value)
        print("mass exchanged L:  ", q )
        #print("All inlet and outlet concs:")
        #print(m.cR0[1].value, self.rich_in[self.rich_stream_name])
        #print(m.cRs[self.nfe,self.ncp].value, self.rich_out[self.rich_stream_name])
        #print(m.cL0[1].value, self.rich_in[self.lean_stream_name])
        #print(m.cLs[self.nfe,self.ncp].value, self.rich_out[self.lean_stream_name])
        #print("number of variables", m.nvariables())
        
        #print("number of constraints", m.nconstraints())
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
        #print('=============================================================================================')
        #print(results)
        #m.load(results)
        #elif (results.solver.termination_condition == TerminationCondition.infeasible) or (results.solver.termination_condition == TerminationCondition.maxIterations):  
        #    print("The exchanger problem could not be solved")
            #raise Exception("Could not find a valid model to continue iterations")
        m.success = success_solve
        return m, results, presolve_clone, success_solve

    def full_exchanger_model(self):
        """ Constructs the the 5th pyomo model of 5 from no initial values.
        Contains all variables and model information.
        
        This will be attempted first to see whether the NLP initialization steps are necessary
        
        Args:
            None
            
        Returns:
            m (Concrete pyomo model): final solution.
            results (solver results): ipopt solver output.
            pre_solve_clone (clone of concrete model before solve statement): should only be used if solve failed
            success_solve (bool): flag as to whether the model solved
        
        """
        print("Setting up the full exchanger model from no inits")
        #=========================================
        #Variables from Previous NLP
        #=========================================

        m1 = ConcreteModel()
        
        #sets
        m1.ii = RangeSet((self.nfe))
        m1.jj = RangeSet((self.ncp))

        #Table a(jj,jj) First order derivatives collocation matrix
        a = {}
        a[1,1] = 0.19681547722366
        a[1,2] = 0.39442431473909
        a[1,3] = 0.37640306270047
        a[2,1] = -0.06553542585020
        a[2,2] = 0.29207341166523
        a[2,3] = 0.51248582618842
        a[3,1] = 0.02377097434822
        a[3,2] = -0.04154875212600
        a[3,3] = 0.11111111111111
        m1.a = Param(m1.jj,m1.jj, initialize = a)
        
        m1.ag = Param(initialize = 0.123)
        
        
        m1.height = Var(initialize = 2,bounds = (0.15, None))
        #=========================================
        #Parameters
        #=========================================
        #I will fix these here for now, but the plan is to load these from a seperate file
        #preferably for each component
        rhog={}
        rhol={}
        m1.surft={}
        m1.visR={}
        m1.visL={}
        count = 0
        for i in self._stream_properties.stream:
            if self._stream_properties.index[count]=='RHOG':
                rhog[i]=self._stream_properties.iloc[count]['value']
            if self._stream_properties.index[count]=='RHOL':
                rhol[i]=self._stream_properties.iloc[count]['value']
            if self._stream_properties.index[count]=='surften':
                m1.surft[i]=self._stream_properties.iloc[count]['value']
            if self._stream_properties.index[count]=='visRich':
                m1.visR[i]=self._stream_properties.iloc[count]['value']
            if self._stream_properties.index[count]=='vis':
                m1.visL[i]=self._stream_properties.iloc[count]['value']
            count+=1
            
        m1.de = Param(initialize=0.02)        
        
        #These need to come from data
        m1.RHOG = Param(initialize = rhog[self.rich_stream_name])
        m1.RHOL = Param(initialize = rhol[self.lean_stream_name])
        #Henry for mol SO2 per mol H2O = 0.0234, but in this eg, it is already inc
        m1.henry = Param(initialize = 1)
        #print("mTHIS IS THE MASS_FLOWS", self.mass_flows)
        m1.FlowRm = Param(initialize = self.mass_flows[self.rich_stream_name])
        m1.FlowLm = Param (initialize = self.mass_flows[self.lean_stream_name])
        #m.PackCost = Param(initialize = (self.ME_inits["packcost"]*self.ME_inits["packcostcor"]))
        m1.AF = Param(initialize = 0.2)
        m1.surften = Param(initialize = m1.surft[self.lean_stream_name])
        m1.visRich = Param(initialize = m1.visR[self.rich_stream_name])
        #m.visRich.pprint()
        #m.de = Param(initialize=0.02)        
        m1.vis = Param(initialize= m1.visL[self.lean_stream_name])
        #These need to come from data
        #m.RHOL.pprint()
        #sys.exit()
        #Henry for mol SO2 per mol H2O = 0.0234, but in this eg, it is already inc
        #m.henry = Param(initialize = 1)
        #m.FlowRm = Param(initialize = self.mass_flows['R1'])
        #m.FlowLm = Param (initialize = self.mass_flows['L2'])
        
        FlowRVlat = self.mass_flows[self.rich_stream_name]/m1.RHOG
        FlowLVlat = self.mass_flows[self.lean_stream_name]/m1.RHOL
        FlowLVcor = (self.mass_flows[self.lean_stream_name]/self.mass_flows[self.rich_stream_name])*((m1.RHOG/m1.RHOL)**0.5)
        
        m1.FlowRVlat =Param(initialize=FlowRVlat)
        m1.FlowLVlat =Param(initialize=FlowLVcor)
        #=========================================
        #Variables
        #=========================================
        flux_init = {}
        for i in m1.ii:
            for j in m1.jj:
                flux_init[i,j]=-1e-4

        cRs_init = {}

        for i in m1.ii:
            for j in m1.jj:
                cRs_init[i,j]=0.001

        cLs_init = {}

        for i in m1.ii:
            for j in m1.jj:
                cLs_init[i,j]=0.001
            
        cL0_init = {}

        for i in m1.ii:
            for j in m1.jj:
                cL0_init[i]= 0.001
                                        
        cR0_init = {}

        for i in m1.ii:
            for j in m1.jj:
                cR0_init[i]= 0.001
                    
        h0_init = {}

        for i in m1.ii:
            for j in m1.jj:
                h0_init[i]=0.01
                    
        cdotR_init = {}

        for i in m1.ii:
            for j in m1.jj:
                cdotR_init[i,j]=-1e-04
                    
        cdotL_init = {}

        for i in m1.ii:
            for j in m1.jj:
                cdotL_init[i,j]= -1e-04
                    
        hs_init = {}

        for i in m1.ii:
            for j in m1.jj:
                hs_init[i,j]=0.1
                    
        #flux of the contaminant from vapour
        m1.flux =Var(m1.ii,m1.jj, initialize = flux_init, bounds = (None, 0))
        m1.cRs = Var(m1.ii,m1.jj,within = NonNegativeReals, initialize = cRs_init)
        m1.cLs = Var(m1.ii,m1.jj,within = NonNegativeReals, initialize = cLs_init)
        m1.cR0 = Var(m1.ii,within = NonNegativeReals, initialize = cR0_init)
        m1.cL0 = Var(m1.ii,within = NonNegativeReals, initialize = cL0_init)
        m1.h0 = Var(m1.ii,within = NonNegativeReals, initialize = h0_init)
        
        m1.cdotR = Var(m1.ii,m1.jj, initialize = cdotR_init)
        m1.cdotL = Var(m1.ii,m1.jj, initialize = cdotL_init)
        
        m1.hs = Var(m1.ii,m1.jj,within = NonNegativeReals, initialize = hs_init)
        
        
        d = 0.5
        m1.diameter = Var(initialize =d, within = NonNegativeReals)

        m1.area = Var(initialize = 0.25, within = NonNegativeReals)

        m1.koga = Var(initialize = 0.04, within = NonNegativeReals)

        m1.VelocityR = Var(initialize = 1, bounds=(0.00001,None))
        
        m1.VelocityL = Var(initialize = 1, bounds=(0.00001,None)) 
        
        m1.ReL = Var(initialize = 100, bounds = (0.00001,None)) 
        
        m1.ReG = Var(initialize = 100, bounds = (1,None))

        m1.Flood = Var(initialize = 1000, within = NonNegativeReals)

        m1.FloodAct = Var(initialize = 1000, within = NonNegativeReals)
        
        m1.packfact = Var(initialize = 2000, bounds =(40,4000))

        m1.ai = Var(initialize = 150, within = NonNegativeReals) 
        
        m1.packsize = Var(initialize = 0.05, bounds=(0.005, None))
        m1.SpecAreaPacking = Var(initialize =150, bounds=(5, None))
        m1.packVoid = Var(initialize=0.68,bounds = (0.5, None))
        
        #m.del_component(m.PackCost)
        m1.PackCost = Var(initialize = (self.ME_inits["packcost"]*self.ME_inits["packcostcor"]), within = NonNegativeReals)
 
        #========================================
        #CONSTRAINTS
        #========================================

        #Differential Equations
        print("Number of finite elements: ", self.nfe)
        def FECOLcr_(m, ii,jj):
            return m1.cRs[ii,jj] ==  m1.cR0[ii] + m1.height/self.nfe*sum(m1.a[kk,jj]*m1.cdotR[ii,jj] for kk in m1.jj)
        m1.FECOLcr = Constraint(m1.ii,m1.jj, rule = FECOLcr_)

        def FECOLcl_(m, ii,jj):
            return m1.cLs[ii,jj] ==  m1.cL0[ii] + m1.height/self.nfe*sum(m1.a[kk,jj]*m1.cdotL[ii,jj] for kk in m1.jj)
        m1.FECOLcl = Constraint(m1.ii,m1.jj, rule = FECOLcl_)
        
        def FECOLch_(m, ii,jj):
            return m1.hs[ii,jj] ==  m1.h0[ii] + m1.height/self.nfe*sum(m1.a[kk,jj] for kk in m1.jj)
        m1.FECOLch = Constraint(m1.ii,m1.jj, rule = FECOLch_)
        
        #CONTINUITY EQUNS
        def CONcR_(m, ii):
            if ii == 1:
                return Constraint.Skip
            else:
                return m1.cR0[ii] ==  m1.cR0[ii-1] + m1.height/self.nfe*sum(m1.cdotR[ii-1,jj]*m1.a[jj,3] for jj in m1.jj)
        m1.CONcR = Constraint(m1.ii, rule = CONcR_)
        
        def CONcL_(m, ii):
            if ii == 1:
                return Constraint.Skip
            else:
                return m1.cL0[ii] ==  m1.cL0[ii-1] + m1.height/self.nfe*sum(m1.cdotL[ii-1,jj]*m1.a[jj,3] for jj in m1.jj)
        m1.CONcL = Constraint(m1.ii, rule = CONcL_)
        
        def CONtt_(m, ii):
            if ii == 1:
                return Constraint.Skip
            else:
                return m1.h0[ii] ==  m1.h0[ii-1] + m1.height/self.nfe*sum(m1.a[jj,3] for jj in m1.jj)
        m1.CONtt = Constraint(m1.ii, rule = CONtt_)
        
        # DIFFERENTIAL EQUATIONS
        
        def ODECL_(m, ii,jj):
            return m1.cdotL[ii,jj] ==  m1.flux[ii,jj]/m1.FlowLm
        m1.ODECL = Constraint(m1.ii,m1.jj, rule = ODECL_)
        
        
        def ODECR_(m, ii,jj):
            return m1.cdotR[ii,jj] ==  m1.flux[ii,jj]/m1.FlowRm
        m1.ODECR = Constraint(m1.ii,m1.jj, rule = ODECR_)

        #initial conditions
        def _init1(m):
            return m1.cR0[1] == self.rich_in[self.rich_stream_name]
        m1.initcon1 = Constraint(rule=_init1)
        def _init2(m):
            return m1.cRs[self.nfe, 3] == self.rich_out[self.rich_stream_name]
        m1.initcon2 = Constraint(rule=_init2)
        def _init3(m):
            return m1.cL0[1] == self.rich_in[self.lean_stream_name]
        m1.initcon3 = Constraint(rule=_init3)
        def _init4(m):
            return m1.cLs[self.nfe, 3] == self.rich_out[self.lean_stream_name]
        m1.initcon4 = Constraint(rule=_init4)        
        def _init5(m):
            return m1.h0[1] == 0
        m1.initcon5 = Constraint(rule=_init5)  
        
        def loverdup_(m):
            return m1.height <= 25*m1.diameter
            
        m1.loverdup = Constraint(rule=loverdup_)
        
        def loverdlo_(m):
            return m1.height >= 2*m1.diameter
            
        m1.loverdlo = Constraint(rule=loverdlo_)

        def TRateVap_(m, ii,jj):
            return m1.flux[ii,jj] == -m1.koga*m1.ai*m1.area*(m1.cRs[ii,jj]-m1.henry*m1.cLs[ii,jj])
        m1.TRateVap = Constraint(m1.ii,m1.jj, rule = TRateVap_)

        #m.del_component(m.KogaEq)
        def KogaEq_(m):
            return m1.koga == (m1.VelocityR)/(m1.packVoid)*m1.ag*(((m1.packsize*m1.VelocityR)/(m1.packVoid*m1.visRich))**(-0.25))*(0.7**(-0.677))*(1)
        m1.KogaEq = Constraint(rule=KogaEq_)

        def VelocityREq_(m):
            return m1.VelocityR*m1.area == m1.FlowRVlat
            
        m1.VelocityREq = Constraint(rule=VelocityREq_)

        def VelocityLEq_(m):
            return m1.VelocityL*m1.area == m1.FlowLVlat
            
        m1.VelocityLEq = Constraint(rule=VelocityLEq_)

        def Flood1_(m):
            return m1.Flood == 249.089/0.3048*0.12*((m1.packfact*0.3048)**0.7)  
        m1.Flood1 = Constraint(rule = Flood1_) 
        
        def Flood3_(m):
            return m1.Flood >=  m1.FloodAct
        m1.Flood3 = Constraint(rule = Flood3_)
        
        def Flood2_(m):
            return m1.FloodAct ==(94*((m1.ReL**1.11)/(m1.ReG**1.8))+4.4)*6*(1-m1.packVoid)/(m1.packsize*((m1.packVoid)**3))*m1.RHOG*((m1.VelocityR)**2)
        
        m1.Flood2 = Constraint(rule = Flood2_)

        def ReynoldsG_(m):
            return m1.ReG ==   m1.RHOG*m1.VelocityR/(m1.visRich*m1.SpecAreaPacking);
        m1.ReynoldsG = Constraint(rule = ReynoldsG_) 
        
        def ReynoldsL_(m):
            return m1.ReL ==   m1.RHOL*m1.VelocityL/(m1.vis*m1.ai);
        m1.ReynoldsL = Constraint(rule = ReynoldsL_) 
        
        def Aid_(m):
            return m1.ai ==  m1.SpecAreaPacking*(1-exp(-1.45*((0.075/m1.surften)**0.75)*((m1.RHOL*m1.VelocityR/(m1.vis*m1.SpecAreaPacking))**0.1)*((m1.SpecAreaPacking*(m1.VelocityR**2)/9.81)**(-0.05))*((m1.RHOL*(m1.VelocityR**2)/(m1.SpecAreaPacking*m1.surften))**0.2)));

        m1.Aid = Constraint(rule = Aid_) 

        def packingFactorEq_(m):
            return m1.packfact == (2.0034)*(m1.packsize**(-1.564))
        
        m1.packingFactorEq = Constraint(rule=packingFactorEq_)
        
        def AreaofPackingEq_(m):
            return m1.SpecAreaPacking == (5.0147)*(m1.packsize**(-0.978))
        
        m1.AreaofPackingEq = Constraint(rule=AreaofPackingEq_)  
        
        def AreaEq_(m):
            return m1.area == pi/4*(m1.diameter**2)
            
        m1.AreaEq = Constraint(rule=AreaEq_)
        
        def PackVoidEq_(m):
            return m1.packVoid == 0.0569*log(m1.packsize)+0.9114
        
        m1.PackVoidEq = Constraint(rule=PackVoidEq_)
        
        def PackCostEq_(m):
            return m1.PackCost == 397431*(m1.packsize**(2)) - 53449*(m1.packsize) + 2366.1
        
        m1.PackCostEq = Constraint(rule=PackCostEq_)   
        
        
        def PackSizeCons_(m):
            return m1.packsize *20 >= m1.diameter
        m1.PackSizeCons = Constraint(rule=PackSizeCons_)
        #========================================
        # OBJECTIVE and SOLVE
        #======================================== 
        #m.del_component(m.Obj3)        

        print("is this the correct mass exchanger unit?")
        print("Solve with proper objective")
        #m.del_component(m.Obj4)        
        def Obj4_(model):
           return m1.AF*23805*(m1.diameter**0.57)*1.15*m1.height + m1.AF*pi*(m1.diameter**2)/4*m1.height*m1.PackCost
       #m.AF*23805*(m.diameter**0.57)*1.15*m.height+\
       #                         m.AF*pi*(m.diameter**2)/4*m.height*m.PackCost

        m1.Obj4 = Objective( rule = Obj4_,sense=minimize)
        #m.Obj3.deactivate()
        #m.Obj4.activate() 
        presolve_clone = m1.clone()
        results = solve_until_feas_NLP(m1)
        #m.display()
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
       
        q= m1.AF*23805*(m1.diameter**0.57)*1.15*m1.height()
        w=m1.AF*pi*(m1.diameter()**2)/4*m1.height()*m1.PackCost
        print( "shell",q,"packing   ", w)
        print("results from 5th NLP")
        #m.CapCost.pprint()
        m1.height.pprint()
        m1.diameter.pprint()
        #m.ai.pprint()
        m1.area.pprint()
        m1.FloodAct.pprint()
        m1.Flood.pprint()  
        m1.ai.pprint()
        #m.ap.pprint()
        m1.packfact.pprint()
        m1.VelocityR.pprint()
        m1.VelocityL.pprint()
        m1.koga.pprint()
        m1.packsize.pprint()
        m1.PackCost.pprint()
        m1.SpecAreaPacking.pprint()
        m1.ReL.pprint()
        m1.ReG.pprint()
        m1.packVoid.pprint()
        print("All inlet and outlet concs:")
        q = m1.FlowRm.value*(m1.cR0[1].value-m1.cRs[self.nfe,self.ncp].value)
        print("mass exchanged R:  ", q )
        
        q = m1.FlowLm.value*(m1.cL0[1].value-m1.cLs[self.nfe, self.ncp].value)
        print("mass exchanged L:  ", q )
        print("All inlet and outlet concs:")
        #print(m1.cR0[1].value, self.rich_in[self.rich_stream_name])
        #print(m1.cRs[self.nfe,self.ncp].value, self.rich_out[self.rich_stream_name])
        #print(m1.cL0[1].value, self.rich_in[self.lean_stream_name])
        #print(m1.cLs[self.nfe,self.ncp].value, self.rich_out[self.lean_stream_name])
        #print("number of variables", m1.nvariables())
        
        #print("number of constraints", m1.nconstraints())
        
        #m.display()
        print('=============================================================================================')
        print(results)
        #m.load(results)
        #elif (results.solver.termination_condition == TerminationCondition.infeasible) or (results.solver.termination_condition == TerminationCondition.maxIterations):  
        #    print("The exchanger problem could not be solved")
            #raise Exception("Could not find a valid model to continue iterations")
        m1.success = success_solve
        return m1, results, presolve_clone, success_solve
    
    def find_detailed_exchanger_design(self, FE_analysis = False):
        """ finds the detailed exchanger design based on the inputs provided to the class
        
        It does so by first trying to solve the full problem without initializations from the other
        functions. If it does find a feasible exchanger first time then it returns this. If not, the
        full initialization scheme is used. If the option to perform the FE analysis is on then the
        model will change the number of finite elements to determine what the best number of elements
        for the particular boundary conditions.
        
        Args:
            FE_analysis (bool, optional): when FE_analysis is on the FE analysis is performed on this exchanger
            
        Returns:
            m (Concrete pyomo model): final solution.
            results (solver results): ipopt solver output.
            pre_solve_clone (clone of concrete model before solve statement): should only be used if solve failed
            success_solve (bool): flag to tell whether we have a feasible exchanger
        """
        print("First trying to solve the exchanger with no initializations")
        
        ME5, ME5results, presolve_5, success = self.full_exchanger_model()
        
        if success == False:
            ME1, success1, presolve_1 = self.Construct_pyomo_model()
            ME2, success2, presolve_2 = self.Construct_pyomo_model_2(ME1, success1, presolve_1)
            ME3, success3, presolve_3 = self.Construct_pyomo_model_3(ME2, success2, presolve_2)
            ME4, success4, presolve_4 = self.Construct_pyomo_model_4(ME3, success3, presolve_3)
            ME5, ME5results, presolve_5, success = self.Construct_pyomo_model_5(ME4, success4, presolve_4)
            
            if success == False:
                print("5th NLP has failed for this match. Relaxing bounds on the L / D ratio")
                ME6, ME6results, presolve_6, success6 = self.Construct_pyomo_model_6(ME5, success, presolve_5)
                
                if success6 == True:
                    ME5 = ME6
                    ME5results = ME6results
                    success = success6
                else:
                    success = False
        else:
            print("We found a solution to the exchanger on the first try with lazy inits!")
            
        return ME5, ME5results

'''
CRin_Side = {}
CRin_Side['R1'] = 0.07
CRin_Side['L2'] = 0.045

CRout_Side = {}
CRout_Side['R1'] = 0.017
CRout_Side['L2'] = 0.013680236

FlowM = {}
FlowM['R1'] = 0.9
FlowM['L2'] = 1.523
i = 'R1'
j='L2'

ME_inits = dict()
ME_inits["height"]=2
ME_inits["kw"]=0.05
ME_inits["kwcor"]=1
ME_inits["surfarea"]=300
ME_inits["surfacor"]=1
ME_inits["diameter"]=0.35
ME_inits["diacor"]=1
ME_inits["packcostcor"]=1
ME_inits["packcost"]=1500

dataDirectory = os.path.abspath(
    os.path.join( os.path.dirname(os.path.abspath(inspect.getfile(
        inspect.currentframe() ) ) ),'../example_data'))


filenameP = os.path.join(dataDirectory,'problem_parameters.csv')
problem_parameters = read_stream_data(filenameP)

filenameSP = os.path.join(dataDirectory,'stream_properties.csv')
stream_properties = read_stream_data(filenameSP)  

mx = mass_exchanger(rich_stream_name = i, lean_stream_name=j,rich_in_side=CRin_Side, rich_out_side=CRout_Side,flowrates=FlowM,stream_properties = stream_properties, me_inits=ME_inits)
ME1, success1, presolve_1 = mx.Construct_pyomo_model()
ME2, success2, presolve_2 = mx.Construct_pyomo_model_2(ME1, success1, presolve_1)
ME3, success3, presolve_3 = mx.Construct_pyomo_model_3(ME2, success2, presolve_2)
ME4, success4, presolve_4 = mx.Construct_pyomo_model_4(ME3, success3, presolve_3)
ME5, ME5results, presolve_5, success = mx.Construct_pyomo_model_5(ME4, success4, presolve_4)
#ME6, ME6results, presolve_6, success6 = mx.Construct_pyomo_model_6(ME5, success, presolve_5)
#ME3 = mx.Construct_pyomo_model_3(ME2)
#ME4 = mx.Construct_pyomo_model_4(ME3)
#ME5 = mx.Construct_pyomo_model_5(ME4)
'''