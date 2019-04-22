*230   FBHU
*240   Solar thermal

SCALARS

NLUT number of lean streams /3/
NRPS number of rich streams  /5/
NREG number of regenerating streams /1/

nhut number of hot utilities /2/
ncut number of cold utilities /0/

SETS
*===============================================================================
I rich streams  /1*5/
ih hot streams /1*3/
J lean streams and lean utilities /1*3/
jc cold streams /1*2/
R regenerating stream            /1*1/
K composition locations /1*4/
kh temperature locations  nok + 1 /1*4/
P Number of periods         /1*2/
DATA   data    /CIN, COUT, tin, tout,F,h,COST,costhens, m/


ALIAS
(J, JJ);
*Need to confirm this as well
*===============================================================================
PARAMETERS
RPS(I,P)      rich process streams
LPS(J,P)      lean process streams
RES(R,P)      regenerating streams
ST(P,K)       stages
FIRST(P,K)    first composition location
LAST(P,K)     last composition location
first_tlrich(P,k)
SECLAST(P,K)  second last composition location
ms_st(P,k)    mass transfer stages
lut_st(P,k)   lean utility stages
HEIGHT(I,J,K) height of mass exchange unit
RHEIGHT(J,R)  height of regenerating unit


hut(ih,P)             hot utilities
hps(ih,P)             hot process streams
cps(jc,P)             cold process streams
cut(jc,P)             cold utilities
sth(P,kh)              stages
firsth(P,kh)           first temperature location
lasth(P,kh)            last temperature location
hx_st(P,kh)           heat recovery stages
hut_st(P,kh)          hot utility stages
cut_st(P,kh)          cold utility stages
fhps(P,kh)            first temperature location of hps(ih)
fcps(P,kh)            first temperature location of cps(jc)
first_tlhot(P,Kh)     intervals where hps(ih) exist
last_tlhot(P,Kh)      last temperature location of hps(ih)
first_tlcold(P,Kh)    intervals where cps(jc) exist
last_tlcold(P,Kh)     last temperature location of cps(jc);




RPS(I,P)            =YES$(ORD(I) <= NRPS);
LPS(J,P)            =YES$(ORD(J) <= NLUT);
RES(R,P)            =YES$(ORD(R) <= NREG);
ST(P,K)             =YES$(ORD(K) < CARD(K));
LAST(P,K)           =YES$(ORD(K) = CARD(K));
SECLAST(P,K)        =YES$(ORD(K) = card(k)-1);
first(P,k)          =yes$(ord(k) eq 1);
first_tlrich(P,k)   = yes$(ord(k)>=1 and ord(k) <card(k));
ms_st(P,k)          =yes$(ord(k)>=1 and ord(k)<card(k));


sth(P,kh)            = yes$(ord(kh) < card(kh))  ;
firsth(P,kh)          = yes$(ord(kh) eq 1)        ;
lasth(P,kh)          = yes$(ord(kh) eq card(kh))  ;
hut(ih,P)            = yes$(ord(ih) <=nhut);
cut(jc,P)            = yes$(ord(jc) > 1+ncut);
hps(ih,P)            = yes$(ord(ih) >nhut);
cps(jc,P)            = yes$(ord(jc) <=1+ncut);
hut_st(P,kh)         = yes$(ord(kh)=1);
cut_st(P,kh)         = yes$(ord(kh)=card(kh)-1);
hx_st(P,kh)          = yes$(ord(kh)>1 and ord(kh)<=card(kh)-2);
fhps(P,kh)           = yes$(ord(kh)=2);
fcps(P,kh)           = yes$(ord(kh)=card(kh)-1);
first_tlhot(P,kh)    = yes$(ord(kh)>=2 and ord(kh) <card(kh));
last_tlhot(P,kh)     = yes$(ord(kh)=card(kh));
first_tlcold(P,kh)   = yes$(ord(kh)<=card(kh)-2);
last_tlcold(P,kh)    = yes$(ord(kh)=1);
*===============================================================================
*Rich stream data for Example 4 of Simultaneous synthesis of mass exchange networks for waste minimization

*$ONTEXT
TABLE RICH(I,P,DATA) Rich streams data
       CIN           COUT           F
1.1   0.0800        0.00650        0.02
1.2   0.0800        0.00650        0.02
2.1   0.0800        0.00250        0.06
2.2   0.0800        0.00250        0.06
3.1   0.01100       0.00250        0.85
3.2   0.01100       0.00250        0.85
4.1   0.01000       0.00500        .315
4.2   0.01000       0.00500        .315
5.1   0.00800       0.00250        .25
5.2   0.00800       0.00250        .25;
*$OFFTEXT

TABLE LEAN(J,P,DATA) Lean streams data
             CIN            COUT
1.1        0.00204        0.00852
1.2        0.00204        0.00852
2.1        0.00250        0.00850
2.2        0.00250        0.00850
3.1        0.0002         0.00950
3.2        0.0002         0.00950;


TABLE ZEAN(R,P,DATA) Regenerating streams data
             CIN            COUT
1.1        0.00006         0.002
1.2        0.00006         0.002;



TABLE HOTS(Ih,P,DATA) Hot streams data
           TIN        TOUT       H          F         COST
1.1        120         60       0.2       0.00        0.0
1.2        110         50       0.2       0.00        0.0
2.1        150         150      0.2       0.00        235
2.2        150         150      0.2       0.00        235
3.1        100         20       0.2       0.647        0.0
3.2        100         20       0.2       0.647        0.0 ;


TABLE COLDS(Jc,P,DATA) Cold streams data
          TIN        TOUT        H            F         COST
1.1        20         100       0.2         0.647         0
1.2        20         100       0.2         0.647         0
2.1        0          10        0.2         0.00         1.3
2.2        0          10        0.2         0.00         1.3;


PARAMETER
*Capital cost parameters
AF          Annualisation factor
AFM
ACH         Annual cost per height of continuous contact column
ACS         Annual cost per stage of tray columns
D           Area cost exponent for mass exchangers
Kw          Lumped mass transfer coefficient
AC(J)       Annual operating cost per unit of lean stream
AZ(R,P)       Annual operating cost per unit of regenerating stream
EMAC        Exchanger minimum approach composition
INT(K)      Interval in superstructure
OMEGA(I,J,P)
OMEGA1(J,R,P)
CLUTIN      Inlet concentration of external MSA
CLUTOUT     Outlet concentration of external MSA
W
INTRATE
OrigAOC
HEIGHTMENS(I,J,P,K)
HEIGHTREG(J,R,P)
MASSREG(R,P)
H           Height of exchanger between streams I and J in interval K;



ACH=0;  D=0.66;
*AC('1')=10000;
*AC('2')=10000;
AC('1')=120000;
AC('2')=120000;
AC('3')=0; AZ('1',P)=58200;  KW=0.02; AF=.225; W=.1;
EMAC=.0000001;  INTRATE =0.3;  OrigAOC=408480;



PARAMETER
*Used in Logical constraint for mass exchange in match (I,J,K)
OMEGA(I,J,P);
OMEGA(I,J,P)=.01;


OMEGA1(J,R,P)=0.001;
*MAX(0,LEAN(J,'CIN')-RICH(I,'CIN'),LEAN(J,'CIN')-RICH(I,'COUT'),
*LEAN(J,'COUT')-RICH(I,'CIN'),LEAN(J,'COUT')-RICH(I,'COUT'));

PARAMETER
*Capital cost parameters
AF           Annualisation factor
AF2
CF           Investment cost
AChens           Area cost
AE           Area cost index
gamma(ih,jc,P)
EMAT         Exchanger minimum approach temperature
NOP
DOP(P)       Duration of period P
TAMB(P)
GHI(P)
RHO(IH,P)
CP(IH,P)
INSFACTOR(P)
EFFMAX
SCONST1
SCONST2
solarareacost
STORAGETANKCOST;

AF= 0.2;   AF2= 0.2; CF=8333.3;     AChens = 641.7;       AE = 1;
NOP=24;  DOP('1')=8;  DOP('2')=16;     AFM=0;


gamma(ih,jc,P) = .0000000000001;

*gamma(ih,jc,P)=max(0,colds(jc,P,'tin') - hots(ih,P,'tin'), colds(jc,P,'tin') - hots(ih,P,'tout'),
*                colds(jc,P,'tout') - hots(ih,P,'tin'), colds(jc,P,'tout') - hots(ih,P,'tout')) ;

*===============================================================================
*Ambient temperature for each period p
TAMB('1')= 32;
TAMB('2')= 32;

*Global horizontal irradiation for each period p
GHI('1')= .800;
GHI('2')= .800;

*Operating hours
INSFACTOR('1')=8100;
INSFACTOR('2')=8100;

*Density of thermal storage fluid
RHO('1','2') =1000;

*Heat capacity of thermal storage fluid
CP('1','2') = 4.200;

*Efficiency of solar panel
EFFmax = .764;

*Experimental constants for solar panel
SCONST1= .00153;
SCONST2= .0000003;

*Cost of solar panel per area
solarareacost= 100;

*Cost of storage tank per volume
STORAGETANKCOST = 50;
*===============================================================================
INT(K)$(ORD(K)LT CARD(K))=1;
*===============================================================================
PARAMETER
AREX(i,j,P,k)
A_CKR_FIRST(I,P,K)   DEFINE FIRST INTERVAL OF ALL RICH PROCESS STREAMS (I)
A_CKL_FIRST(J,P,K)   DEFINE FIRST INTERVAL OF ALL LEAN PROCESS STREAMS(J)
A_CKR_LAST(I,p,K)
A_CKL_LAST(J,P,K)
A_CKL_LASTEXT(J,P,K)
A_I(I,P,K)           DEFINE INTERVALS IN WHICH RICH STREAMS EXIST(I)
A_RPS(I,P,K)         DEFINE INTERVALS IN WHICH RICH PROCESS STREAM RPS(I) EXIST
A_LPS(J,P,K)         DEFINE INTERVALS IN WHICH LEAN PROCESS STREAM LPS(J)EXIST
MATCH(I,J,P,K)       DEFINE POSSIBLE MATCHES BETWEEN STREAMS I-J IN INTERVAL K
COMP_IN_RICH(I,P,K)
COMP_IN_LEAN(J,P,K)
COMP_OUT_RICH(I,P,K)
COMP_OUT_LEAN(J,P,K)



COMP_OUTEXT_LEAN(J,P,K);

*INITIALIZE FLAGS
A_CKR_FIRST(I,P,K)$ST(P,K)=0;
A_I(I,P,K)=0;
A_RPS(I,P,K)=0;
A_LPS(J,P,K)=0;
*A_LUT(I,J,K)=0;
MATCH(I,J,P,K)=0;
COMP_IN_RICH(I,P,K)=0;
COMP_IN_LEAN(J,P,K)=0;
COMP_OUT_RICH(I,P,K)=0;
COMP_OUT_LEAN(J,P,K)=0;
COMP_OUTEXT_LEAN(J,P,K)=0;
*===============================================================================
*Second set of existance conditionals

A_CKR_FIRST(I,P,K)$(RICH(I,P,'CIN') = ORD(K))=1;
A_CKL_FIRST(J,P,K)$(LPS(J,P) AND (LEAN(J,P,'CIN')))  = CARD(K)=1;
*===============================================================================
*First set of existance conditionals
A_RPS(I,P,K)$(ST(P,K) AND RPS(I,P) AND FIRST_tlrich(P,K)) =1;
A_LPS(J,P,K)$(LPS(J,P)  AND FIRST_tlrich(P,K))=1;

MATCH(I,J,P,K)$((A_RPS(I,P,K) AND A_LPS(J,P,K)))=1;
COMP_IN_RICH(I,P,K)$RPS(I,P)= FIRST(P,K);
COMP_IN_LEAN(J,P,K)$LPS(J,P)=LAST(P,K);

COMP_OUT_RICH(I,P,K)= LAST(P,K);
COMP_OUT_LEAN(J,P,K)= FIRST(P,K);

AREX('1','1',P,'3')  =1;
*AREX('2','1',P,'2')  =1;
*AREX('2','1',P,'3')  =1;
AREX('2','3',P,'2')  =1;
AREX('3','1',P,'3')  =1;
AREX('4','2',P,'1')  =1;
AREX('5','3',P,'3')  =1;


DISPLAY RPS, LPS, K, first, last, ms_st, ST, A_CKR_FIRST, A_CKL_FIRST, A_RPS, A_LPS, MATCH, COMP_IN_LEAN, COMP_IN_RICH, SECLAST;


PARAMETER
*Flags
a_hps(ih,P,kh)        intervals in which hps(ih) are present
a_cps(jc,P,kh)        intervals in which cps(jc) are present
a_hut(ih,P,kh)        intervals in which hot utilities are present
a_cut(jc,P,kh)        intervals in whc cold utilities are present
matchh(ih,jc,p,kh)     define possible macthes between streams ih and jc in interval kh
temp_in_hot(ih,P,kh)
temp_in_cold(jc,P,kh);


*Initialise flags
a_hps(ih,P,kh)$(hps(ih,P) and first_tlhot(p,kh))= 1;
a_cps(jc,P,kh)$(cps(jc,P) and first_tlcold(p,kh))= 1;
a_hut(ih,p,kh)= 0;
a_cut(jc,p,kh)= 0;
matchh(ih,jc,p,kh)=0;
temp_in_hot(ih,p,kh)=0;
temp_in_cold(jc,p,kh)=0;


*Assign flag values
a_hut(ih,p,kh)$(hut(ih,p) and hut_st(p,kh))=1;
a_cut(jc,p,kh)$(cut(jc,p) and cut_st(p,kh))=1;
matchh(ih,jc,p,kh)$(sth(p,kh) and ((a_hps(ih,p,kh) and a_cps(jc,p,kh)$(hps(ih,p) and cps(jc,p))) or (a_cut(jc,p,kh)$((hps(ih,p) and cut(jc,p)))) or (a_hut(ih,p,kh)$((hut(ih,p) and cps(jc,p))))))=1;
temp_in_hot(ih,p,kh)$hps(ih,p)=fhps(p,kh);
temp_in_cold(jc,p,kh)$cps(jc,p)= fcps(p,kh);

Display p,hut, hps, cps, cut, kh, st, first, last, hut_st, cut_st, hx_st, fhps, fcps, first_tlhot,  last_tlhot,  first_tlcold,  last_tlcold, a_hps, a_cps, a_hut, a_cut, matchh,temp_in_hot, temp_in_cold;
*===============================================================================
*===============================================================================
VARIABLES
CAPINVEST        TOTAL ANNUAL COST
DUMMY
Investment
Annualcost
dt(ih,jc,p,kh)  approach between ih and jc in period p at location kh;

*===============================================================================
BINARY VARIABLE
Y1(I,J,K)    Binary variable for match between rich and lean streams
Z(J,R)
yh(ih,jc,kh); ;
*Binary variable for match between lean and regenerating streams

*===============================================================================
POSITIVE VARIABLES
CR(I,P,K)            RICH STREAM COMPOSITION AT LOCATION K
CL(J,P,K)            LEAN STREAM COMPOSITION AT LOCATION K
AVLEAN(J,P)          Mass load of lean streams
M(I,J,P,K)           MASS EXCHANGED between rich stream i and lean stream j in interval k
L(J,P)               FLOWRATE OF LEAN USED(J)ALL INCLUDED
V(R,P)               FLOWRATE OF REGENERATING STREAM USED
DC(I,J,P,K)          COMPOSITION DIFERENCE BETWEEN PAIR OF STREAM (I.J) IN STAGE K
*DC2(I,J,K)         Applies to tray columns
*DC3(I,J,K)         Applies to tray columns
DR(J,R,P,K)          COMPOSITION DIFFERENCE BETWEEN PAIR OF STREAM (J.R)
PNHC(I,J,K)        POSITIVE TOLERANCE
SNHC(I,J,K)        NEGATIVE TOLERANCE
Y(I,J,K)
MX(I,J,K)
MXR(R)


th(ih,p,kh)    temperature of  hot stream ih as it enters stage kh
tc(jc,p,kh)    temperature of cold stream jc as it leaves stage kh
q(ih,jc,p,kh)   energy exchanged between ih and jc in stage kh
AREA_SOLAR_1(ih,Jc,Kh)
AREA_SOLAR_2(ih,Jc,Kh)
SIZE_TANK_2(IH,Jc,Kh)
AX(ih,Jc,kh)                              ;
*===============================================================================
EQUATIONS
CRICH_OUT(I,P,K)
CLEAN_OUT(J,P,K)
*CLEANEXT_OUT(J,K)
AVLEAN1(J,P)
CRICH_IN(I,P,K)             ASIGNMENT OF RICH PROCESS STREAM INLET COMPOSITION
CLEAN_IN(J,P,K)             ASIGNMENT OF LEAN PROCESS STREAM INLET COMPOSITION
TOTAL_MASS_RICH(I,P)        TOTAL MASSS BALANCE OF RICH PROCESS STREAM RPS(I)
TOTAL_MASS_LEAN(J,P)        TOTAL MASS BALANCE OF LEAN PROCESS STREAM LPS(I)
TOTAL_MASS_REG(R,P)         TOTAL MASS BALANCE OF REGENERATING STREAM RES(R)
*TOTAL_MASS_LEAN1(J)
STAGE_MASS_RICH(I,P,K)      STAGE MASS BALANCE OF RICH PROCESS STREAM RPS(I)
STAGE_MASS_LEAN(J,P,K)      STAGE MASS BALANCE OF LEAN PROCESS STREAM LPS(I)
MONOT_RICH(I,P,K)           MONOTONICITY ON CONCENTRATIONS - CONSTRAINT
MONOT_LEAN(J,P,K)           MONOTONICITY ON CONCENTRATIONS - CONSTRAINT

PM(I,J,P,K)
S(I,J,P,K)
N1(I,J,P,K)

LOG_M_RPS_LPS(I,J,P,K)      LOGICAL CONSTRAINT ON MASS EXCHANGED BETWEEN RPS(I) AND LPS(J)

LOG_DC_RPS_LPS_RS(I,J,P,K)  LOGICAL CONSTRAINT ON RICH SIDE COMPOSITION DIFFERENCE BETWEEN RPS(I) AND LPS(J)
LOG_DC_RPS_LPS_RS1(I,J,P,K) LOGICAL CONSTRAINT ON RICH SIDE COMPOSITION DIFFERENCE BETWEEN RPS(I) AND LPS(J)
LOG_DC_RPS_LPS_LS(I,J,P,K)  LOGICAL CONSTRAINT ON LEAN SIDE COMPOSITION DIFFERENCE BETWEEN RPS(I) AND LPS(J)
LOG_DC_RPS_LPS_LS1(I,J,P,K) LOGICAL CONSTRAINT ON LEAN SIDE COMPOSITION DIFFERENCE BETWEEN RPS(I) AND LPS(J)

MX1(I,J,P,K)
MXR1(R,P)

OBJECTIVE                OBJECTIVE FUNCTION



THOT_IN(Ih,p,Kh) ASIGNMENT OF HOT PROCESS STREAM INLET TEMPERATURES
TCOLD_IN(Jc,p,Kh) ASIGNMENT OF COLD PROCESS STREAM INLET TEMPERATURES
TOTAL_HEAT_HOT(Ih,p)   TOTAL HEAT BALANCE OF HOT PROCESS STREAM HPS(I)
TOTAL_HEAT_COLD(Jc,p)  TOTAL HEAT BALANCE OF COLD PROCESS STREAM CPS(I)
*TOTAL_HEAT_HOT1(Ih,p)
*TOTAL_HEAT_COLD1(Jc,p)

STAGE_HEAT_HOT(Ih,p,Kh)   STAGE HEAT BALANCE OF HOT PROCESS STREAM HPS(I)
STAGE_HEAT_COLD(Jc,p,Kh)   STAGE HEAT BALANCE OF COLD PROCESS STREAM CPS(I)

LEANTOHENS1(IH,J,P)
LEANTOHENS2(JC,J,P)

SOLAR_HEAT_1(Ih,Jc,P,Kh)
SOLAR_HEAT_2(Ih,Jc,P,Kh)
SIZE_STORAGETANK_2(Ih,Jc,p,Kh)

MONOT_HOT(Ih,p,Kh)  MONOTONICITY ON TEMPERATURES - CONSTRAINT
MONOT_COLD(Jc,p,Kh) MONOTONICITY ON TEMPERATURES - CONSTRAINT

LOG_Q_HPS_CPS(Ih,Jc,p,J,Kh) LOGICAL CONSTRAINT ON HEAT EXCHANGED BETWEEN HPS(I) AND CPS(J)
LOG_Q_HPS_CUT(Ih,Jc,p,Kh) LOGICAL CONSTRAINT ON HEAT EXCHANGED BETWEEN HPS(I) AND CUT(J)
LOG_Q_HUT_CPS(Ih,Jc,p,Kh) LOGICAL CONSTRAINT ON HEAT EXCHANGED BETWEEN HUT(I) AND CPS(J)

LOG_DT_HPS_CPS_HS(Ih,Jc,p,Kh)  LOGICAL CONSTRAINT ON HOT SIDE TMEPERATURE DIFFERENCE BETWEEN HPS(I) AND CPS(J)
LOG_DT_HPS_CPS_CS(Ih,Jc,p,Kh)  LOGICAL CONSTRAINT ON COLD SIDE TMEPERATURE DIFFERENCE BETWEEN HPS(I) AND CPS(J)

LOG_DT_HPS_CUT_HS(Ih,Jc,p,Kh)  LOGICAL CONSTRAINT ON HOT SIDE TMEPERATURE DIFFERENCE BETWEEN HPS(I) AND CUT(J)
LOG_DT_HPS_CUT_CS(Ih,Jc,p,Kh)  LOGICAL CONSTRAINT ON COLD SIDE TMEPERATURE DIFFERENCE BETWEEN HPS(I) AND CUT(J)

LOG_DT_HUT_CPS_HS(Ih,Jc,p,Kh)  LOGICAL CONSTRAINT ON HOT SIDE TMEPERATURE DIFFERENCE BETWEEN HUT(I) AND CPS(J)
LOG_DT_HUT_CPS_CS(Ih,Jc,p,Kh)  LOGICAL CONSTRAINT ON COLD SIDE TMEPERATURE DIFFERENCE BETWEEN HUT(I) AND CPS(J)
AX1(ih,Jc,P,kh)
AOC
INVEST
;

*OBJECTIVEh OBJECTIVE FUNCTION;

*MODEL EQUATIONS
*===============================================================================
*===============================================================================
*assignment of stream inlet compositions
CRICH_IN(I,P,K)$(RPS(I,P) AND COMP_IN_RICH(I,P,K)).. CR(I,P,K) =E= RICH(I,P,'CIN');
CLEAN_IN(J,P,K)$(LPS(J,P) AND COMP_IN_LEAN(J,P,K)).. CL(J,P,K) =E= LEAN(J,P,'CIN');


CRICH_OUT(I,P,K)$(RPS(I,P) AND COMP_OUT_RICH(I,P,K)).. CR(I,P,K) =E= RICH(I,P,'COUT');
CLEAN_OUT(J,P,K)$(LPS(J,P) AND COMP_OUT_LEAN(J,P,K)).. CL(J,P,K) =E= LEAN(J,P,'COUT');
*ISN'T IT MISSING FOR REGENERATION STREAM?


*assignment of stream inlet temperatures

thot_in(ih,p,kh)$(hps(ih,p) and temp_in_hot(ih,p,kh))..
  th(ih,p,kh) =e= hots(ih,p,'tin');

tcold_in(jc,p,kh)$(cps(jc,p) and temp_in_cold(jc,p,kh))..
  tc(jc,p,kh) =e= colds(jc,p,'tin');
*===============================================================================
PM(I,J,P,K)$(ST(P,K) AND A_RPS(I,P,K)) .. PNHC(I,J,K) =E=.01;
S(I,J,P,K)$(ST(P,K) AND A_RPS(I,P,K)) .. SNHC(I,J,K) =E=.01;

N1(I,J,P,K)$(INT(K) AND A_RPS(I,P,K))..Y(I,J,K) =E= Y1(I,J,K)+(PNHC(I,J,K)-SNHC(I,J,K));
*=====================================================================================
*Available mass in lean stream J
AVLEAN1(J,P)..AVLEAN(J,P) =E= L(J,P)*(LEAN(J,P,'COUT')-LEAN(J,P,'CIN'));

*===============================================================================
*stream overall mass balance
TOTAL_MASS_RICH(I,P)$RPS(I,P) ..  RICH(I,P,'F')*(RICH(I,P,'CIN')-RICH(I,P,'COUT')) =E=
                              SUM((J,K)$(AREX(I,J,P,K)), M(I,J,P,K));

TOTAL_MASS_LEAN(J,P)$LPS(J,P).. L(J,P)*(LEAN(J,P,'COUT')-LEAN(J,P,'CIN')) =e=SUM((I,K)$(AREX(I,J,P,K)),M(I,J,P,K));

TOTAL_MASS_REG(R,P)$RES(R,P)..V(R,P)*(ZEAN(R,P,'COUT')-ZEAN(R,P,'CIN'))=e=SUM((I,K)$(AREX(I,'3',P,K)),M(I,'3',P,K));

*stream overall enthalpy balance


TOTAL_HEAT_HOT(Ih,p)$(HPS(Ih,p))..  HOTS(Ih,p,'F')*(HOTS(Ih,p,'TIN')-HOTS(Ih,p,'TOUT')) =e=
                              SUM((Jc,Kh)$(MATCHH (ih,jc,p,kh)), Q(Ih,Jc,p,Kh));

TOTAL_HEAT_COLD(Jc,p)$(CPS(Jc,p)).. COLDS(Jc,p,'F')*(COLDS(Jc,p,'TOUT')-COLDS(Jc,p,'TIN')) =e=
                              SUM((Ih,Kh)$(MATCHH (ih,jc,p,kh)), Q(Ih,Jc,p,Kh));
*=================================================================================
*stream stage mass exchange
STAGE_MASS_RICH(I,P,K)$(RPS(I,P) AND SUM(J,AREX(I,J,P,K)))..
RICH(I,P,'F')*(CR(I,P,K)-CR(I,P,K+1)) =E= SUM(J$AREX(I,J,P,K), M(I,J,P,K));

STAGE_MASS_LEAN(J,P,K)$(LPS(J,P) AND SUM(I,AREX(I,J,P,K)))..
L(J,P)*(CL(J,P,K)-CL(J,P,K+1)) =E= SUM(I$AREX(I,J,P,K), M(I,J,P,K));


*stream stage heat exchange

STAGE_HEAT_HOT(Ih,p,Kh)$(HPS(Ih,p) AND SUM(Jc,MATCHH (ih,jc,p,kh)))..
HOTS(Ih,p,'F')*(TH(Ih,p,Kh)-TH(Ih,p,Kh+1)) =e= SUM(Jc$MATCHH (ih,jc,p,kh), Q(Ih,Jc,p,Kh));

STAGE_HEAT_COLD(Jc,p,Kh)$(CPS(Jc,p) AND SUM(Ih,MATCHH (ih,jc,p,kh)))..
COLDS(Jc,p,'F')*(TC(Jc,p,Kh)-TC(Jc,p,Kh+1)) =e= SUM(Ih$MATCHH (ih,jc,p,kh), Q(Ih,Jc,p,Kh));


LEANTOHENS1('3','3',P)..
HOTS('3',p,'F')=L=L('3',P);

LEANTOHENS2('1','3',P)..
COLDS('1',p,'F')=L=L('3',P);

*========================================================================================================================================================
SOLAR_HEAT_1(Ih,Jc,P,Kh)$(HPS(ih,P) and MATCHH('1',Jc,'1',Kh))..
AREA_SOLAR_1('1',Jc,Kh)=G=
(Q('1',Jc,'1',Kh)/((effmax*GHI('1'))-((SCONST1)*(((HOTS('1','1','TIN')+HOTS('1','1','TOUT'))/2)-(TAMB('1'))))-((SCONST2)*((((HOTS('1','1','TIN')+HOTS('1','1','TOUT'))/2)-(TAMB('1')))**2))));

SOLAR_HEAT_2(Ih,Jc,P,Kh)$(HPS(ih,P) and MATCHH('1',Jc,'1',Kh) )..
AREA_SOLAR_2('1',Jc,Kh)=G=
(Q('1',Jc,'1',Kh)/((effmax*GHI('1'))-((SCONST1)*(((HOTS('1','1','TIN')+HOTS('1','1','TOUT'))/2)-(TAMB('1'))))-((SCONST2)*((((HOTS('1','1','TIN')+HOTS('1','1','TOUT'))/2)-(TAMB('1')))**2))));


SIZE_STORAGETANK_2(Ih,Jc,p,Kh)$(HPS(IH,P) and MATCHH('1',Jc,'2',Kh))..
SIZE_TANK_2('1',Jc,Kh)=G=
(DOP('2')*3600*(Q('1',Jc,'2',Kh)/((CP('1','2')*RHO('1','2'))*(HOTS('1','2','TIN')-HOTS('1','2','TOUT')))));

*========================================================================================================================================================
*monotonic decrease of composition from k=1 to k=4
MONOT_RICH(I,P,K)$(RPS(I,P) AND ST(P,K) AND A_RPS(I,P,K)).. CR(I,P,K) =G= CR(I,P,K+1);
MONOT_LEAN(J,P,K)$(LPS(J,P) AND ST(P,K) AND A_LPS(J,P,K)).. CL(J,P,K) =G= CL(J,P,K+1);

*FEASIBLE(I,J,K)$AREX(I,J,K)..CR(I,K)-CL(J,K)=G=EMAC;
*===============================================================================

LOG_M_RPS_LPS(I,J,P,K)$(RPS(I,P) AND LPS(J,P) AND AREX(I,J,P,K))..M(I,J,P,K) =L= MIN(RICH(I,P,'F')*(RICH(I,P,'CIN')-RICH(I,P,'COUT')),L(J,P)*(LEAN(J,P,'COUT')-LEAN(J,P,'CIN')))*Y(I,J,K);
*===============================================================================
*Calculation of exchanger driving forces between rich and lean streams

LOG_DC_RPS_LPS_RS(I,J,P,K)$(RPS(I,P) AND LPS(J,P) AND AREX(I,J,P,K))..DC(I,J,P,K) =L= CR(I,P,K) - CL(J,P,K) + OMEGA(I,J,P)*(1-Y(I,J,K));
LOG_DC_RPS_LPS_RS1(I,J,P,K)$(RPS(I,P) AND LPS(J,P) AND AREX(I,J,P,K))..DC(I,J,P,K ) =G= CR(I,P,K) - CL(J,P,K) - OMEGA(I,J,P)*(1-Y(I,J,K));
LOG_DC_RPS_LPS_LS(I,J,P,K)$(RPS(I,P) AND LPS(J,P) AND AREX(I,J,P,K))..DC(I,J,P,K+1) =L= CR(I,P,K+1) - CL(J,P,K+1) + OMEGA(I,J,P)*(1-Y(I,J,K));
LOG_DC_RPS_LPS_LS1(I,J,P,K)$(RPS(I,P) AND LPS(J,P) AND AREX(I,J,P,K))..DC(I,J,P,K+1) =G= CR(I,P,K+1) - CL(J,P,K+1) - OMEGA(I,J,P)*(1-Y(I,J,K));

*=====================================================================================================================

*monotocity of temperature
MONOT_HOT(Ih,p,Kh)$(HPS(Ih,p) AND STh(p,kh) AND A_HPS(Ih,p,Kh)).. TH(Ih,p,Kh) =G= TH(Ih,p,Kh+1);
MONOT_COLD(Jc,p,Kh)$(CPS(Jc,p) AND STh(p,kh) AND A_CPS(Jc,p,Kh))..     TC(Jc,p,Kh) =G= TC(Jc,p,Kh+1);


LOG_Q_HPS_CPS(Ih,Jc,p,J,Kh)$(HPS(Ih,p) AND CPS(Jc,p) AND MATCHH (ih,jc,p,kh))..
Q(Ih,Jc,p,Kh) =L= MIN(HOTS(Ih,p,'F')*(HOTS(Ih,p,'TIN')-HOTS(Ih,p,'TOUT')),COLDS(Jc,p,'F')*(COLDS(Jc,p,'TOUT')-COLDS(Jc,p,'TIN')))*Yh(Ih,Jc,Kh);

LOG_Q_HPS_CUT(Ih,Jc,p,Kh)$(HPS(Ih,p) AND CUT(Jc,p) AND MATCHH (ih,jc,p,kh))..
Q(Ih,Jc,p,Kh) =L= HOTS(Ih,p,'F')*(HOTS(Ih,p,'TIN')-HOTS(Ih,p,'TOUT'))*Yh(Ih,Jc,Kh);

LOG_Q_HUT_CPS(Ih,Jc,p,Kh)$(HUT(Ih,p) AND CPS(Jc,p) AND MATCHH (ih,jc,p,kh))..
Q(Ih,Jc,p,Kh) =L=COLDS(Jc,p,'F')*(COLDS(Jc,p,'TOUT')-COLDS(Jc,p,'TIN'))*Yh(Ih,Jc,Kh);


LOG_DT_HPS_CPS_HS(Ih,Jc,p,Kh)$(HPS(Ih,p) AND CPS(Jc,p) AND MATCHH (ih,jc,p,kh))..DT(Ih,Jc,p,Kh) =L= TH(Ih,p,Kh) - TC(Jc,p,Kh) + GAMMA(Ih,Jc,p)*(1-Yh(Ih,Jc,Kh));
LOG_DT_HPS_CPS_CS(Ih,Jc,p,Kh)$(HPS(Ih,p) AND CPS(Jc,p) AND MATCHH (ih,jc,p,kh))..DT(Ih,Jc,p,Kh+1) =L= TH(Ih,p,Kh+1) - TC(Jc,p,Kh+1) + GAMMA(Ih,Jc,p)*(1-Yh(Ih,Jc,Kh));

LOG_DT_HPS_CUT_HS(Ih,Jc,p,Kh)$(HPS(Ih,p) AND CUT(Jc,p) AND MATCHH (ih,jc,p,kh))..DT(Ih,Jc,p,Kh)$(HPS(Ih,p) AND CUT(Jc,p) AND MATCHH (ih,jc,p,kh)) =L= (TH(Ih,p,Kh) - COLDS(Jc,p,'TOUT')) + GAMMA(Ih,Jc,p)*(1-Yh(Ih,Jc,Kh));
LOG_DT_HPS_CUT_CS(Ih,Jc,p,Kh)$(HPS(Ih,p) AND CUT(Jc,p) AND MATCHH (ih,jc,p,kh))..DT(Ih,Jc,p,Kh+1)$(HPS(Ih,p) AND CUT(Jc,p) AND MATCHH (ih,jc,p,kh)) =L= (TH(Ih,p,Kh+1) - COLDS(Jc,p,'TIN')) + GAMMA(Ih,Jc,p)*(1-Yh(Ih,Jc,Kh));

LOG_DT_HUT_CPS_HS(Ih,Jc,p,Kh)$(HUT(Ih,p) AND CPS(Jc,p) AND MATCHH (ih,jc,p,kh))..DT(Ih,Jc,p,Kh)$(HUT(Ih,p) AND CPS(Jc,p) AND MATCHH (ih,jc,p,kh)) =L= (HOTS(Ih,p,'TIN') - TC(Jc,p,Kh)) + GAMMA(Ih,Jc,p)*(1-Yh(Ih,Jc,Kh));
LOG_DT_HUT_CPS_CS(Ih,Jc,p,Kh)$(HUT(Ih,p) AND CPS(Jc,p) AND MATCHH (ih,jc,p,kh))..DT(Ih,Jc,p,Kh+1)$(HUT(Ih,p) AND CPS(Jc,p) AND MATCHH (ih,jc,p,kh)) =L=(HOTS(Ih,p,'TOUT') - TC(Jc,p,Kh+1)) + GAMMA(Ih,Jc,p)*(1-Yh(Ih,Jc,Kh));

*===============================================================================================================================================================

MX1(I,J,P,K)$(AREX(I,J,P,K))..
MX(I,J,K)=g=(M(I,J,P,K)*(1/KW)/((((1e-6)**3+
(DC(I,J,P,K)*DC(I,J,P,K+1))*((DC(I,J,P,K)+
DC(I,J,P,K+1))*0.5))**0.3333)+1E-6)+1E-6);

MXR1(R,P)..
MXR(R)=g=(V('1',P)*(ZEAN('1',P,'COUT')-ZEAN('1',P,'CIN'))*(1/KW)/((((1e-6)**3+
(((LEAN('3',P,'COUT')-ZEAN('1',P,'COUT'))*(LEAN('3',P,'CIN')-ZEAN('1',P,'CIN')))*((LEAN('3',P,'COUT')-ZEAN('1',P,'COUT'))
+(LEAN('3',P,'CIN')-ZEAN('1',P,'CIN')))*0.5))**0.3333)+1E-6)+1E-6) ;

AX1(ih,Jc,P,kh)$(MATCHH (ih,jc,p,kh))..
AX(ih,Jc,kh)=g=(Q(ih,Jc,P,kh)*(1/HOTS(ih,P,'H')+1/COLDS(Jc,P,'H'))/
(((1e-6)**3+((2/3)*(DT(Ih,Jc,P,Kh)*DT(Ih,Jc,P,Kh+1))**0.5)+(1/3*(DT(Ih,Jc,P,Kh)+
DT(Ih,Jc,P,Kh+1))*0.5))+1E-6)+1E-6);
*=================================================================================================================================================================
*$ONTEXT
Invest..
CAPINVEST =e=((AFM*(AF*(SUM((I,J,K),Y(I,J,K))+ACH*SUM((I,J,K),MX(I,J,K)**D))))+ (AF*(ACH*MXR('1'))**D)
+(AF2*((solarareacost*(SUM((IH,JC,kH),(AREA_SOLAR_1(IH,JC,KH)))))+(solarareacost*(SUM((IH,JC,kH),(AREA_SOLAR_2(IH,JC,KH)))))
+(storagetankcost*(SUM((IH,JC,kH),(SIZE_TANK_2(IH,JC,KH)))))))+AF*((CF*(SUM((Ih,Jc,Kh),Yh(Ih,Jc,Kh))))+(AChens*((SUM((Ih,Jc,kh),(AX(ih,Jc,kh))))))));

AOC..
Annualcost=E=SUM((P,J),(DOP(P)/NOP)*L(J,P)*AC(J))+SUM((P),(DOP(P)/NOP)*V('1',P)*AZ('1',P))
+SUM((P),(DOP(P)/NOP)* SUM((Ih,Jc,Kh),COLDS(Jc,p,'COST')*Q(Ih,Jc,p,Kh)))
+SUM((P),(DOP(P)/NOP)*SUM((Ih,Jc,Kh),HOTS(Ih,p,'COST')*Q(Ih,Jc,p,Kh)))
+W*(SUM((I,J,K),PNHC(I,J,K)+SNHC(I,J,K)));
*==========================================================================================================
*OBJECTIVE
*$ontext
OBJECTIVE..DUMMY=E= ((-CAPINVEST/((1+INTRATE)**0))+ ((OrigAOC-Annualcost)/((1+INTRATE)**1))
+((OrigAOC-Annualcost)/((1+INTRATE)**2))
+((OrigAOC-Annualcost)/((1+INTRATE)**3))+((OrigAOC-Annualcost)/((1+INTRATE)**4))+((OrigAOC-Annualcost)/((1+INTRATE)**5)));
*$OFFTEXT
*===========================================================================================================================================
$ontext
*OBJECTIVE

OBJECTIVE..
DUMMY =E=(AF*(SUM((I,J,K),Y(I,J,K))
+ACH*SUM((I,J,K),MX(I,J,K)**D)))
*Capital cost terms for AREXes involving lean stream 1 which requires tray columns

*Capital cost terms for AREXes involving lean stream 3 and regenerating stream which requires continuous contact columns
+ AF*(ACH*MXR('1'))**D

*tolerances to ensure that model converges
+W*(SUM((I,J,K),PNHC(I,J,K)+SNHC(I,J,K)))

+SUM((J,P),(DOP(P)/NOP)*L(J,P)*AC(J))

*Flowrate of regenerating stream multiplied by cost per unit of regenerating stream
+SUM((P),(DOP(P)/NOP)*V('1',P)*AZ('1',P))

*OBJECTIVEh..DUMMY=E=

+(AF2*((solarareacost*(SUM((IH,JC,kH),(AREA_SOLAR_1(IH,JC,KH)))))+
(solarareacost*(SUM((IH,JC,kH),(AREA_SOLAR_2(IH,JC,KH)))))
+(storagetankcost*(SUM((IH,JC,kH),(SIZE_TANK_2(IH,JC,KH)))))))

+         AF*((CF*(SUM((Ih,Jc,Kh),Yh(Ih,Jc,Kh))))+
         (AChens*((SUM((Ih,Jc,kh),(AX(ih,Jc,kh)))))))

        +SUM((P),(DOP(P)/NOP)* SUM((Ih,Jc,Kh),COLDS(Jc,p,'COST')*Q(Ih,Jc,p,Kh)))
        +SUM((P),(DOP(P)/NOP)*SUM((Ih,Jc,Kh),HOTS(Ih,p,'COST')*Q(Ih,Jc,p,Kh))) ;
$offtext
*===============================================================================
MODEL EXAMPLE1 /ALL/;
*===============================================================================
*INITIALISATIONS
*Initialisation for exchanger approach composition between RPS(I) AND LPS(J)
DC.L(I,J,P,K)$(RPS(I,P) AND LPS(J,P) AND AREX(I,J,P,K))=RICH(I,P,'CIN')-LEAN(J,P,'CIN') ;
DC.L(I,J,P,K+1)$(RPS(I,P) AND LPS(J,P) AND AREX(I,J,P,K))=RICH(I,P,'CIN')-LEAN(J,P,'CIN');
DC.LO(I,J,P,K)$(RPS(I,P) AND LPS(J,P) AND AREX(I,J,P,K))=EMAC;
DC.LO(I,J,P,K+1)$(RPS(I,P) AND LPS(J,P) AND AREX(I,J,P,K))=EMAC;
DC.UP(I,J,P,K)$(RPS(I,P) AND LPS(J,P) AND AREX(I,J,P,K))=1;
DC.UP(I,J,P,K+1)$(RPS(I,P) AND LPS(J,P) AND AREX(I,J,P,K))=1;

CAPINVEST.LO= .1;
CAPINVEST.L= .1;
CAPINVEST.UP= 100000;

Annualcost.LO= .1;
Annualcost.L= .1 ;
Annualcost.UP= 1000000;

L.L('1',P)=.1;  L.LO('1',P)=.1;  L.UP('1',P)=2.0;
L.L('2',P)=.1;  L.LO('2',P)=.1;  L.UP('2',P)=1.9;
L.L('3',P)=.1;  L.LO('3',P)=.01;  L.UP('3',P)=20;
V.L('1',P)=.1;  V.LO('1',P)=.1;  V.UP('1',P)=15.25;

*$ONTEXT
MX.L('1','1','3')= 3.2;
MX.LO('1','1','3')=3.2;
MX.UP('1','1','3')=3.2;

MX.L('2','3','2')= 31;
MX.LO('2','3','2')=31;
MX.UP('2','3','2')=31;

MX.L('3','1','3')= 304;
MX.LO('3','1','3')=304;
MX.UP('3','1','3')=304;

MX.L('4','2','1')= 41;
MX.LO('4','2','1')=41;
MX.UP('4','2','1')=41;

MX.L('5','3','3')= 19;
MX.LO('5','3','3')=19;
MX.UP('5','3','3')=19;
*$OFFTEXT


*m for regeneration kept constant

*Initialisations for M(I,J,K) between RPS(I) and LPS(J)
*$ONTEXT
M.L(I,J,P,K)$(RPS(I,P) AND AREX(I,J,P,K))=(RICH(I,P,'F')*(RICH(I,P,'CIN')-RICH(I,P,'COUT')));
M.L(I,J,P,K)$(RPS(I,P) AND AREX(I,J,P,K))=MIN(RICH(I,P,'F')*(RICH(I,P,'CIN')-RICH(I,P,'COUT')),L.L(J,P)*(LEAN(J,P,'COUT')-LEAN(J,P,'CIN')));

M.UP(I,J,P,K)$(RPS(I,P) AND LPS(J,P) AND AREX(I,J,P,K))=MIN(RICH(I,P,'F')*(RICH(I,P,'CIN')-RICH(I,P,'COUT')),L.L(J,P)*(LEAN(J,P,'COUT')-LEAN(J,P,'CIN')));
M.UP(I,J,P,K)$(RPS(I,P) AND AREX(I,J,P,K)) = RICH(I,P,'F')*(RICH(I,P,'CIN')-RICH(I,P,'COUT'));
*$offtext
*Intialisations and bounds for intermediate compositions
*$OFFTEXT

*$ONTEXT
CR.L(I,P,K)$(A_RPS(I,P,K))=RICH(I,P,'COUT');
CL.L(J,P,K)$(A_LPS(J,P,K) AND COMP_IN_LEAN(J,P,K))=LEAN(J,P,'CIN');

CR.LO(I,P,K)$(A_RPS(I,P,K) AND LAST(P,K))=RICH(I,P,'COUT');
CR.UP(I,P,K)$(A_RPS(I,P,K) AND COMP_IN_RICH(I,P,K))=RICH(I,P,'CIN');

CL.LO(J,P,K)$(A_LPS(J,P,K) AND COMP_IN_LEAN(J,P,K))=LEAN(J,P,'CIN');
CL.UP(J,P,K)$(A_LPS(J,P,K) AND COMP_OUT_LEAN(J,P,K))=LEAN(J,P,'COUT');

*$OFFTEXT
*===============================================================================
*Initialisation for exchanger approach temperatures between HPS(I) AND CPS(J)
EMAT=.0000001;
DT.L(Ih,Jc,P,Kh)$(HPS(Ih,P) AND CPS(Jc,P) AND MATCHH (ih,jc,p,kh))=HOTS(Ih,P,'TIN')-COLDS(Jc,P,'TIN') ;
DT.L(Ih,Jc,P,Kh+1)$(HPS(Ih,P) AND CPS(Jc,P) AND MATCHH (ih,jc,p,kh))=HOTS(Ih,P,'TIN')-COLDS(Jc,P,'TIN');
DT.LO(Ih,Jc,P,Kh)$(HPS(Ih,P) AND CPS(Jc,P) AND MATCHH (ih,jc,p,kh))=EMAT;
DT.LO(Ih,Jc,P,Kh+1)$(HPS(Ih,P) AND CPS(Jc,P) AND MATCHH (ih,jc,p,kh))=EMAT;
DT.UP(Ih,Jc,P,Kh)$(HPS(Ih,P) AND CPS(Jc,P) AND MATCHH (ih,jc,p,kh))=400;
DT.UP(Ih,Jc,P,Kh+1)$(HPS(Ih,P) AND CPS(Jc,P) AND MATCHH (ih,jc,p,kh))=400;

*Initialisation for exchanger approach temperatures between HPS(I) AND CUT(J)
DT.L(Ih,Jc,P,Kh)$(HPS(Ih,P) AND CUT(Jc,P) AND MATCHH (ih,jc,p,kh))=HOTS(Ih,P,'TIN')-COLDS(Jc,P,'TIN');
DT.L(Ih,Jc,P,Kh+1)$(HPS(Ih,P) AND CUT(Jc,P) AND MATCHH (ih,jc,p,kh))=HOTS(Ih,P,'TIN')-COLDS(Jc,P,'TIN');
DT.LO(Ih,Jc,P,Kh)$(HPS(Ih,P) AND CUT(Jc,P) AND MATCHH (ih,jc,p,kh))=EMAT;
DT.LO(Ih,Jc,P,Kh+1)$(HPS(Ih,P) AND CUT(Jc,P) AND MATCHH (ih,jc,p,kh))=EMAT;
DT.UP(Ih,Jc,P,Kh)$(HPS(Ih,P) AND CUT(Jc,P) AND MATCHH (ih,jc,p,kh))=400;
DT.UP(Ih,Jc,P,Kh+1)$(HPS(Ih,P) AND CUT(Jc,P) AND MATCHH (ih,jc,p,kh))=400;

*Initialisation for exchanger approach temperatures between HUT(I) AND CPS(J)
DT.L(Ih,Jc,P,Kh)$(HUT(Ih,P) AND CPS(Jc,P) AND MATCHH (ih,jc,p,kh))=HOTS(Ih,P,'TIN')-COLDS(Jc,P,'TIN');
DT.L(Ih,Jc,P,Kh+1)$(HUT(Ih,P) AND CPS(Jc,P) AND MATCHH (ih,jc,p,kh))=HOTS(Ih,P,'TIN')-COLDS(Jc,P,'TIN');
DT.LO(Ih,Jc,P,Kh)$(HUT(Ih,P) AND CPS(Jc,P) AND MATCHH (ih,jc,p,kh))=EMAT;
DT.LO(Ih,Jc,P,Kh+1)$(HUT(Ih,P) AND CPS(Jc,P) AND MATCHH (ih,jc,p,kh))=EMAT;
DT.UP(Ih,Jc,P,Kh)$(HUT(Ih,P) AND CPS(Jc,P) AND MATCHH (ih,jc,p,kh))=400;
DT.UP(Ih,Jc,P,Kh+1)$(HUT(Ih,P) AND CPS(Jc,P) AND MATCHH (ih,jc,p,kh))=400;
*$OFFTEXT



$ONTEXT
Initialisations for Q(I,J,K) between HPS(I) and CPS(J)
Q.L(Ih,Jc,P,Kh)$(HPS(Ih,P) AND CPS(Jc,P) AND MATCHH (ih,jc,p,kh))=MIN(L.L('3',P)*(HOTS(Ih,P,'TIN')-HOTS(Ih,P,'TOUT')),L.L('3',P)*(COLDS(Jc,P,'TOUT')-COLDS(Jc,P,'TIN')));
Q.L(Ih,Jc,P,Kh)$(HPS(Ih,P) AND CUT(Jc,P) AND MATCHH (ih,jc,p,kh)) = L.L('3',P)*(HOTS(Ih,P,'TIN')-HOTS(Ih,P,'TOUT'));
Q.L(Ih,Jc,P,Kh)$(HUT(Ih,P) AND CPS(Jc,P) AND MATCHH (ih,jc,p,kh))= L.L('3',P)*(COLDS(Jc,P,'TOUT')-COLDS(Jc,P,'TIN'));

Q.UP(Ih,Jc,P,Kh)$(HPS(Ih,P) AND CPS(Jc,P) AND MATCHH (ih,jc,p,kh))=MIN(L.L('3',P)*(HOTS(Ih,P,'TIN')-HOTS(Ih,P,'TOUT')),L.L('3',P)*(COLDS(Jc,P,'TOUT')-COLDS(Jc,P,'TIN')));
Q.UP(Ih,Jc,P,Kh)$(HPS(Ih,P) AND CUT(Jc,P) AND MATCHH (ih,jc,p,kh)) = L.L('3',P)*(HOTS(Ih,P,'TIN')-HOTS(Ih,P,'TOUT'));
Q.UP(Ih,Jc,P,Kh)$(HUT(Ih,P) AND CPS(Jc,P) AND MATCHH (ih,jc,p,kh))= L.L('3',P)*(COLDS(Jc,P,'TOUT')-COLDS(Jc,P,'TIN'));


Q.L(I,J,P,K)$(HPS(I,P) AND CPS(J,P) AND AREX(i,j,p,k))=MIN(HOTS(I,P,'F')*(HOTS(I,P,'TIN')-HOTS(I,P,'TOUT')),COLDS(J,P,'F')*(COLDS(J,P,'TOUT')-COLDS(J,P,'TIN')));
Q.L(I,J,P,K)$(HPS(I,P) AND CUT(J,P) AND AREX(i,j,p,k)) = HOTS(I,P,'F')*(HOTS(I,P,'TIN')-HOTS(I,P,'TOUT'));
Q.L(I,J,P,K)$(HUT(I,P) AND CPS(J,P) AND AREX(i,j,p,k))= COLDS(J,P,'F')*(COLDS(J,P,'TOUT')-COLDS(J,P,'TIN'));

Q.UP(I,J,P,K)$(HPS(I,P) AND CPS(J,P) AND AREX(i,j,p,k))=MIN(HOTS(I,P,'F')*(HOTS(I,P,'TIN')-HOTS(I,P,'TOUT')),COLDS(J,P,'F')*(COLDS(J,P,'TOUT')-COLDS(J,P,'TIN')));
Q.UP(I,J,P,K)$(HPS(I,P) AND CUT(J,P) AND AREX(i,j,p,k)) = HOTS(I,P,'F')*(HOTS(I,P,'TIN')-HOTS(I,P,'TOUT'));
Q.UP(I,J,P,K)$(HUT(I,P) AND CPS(J,P) AND AREX(i,j,p,k))= COLDS(J,P,'F')*(COLDS(J,P,'TOUT')-COLDS(J,P,'TIN'));
$offtext

*Intialisations and bounds for intermediate temperatures
TH.L(Ih,P,Kh)$(firsth(P,kh))=HOTS(Ih,P,'TIN');
TC.L(Jc,P,Kh)$(lasth(P,kh))=COLDS(Jc,P,'TIN');

TH.LO(Ih,P,Kh)$(lasth(P,kh))=HOTS(Ih,P,'TOUT');
TH.UP(Ih,P,Kh)$(firsth(P,kh))=HOTS(Ih,P,'TIN');

TC.LO(Jc,P,Kh)$(lasth(P,kh))=COLDS(Jc,P,'TIN');
TC.UP(Jc,P,Kh)$(firsth(P,kh))=COLDS(Jc,P,'TOUT');

*===============================================================================
EXAMPLE1.optfile=1;
OPTION DOMLIM =10000;
OPTION ITERLIM =200000;
SOLVE EXAMPLE1 USING MINLP MAXIMIZING DUMMY;
*SOLVE EXAMPLE1 USING MINLP MINIMIZING DUMMY;
*POSTPROCESSING



SCALAR
MASS_EXCHANGED
LEAN_UTILITIES
REGCOST
ACC
;
MASS_EXCHANGED = SUM((I,J,P,K)$(RPS(I,P) AND LPS(J,P)), M.L(I,J,P,K));

*Height of each mass exchange unit
HEIGHTMENS(I,J,P,K)=(M.L(I,J,P,K)*(1/KW)/((((1e-6)**3+
(DC.L(I,J,P,K)*DC.L(I,J,P,K+1))*((DC.L(I,J,P,K)+
DC.L(I,J,P,K+1))*0.5))**0.3333)+1E-6)+1E-6);

*Mass load stripped by regenerating stream from lean stream 3.
*Note that this mass load is equal to AVLEAN('3')
MASSREG(R,P)=V.L('1',P)*(ZEAN('1',P,'COUT')-ZEAN('1',P,'CIN'));

*Height of regenerating unit
HEIGHTREG('1',R,P) =((V.L('1',P)*(ZEAN('1',P,'COUT')-ZEAN('1',P,'CIN'))*(1/KW)/((((1e-6)**3+
(((LEAN('1',P,'COUT')-ZEAN(R,P,'COUT'))*(LEAN('1',P,'CIN')-ZEAN(R,P,'CIN')))*((LEAN('1',P,'COUT')-ZEAN(R,P,'COUT'))
+(LEAN('1',P,'CIN')-ZEAN(R,P,'CIN')))*0.5))**0.3333)+1E-6)+1E-6));

*Annual operating cost of regenerating stream
REGCOST=SUM((R,P),V.L('1',P)*AZ('1',P));

DISPLAY "RICH COMP:"
OPTION CL:7:1:1; DISPLAY CL.L;

DISPLAY "Annualcost:"
OPTION Annualcost:7; DISPLAY Annualcost.L;

DISPLAY "Capinvest:"
OPTION Capinvest:7; DISPLAY Capinvest.L;

*Annual capital cost which is a sum of annual cap cost of mass excahngers and regenerating unit
$ONTEXT
ACC= (AF*(SUM((I,J,P,K)$(AREX(I,J,P,K)),Y.L(I,J,K))
     +ACH*SUM((I,J,P,K)$(AREX(I,J,P,K)),(M.L(I,J,P,K)*(1/KW)/((((1e-6)**3+
     (DC.L(I,J,P,K)*DC.L(I,J,P,K+1))*((DC.L(I,J,P,K)+
      DC.L(I,J,P,K+1))*0.5))**0.3333)+1E-6)+1E-6)**D)))

+   AF*(ACH*((V.L('1',P)*(ZEAN('1',P,'COUT')-ZEAN('1',P,'CIN'))*(1/KW)/((((1e-6)**3+
   (((LEAN('3',P,'COUT')-ZEAN('1',P,'COUT'))*(LEAN('3',P,'CIN')-ZEAN('1',P,'CIN')))*((LEAN('3',P,'COUT')-ZEAN('1',P,'COUT'))
    +(LEAN('3',P,'CIN')-ZEAN('1',P,'CIN')))*0.5))**0.3333)+1E-6)+1E-6))**D )



*===============================================================================
*Display
DISPLAY "AREXES:"
DISPLAY Y.L;

DISPLAY "MASS:"
OPTION M:7:1:1; DISPLAY M.L;

DISPLAY "RICH COMP:"
OPTION CR:7:1:1; DISPLAY CR.L;

DISPLAY "LEAN COMP:"
OPTION CL:7:1:1; DISPLAY CL.L;

DISPLAY "TOTAL MASS EXCHANGED:"
DISPLAY MASS_EXCHANGED;

DISPLAY "TOTAL LEAN UTILITY CONSUMPTION:"

OPTION L:5; DISPLAY L.L;
DISPLAY V.L;

DISPLAY "HEIGHTMENS:"
DISPLAY HEIGHTMENS;

DISPLAY "HEIGHTREG:"
DISPLAY HEIGHTREG;

DISPLAY "MASSREG:"
DISPLAY MASSREG;

DISPLAY "REGCOST:"
DISPLAY REGCOST;

DISPLAY "ACC:"
DISPLAY ACC;
*===============================================================================
*                         - The End -



*$ONTEXT
SCALAR
HEAT_EXCHANGED
HOT_UTILITIES
COLD_UTILITIES
AOCCOST
AREA
Total;
HEAT_EXCHANGED= SUM((Ih,Jc,p,Kh)$(HPS(Ih,p) AND CPS(Jc,p)), Q.L(Ih,Jc,p,Kh));
HOT_UTILITIES = SUM((Ih,Jc,p,Kh)$(HUT(Ih,p) AND CPS(Jc,p)), Q.L(Ih,Jc,p,Kh));
COLD_UTILITIES = SUM((Ih,Jc,p,Kh)$(HPS(Ih,p) AND CUT(Jc,p)), Q.L(Ih,Jc,p,Kh));

AOCCOST=SUM((P),(DOP(P)/NOP)*SUM((ih,Jc,kh),Q.L(ih,Jc,P,kh)*HOTS(Ih,p,'COST')))+
SUM((P),(DOP(P)/NOP)*SUM((Ih,Jc,Kh),Q.L(Ih,Jc,P,Kh)*COLDS(Jc,p,'COST')));

AREA=SUM((Ih,Jc,Kh),(AF*(CF+AChens*(AX.L(Ih,Jc,Kh))**AE)));

Total = AOCCOST+AREA;



DISPLAY "AREXES:"
DISPLAY Yh.L;

DISPLAY "TOTAL HEAT EXCHANGED:"
DISPLAY HEAT_EXCHANGED ;

DISPLAY "TOTAL HOT UTILITY CONSUMPTION:"
DISPLAY HOT_UTILITIES;

DISPLAY "TOTAL HOT UTILITY CONSUMPTION:"
DISPLAY COLD_UTILITIES;

DISPLAY "Annual operating cost:"
DISPLAY AOCCOST;

DISPLAY "AREA"
DISPLAY AREA;

DISPLAY "Total"
DISPLAY Total;

$OFFTEXT
