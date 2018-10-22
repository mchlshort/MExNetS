scalar ICounter /2/;


SCALARS

NLUT number of lean utilities /2/
NRPS number of rich streams  /2/
ag        experimental constant /.123/
SETS
*===============================================================================
I rich streams  /1*2/
J lean streams and lean utilities /1*2/
K composition locations /1*4/
colpos number of collocation positions /1*30/
DATA   data    /CIN, COUT, F, COST, m/;

ALIAS
(J, JJjj);

*ALIAS
*(Jj, JJj);

*ALIAS
*(ii, iii);

option decimals=8;

*CHECK SCHMIDT NUMBER




*Need to confirm this as well
*===============================================================================
PARAMETERS
loverdee1,
RPS(I)      rich process streams
LPS(J)      lean process streams
*LUT(J)      lean utilities
ST(K)       stages
FIRST(K)    first composition location
LAST(K)     last composition location
first_tlrich(k)
SECLAST(K)  second last composition location
ms_st(k)    mass transfer stages
lut_st(k)   lean utility stages
CK(K)
AOC(JJjj);

RPS(I)            =YES$(ORD(I) <= NRPS);
LPS(J)            =YES$(ORD(J) <= NLUT);
*LUT(J)            =YES$(ORD(J) >=  NLUT-1);
ST(K)             =YES$(ORD(K) < CARD(K));
LAST(K)           =YES$(ORD(K) = CARD(K));
SECLAST(K)        =YES$(ORD(K) = card(k)-1);
first(k)          =yes$(ord(k) eq 1);
first_tlrich(k)   = yes$(ord(k)>=1 and ord(k) <card(k));
ms_st(k)          =yes$(ord(k)>=1 and ord(k)<card(k));
*lut_st(k)         =yes$(ord(k) = card(k)-1);


*===============================================================================
*Example 1 data
TABLE RICH(I,DATA) Rich streams data
       CIN          COUT          F
1     0.07         0.0003        0.90
2     0.051        0.0001        0.1;

TABLE LEAN(J,DATA) Lean streams data
       CIN          COUT           F
1     0.00087      0.04495       1.5862
2     0.000052     0.00091         0;

PARAMETER
*Capital cost parameters
arex2(i,j,k),
diainit(i,j,k),
FixCost     fixed cost for exchanger
AF          Annualisation factor
ACH         Annula cost per height of continuous contact column
D           Area cost exponent for mass exchangers
Kw          Lumped mass transfer coefficient
AC(J)          Annual operating cost per unit of lean stream
EMAC        Exchanger minimum approach composition
INT(K)      Interval in superstructure
R(I,K)      Rich stream existance coefficient
OMEGA(I,J)

RHOG(I,J)
RHOL(J)
SurfTen(j)  surface tension
surfarea(I)
packfact(I)
porosity(i)
de(i)
VIS(J)
VISRICH(I,J)
dia(i,j,k)   d
PACKCOST(i,j,k),
CLUTIN      Inlet concentration of external MSA
CLUTOUT     Outlet concentration of external MSA
W
H           Height of exchanger between streams I and J in interval K
*CORRECTION FACTORS DEFINED UNDER THESE PARAMETERS
diacor(i,j,k),
surfAcor(i,j,k),
KWCOR(i,j,k),
HCOR(i,j,k),
packcostcor(i,j,k),
*NLP init corrections
packfactcor(i,j,k),
PoroCor(i,j,k),
PartSizeCor(i,j,k),



Ap(i,j,k)   specific surface area of packing
*A Packing correction may be needed in order to account for cost of different
*PACKCORMAY(i,j,k)

;
*The UPDATED CORRECTION FACTORS
diacor(i,j,k)=1;

diacor('1','1','1')=1.05;
diacor('1','1','2')=1.05;
diacor('1','2','1')=1;
diacor('1','2','2')=1;
diacor('1','2','3')=1.05;

diacor('2','1','2')=1.05;
diacor('2','2','2')=1;
diacor('2','2','3')=0.95;

KWCOR(i,j,k)=1;

KWCOR('1','1','1')=0.98;
KWCOR('1','1','2')=0.98;
KWCOR('1','2','1')=1;
KWCOR('1','2','2')=1;
KWCOR('1','2','3')=0.95;

KWCOR('2','1','2')=0.95;
KWCOR('2','2','2')=1;
KWCOR('2','2','3')=0.95;

HCOR(i,j,k)=1;

HCOR('1','1','1')=0.95;
HCOR('1','1','2')=0.95;
HCOR('1','2','1')=1;
HCOR('1','2','2')=1;
HCOR('1','2','3')=0.95;

HCOR('2','1','2')=1.05;
HCOR('2','2','2')=1;
HCOR('2','2','3')=1.05;

SurfAcor(i,j,k)=1;

SurfAcor('1','1','1')=0.95;
SurfAcor('1','1','2')=0.95;
SurfAcor('1','2','1')=1;
SurfAcor('1','2','2')=1;
SurfAcor('1','2','3')=0.95;

SurfAcor('2','1','2')=0.95;
SurfAcor('2','2','2')=1;
SurfAcor('2','2','3')=0.9596;

packcostcor(i,j,k)=1;

packcostcor('1','1','1')=0.95;
packcostcor('1','1','2')=0.950119;
packcostcor('1','2','1')=1;
packcostcor('1','2','2')=1;
packcostcor('1','2','3')=1.02962;

packcostcor('2','1','2')=1.05;
packcostcor('2','2','2')=1;
packcostcor('2','2','3')=1.05;

packfactcor(i,j,k)=1;

packfactcor('1','1','1')=0.95;
packfactcor('1','1','2')=0.95;
packfactcor('1','2','1')=1;
packfactcor('1','2','2')=1;
packfactcor('1','2','3')=0.95;

packfactcor('2','1','2')=0.95;
packfactcor('2','2','2')=1;
packfactcor('2','2','3')=0.95;

PoroCor(i,j,k)=1;

PoroCor('1','1','1')=1.05;
PoroCor('1','1','2')=1.05;
PoroCor('1','2','1')=1;
PoroCor('1','2','2')=1;
PoroCor('1','2','3')=1.05;

PoroCor('2','1','2')=1.0147;
PoroCor('2','2','2')=1;
PoroCor('2','2','3')=0.994118;

PartSizeCor(i,j,k)=1;

PartSizeCor('1','1','1')=1.05;
PartSizeCor('1','1','2')=1.05;
PartSizeCor('1','2','1')=1;
PartSizeCor('1','2','2')=1;
PartSizeCor('1','2','3')=1.05;

PartSizeCor('2','1','2')=1;
PartSizeCor('2','2','2')=1;
PartSizeCor('2','2','3')=0.95;


Packcost(i,j,k)=1000;
dia(i,j,k)=0.35;

RHOG('1','1')= 1.14;
RHOG('1','2')= 1.50;
RHOG('2','1')= 1.14;
RHOG('2','2')= 1.50;

*For water at 20 therefore not aq ammonia
Surften('1')=72.80/1000;
*methanol at 20 therefore not right
Surften('2')=22.50/1000;

*a bit random for now THIS IS IN THE SUB FINAL NLP MODEL NB
Ap(i,j,k) = 300;

RHOL('1')= 900;
RHOL('2')= 842.5;

VISRICH(I,'1')=0.0000188648;
VISRICH(I,'2')=0.0000158723;
VIS('1')= 0.0011;
VIS('2')= 0.001258;

packfact(i)=2000;
surfarea(i)=300;
porosity(i)=.68;
*porosity('2')=.68;
de(i)=.02;
*de('2')= .0356;


ACH=618;  D=0.66;  AC('1')=117360;  AC('2')= 176040.4; AF=0.2; W=.000001; FixCost=30000;
EMAC=.000000001;  KW=0.05;
*===============================================================================
*===============================================================================
PARAMETER
*Used in Logical constraint for mass exchange in match (I,J,K)
OMEGAinit(I,J);
OMEGAinit(I,J)= 0.001;
*MAX(0,LEAN(J,'CIN')-RICH(I,'CIN'),LEAN(J,'CIN')-RICH(I,'COUT'),
*LEAN(J,'COUT')-RICH(I,'CIN'),LEAN(J,'COUT')-RICH(I,'COUT'));
*===============================================================================
INT(K)$(ORD(K)LT CARD(K))=1;
*===============================================================================

PARAMETER
AREX(I,J,K)
*CK(K)              INTERVAL COMPOSITION LOCATION
A_CKR_FIRST(I,K)   DEFINE FIRST INTERVAL OF ALL RICH PROCESS STREAMS (I)
A_CKL_FIRST(J,K)   DEFINE FIRST INTERVAL OF ALL LEAN PROCESS STREAMS(J)
A_CKR_LAST(I,K)
A_CKL_LAST(J,K)
A_CKL_LASTEXT(J,K)
A_I(I,K)           DEFINE INTERVALS IN WHICH RICH STREAMS EXIST(I)
A_RPS(I,K)         DEFINE INTERVALS IN WHICH RICH PROCESS STREAM RPS(I) EXIST
A_LPS(J,K)         DEFINE INTERVALS IN WHICH LEAN PROCESS STREAM LPS(J)EXIST
*A_LUT(I,J,K)       INTERVAS IN WHICH LEAN UTILITY LUT(J) IS PRESENT
MATCH(I,J,K)       DEFINE POSSIBLE MATCHES BETWEEN STREAMS I-J IN INTERVAL K
COMP_IN_RICH(I,K)
COMP_IN_LEAN(J,K)
COMP_OUT_RICH(I,K)
COMP_OUT_LEAN(J,K)
COMP_OUTEXT_LEAN(J,K);


*INITIALIZE FLAGS
A_CKR_FIRST(I,K)$ST(K)=0;
A_I(I,K)=0;
*A_RPS(I,K)=0;
*A_LPS(J,K)=0;
*A_LUT(I,J,K)=0;
MATCH(I,J,K)=0;
COMP_IN_RICH(I,K)=0;
COMP_IN_LEAN(J,K)=0;
COMP_OUT_RICH(I,K)=0;
COMP_OUT_LEAN(J,K)=0;
COMP_OUTEXT_LEAN(J,K)=0;


CK('1') = 0.07;
CK('2') = 0.051; CK('3') = 0.00087; CK('4') = 0.000052;
*===============================================================================
A_CKR_FIRST('1','1')$(RICH('1','CIN')) = CK('1');
A_CKR_FIRST('2','2')$(RICH('2','CIN')) = CK('2');

A_CKL_FIRST('1','3')$(LPS('1') AND (LEAN('1','CIN')))=CK('3');
A_CKL_FIRST('2','4')$(LPS('2') AND (LEAN('2','CIN')))=CK('4');

TABLE A_RPS(I,K)
    1   2   3
1   1   1   1
2   0   1   1 ;


TABLE A_LPS(J,K)
    1   2   3
1   1   1   0
2   1   1   1;

MATCH(I,J,K)$((A_RPS(I,K) AND A_LPS(J,K)))=1;
*===============================================================================
*First set of existance conditionals

MATCH(I,J,K)$((A_RPS(I,K) AND A_LPS(J,K)))=1;

COMP_IN_RICH(I,K)$RPS(I)= A_CKR_FIRST(I,K);
COMP_IN_LEAN(J,K)$LPS(J)=A_CKL_FIRST(J,K);

COMP_OUT_RICH(I,K)= LAST(K);
COMP_OUT_LEAN(J,K)= FIRST(K);

arex('1','1','1')=1;
arex('1','1','2')=1;
arex('1','2','1')=1;
arex('1','2','2')=1;
arex('1','2','3')=1;

arex('2','1','2')=1;
arex('2','2','2')=1;
arex('2','2','3')=1;







DISPLAY RPS, LPS, K, first, last, ms_st, ST, A_CKR_FIRST, A_CKL_FIRST, A_RPS, A_LPS, MATCH, COMP_IN_LEAN, COMP_IN_RICH, SECLAST;



*===============================================================================
VARIABLES
TACinit        TOTAL ANNUAL COST;
*===============================================================================
BINARY VARIABLE
Y1init(I,J,K);
*===============================================================================
POSITIVE VARIABLES
CRinit(I,K)            RICH STREAM COMPOSITION AT LOCATION K
CLinit(J,K)            LEAN STREAM COMPOSITION AT LOCATION K
CRINinit(I,J,K)
CLINinit(I,J,K)

AVLEANinit(J)
Minit(I,J,K)           MASS EXCHANGED
Linit(J)               FLOWRATE OF LEAN USED(J)ALL INCLUDED
FLRICHinit(I,J,K)
FLEANinit(I,J,K)

DCINinit(I,J,K)          COMPOSITION DIFERENCE BETWEEN PAIR OF STREAM (I.J) IN STAGE K
DCOUTinit(I,J,K)
*KAYFOURinit(I,J,K)
FLVinit(I,J,K)
*DIAinit(I,J,K)
HEIGHTinit(I,J,K)
SHELLinit(I,J,K)
PACKinit(I,J,K)
AREAinit(I,J,K)
KYinit(I,J,K)
KYAinit(I,J,K)
KYAREAinit(I,J,K)
TRUEHEIGHTinit(I,J,K)
PNHCinit(I,J,K)        POSITIVE TOLERANCE
SNHCinit(I,J,K)        NEGATIVE TOLERANCE
NHCinit(I,J,K)         RELAXED BINARY VARIABLE
Yinit(I,J,K);

*===============================================================================
EQUATIONS
CRICH_OUTinit(I,K)
CLEAN_OUTinit(J,K)
*CLEANEXT_OUT(J,K)
AVLEAN1init(J)
CRICH_INinit(I,K)             ASIGNMENT OF RICH PROCESS STREAM INLET COMPOSITION
CLEAN_INinit(J,K)             ASIGNMENT OF LEAN PROCESS STREAM INLET COMPOSITION
TOTAL_MASS_RICHinit(I)        TOTAL MASSS BALANCE OF RICH PROCESS STREAM RPS(I)
TOTAL_MASS_LEANinit(J)        TOTAL MASS BALANCE OF LEAN PROCESS STREAM LPS(I)
*TOTAL_MASS_LEAN1(J)
STAGE_MASS_RICHinit(I,K)      STAGE MASS BALANCE OF RICH PROCESS STREAM RPS(I)
STAGE_MASS_LEANinit(J,K)      STAGE MASS BALANCE OF LEAN PROCESS STREAM LPS(I)

MONOT_RICHinit(I,K)           MONOTONICITY ON CONCENTRATIONS - CONSTRAINT
MONOT_LEANinit(J,K)           MONOTONICITY ON CONCENTRATIONS - CONSTRAINT
MONOT_RICHSUBinit(I,J,K)
MONOT_LEANSUBinit(I,J,K)


Pinit(I,J,K)
Sinit(I,J,K)
N1init(I,J,K)

FLOWRICHinit(I,K)
FLOWLEANinit(J,K)

EXUNITRinit(i,j,k)
EXUNITLinit(i,j,k)


LOG_M_RPS_LPSinit(I,J,K)      LOGICAL CONSTRAINT ON MASS EXCHANGED BETWEEN RPS(I) AND LPS(J)


LOG_DC_RPS_LPS_RSinit(I,J,K)  LOGICAL CONSTRAINT ON RICH SIDE COMPOSITION DIFFERENCE BETWEEN RPS(I) AND LPS(J)
LOG_DC_RPS_LPS_RS1init(I,J,K)
LOG_DC_RPS_LPS_LSinit(I,J,K)  LOGICAL CONSTRAINT ON LEAN SIDE COMPOSITION DIFFERENCE BETWEEN RPS(I) AND LPS(J)
LOG_DC_RPS_LPS_LS1init(I,J,K)

FLOWLVinit(I,J,K)
*KFOUREQUinit(I,J,K)
*KYTRANSFERinit(I,J,K)
KYTRANSFERMASSinit(I,J,K)
*AREASinit(I,J,K)

*KYAREA1init(I,J,K)
*SHELLCOST(I,J,K)
*PACKING(I,J,K)
HEIGHTCOLUMNinit(I,J,K)
TRUEHEIGHTCOLUMNinit(I,J,K)


OBJECTIVEinit                 OBJECTIVE FUNCTION;

parameter CostOf1;
*MODEL EQUATIONS
*===============================================================================
*===============================================================================
*assignment of stream inlet compositions
CRICH_INinit(I,K)$(RPS(I) AND COMP_IN_RICH(I,K)).. CRinit(I,K) =E= RICH(I,'CIN');
CLEAN_INinit(J,K)$(LPS(J) AND COMP_IN_LEAN(J,K)).. CLinit(J,K) =E= LEAN(J,'CIN');


CRICH_OUTinit(I,K)$(RPS(I) AND COMP_OUT_RICH(I,K)).. CRinit(I,K) =E= RICH(I,'COUT');
CLEAN_OUTinit(J,K)$(LPS(J) AND COMP_OUT_LEAN(J,K)).. CLinit(J,K) =E= LEAN(J,'COUT');
*===============================================================================
Pinit(I,J,K)$(ST(K) AND A_RPS(I,K)) .. PNHCinit(I,J,K) =E=.0000001;
Sinit(I,J,K)$(ST(K) AND A_RPS(I,K)) .. SNHCinit(I,J,K) =E=.0000001;

N1init(I,J,K)$(INT(K) AND A_RPS(I,K))..Yinit(I,J,K) =E= Y1init(I,J,K)+(PNHCinit(I,J,K)-SNHCinit(I,J,K));
*=====================================================================================
*Available mass in lean stream J
AVLEAN1init(J)..AVLEANinit(J) =E= Linit(J)*(LEAN(J,'COUT')-LEAN(J,'CIN'));

*===============================================================================
*stream overall mass balance
TOTAL_MASS_RICHinit(I)$RPS(I) ..  RICH(I,'F')*(RICH(I,'CIN')-RICH(I,'COUT')) =E=
                              SUM((J,K)$(arex (I,J,K)), Minit(I,J,K));

TOTAL_MASS_LEANinit(J)$LPS(J).. Linit(J)*(LEAN(J,'COUT')-LEAN(J,'CIN')) =E=SUM((I,K)$(arex (I,J,K)),Minit(I,J,K));

*=================================================================================
*stream stage mass exchange
STAGE_MASS_RICHinit(I,K)$(RPS(I) AND SUM(J,arex (I,J,K)))..
RICH(I,'F')*(CRinit(I,K)-CRinit(I,K+1)) =E= SUM(J$arex (I,J,K), Minit(I,J,K));

STAGE_MASS_LEANinit(J,K)$(LPS(J) AND SUM(I,arex (I,J,K)))..
Linit(J)*(CLinit(J,K)-CLinit(J,K+1)) =E= SUM(I$arex (I,J,K), Minit(I,J,K));


FLOWRICHinit(I,K)$(RPS(I) AND SUM(J,arex (I,J,K)))..
RICH(I,'F')=E=SUM(J$arex (I,J,K),FLRICHinit(I,J,K));


FLOWLEANinit(J,K)$(LPS(J) AND SUM(I,arex (I,J,K)))..
Linit(J) =E= SUM(I$arex (I,J,K), FLEANinit(I,J,K));


EXUNITRinit(i,j,k)$(RPS(I) AND arex (I,J,K))..
FLRICHinit(I,J,K)*(CRinit(I,K)-CRINinit(I,J,K+1))=E=Minit(I,J,K);

EXUNITLinit(i,j,k)$(LPS(J) AND arex (I,J,K))..
FLEANinit(I,J,K)*(CLINinit(I,J,K)-CLinit(J,K+1))=E=Minit(I,J,K);
*===============================================================================
*monotonic decrease of composition from k=1 to k=5
MONOT_RICHinit(I,K)$(RPS(I) AND ST(K) AND A_RPS(I,K)).. CRinit(I,K) =G= CRinit(I,K+1);
MONOT_LEANinit(J,K)$(LPS(J) AND ST(K) AND A_LPS(J,K)).. CLinit(J,K) =G= CLinit(J,K+1);

MONOT_RICHSUBinit(I,J,K)$(RPS(I) AND ST(k) AND A_RPS(I,K)).. CRinit(I,K) =G= CRINinit(I,J,K+1);
MONOT_LEANSUBinit(I,J,K)$(LPS(J) AND ST(k) AND A_LPS(J,K)).. CLINinit(I,J,K) =G= CLinit(J,K+1);

*===============================================================================
*Logical constraint - Restrict ammount of mass exchanged in a arex  to lesser of the mass loads of R and L in the arex .

LOG_M_RPS_LPSinit(I,J,K)$(RPS(I) AND LPS(J) AND arex (I,J,K))..Minit(I,J,K) =L= MIN(RICH(I,'F')*(RICH(I,'CIN')-RICH(I,'COUT')),Linit(J)*(LEAN(J,'COUT')-LEAN(J,'CIN')))*Yinit(I,J,K);

*===============================================================================
*Calculation of exchanger driving forces

LOG_DC_RPS_LPS_RSinit(I,J,K)$(RPS(I) AND LPS(J) AND arex (I,J,K))..DCINinit(I,J,K) =L= CRinit(I,K) - CLINinit(I,J,K) + OMEGAinit(I,J)*(1-Yinit(I,J,K));
LOG_DC_RPS_LPS_RS1init(I,J,K)$(RPS(I) AND LPS(J) AND arex (I,J,K))..DCINinit(I,J,K ) =G= CRinit(I,K) - CLINinit(I,J,K) - OMEGAinit(I,J)*(1-Yinit(I,J,K));
LOG_DC_RPS_LPS_LSinit(I,J,K)$(RPS(I) AND LPS(J) AND arex (I,J,K))..DCOUTinit(I,J,K+1) =L= CRINinit(I,J,K+1) - CLinit(J,K+1) + OMEGAinit(I,J)*(1-Yinit(I,J,K));
LOG_DC_RPS_LPS_LS1init(I,J,K)$(RPS(I) AND LPS(J) AND arex (I,J,K))..DCOUTinit(I,J,K+1) =G= CRINinit(I,J,K+1) - CLinit(J,K+1) - OMEGAinit(I,J)*(1-Yinit(I,J,K));



*KFOUREQUinit(I,J,K)$arex(I,J,K)..
*KAYFOURinit(I,J,K)=E=(13.1*(((FLRICHinit(I,J,K)/(RHOG(I,J)*(AREAinit(I,J,K)))))**2)*(Packfact(I))*(((VIS(J))/(RHOL(J)))**0.1))/((RHOG(I,J))*(RHOL(J)-RHOG(I,J)));

FLOWLVinit(I,J,K)$arex(I,J,K)..
FLVinit(I,J,K)=E= ((FLEANinit(I,J,K))/(FLRICHinit(I,J,K)))*(((RHOG(I,J))/(RHOL(J)))**(0.5));


*AREASinit(I,J,K)$arex(I,J,K)..
*AREAinit(I,J,K)=E=(3.142*((DIAinit(I,J,K)**2)/4))*Yinit(I,J,K);

*KYTRANSFERinit(I,J,K)$arex(I,J,K)..
*KYinit(I,J,K)=E= (((FLRICHinit(I,J,K)/(RHOG(I,J)*(AREAinit(I,J,K))))/(porosity(i)))*(ag)*((((de(i))*(FLRICHinit(I,J,K)/(RHOG(I,J)*(AREAinit(I,J,K)))))/(porosity(i)*visrich(i,J)))**(-0.25))*(0.7**(-0.677))*(1))*Yinit(I,J,K);

KYTRANSFERMASSinit(I,J,K)$arex(I,J,K)..
KYAinit(I,J,K)=E=(kw*kwcor(i,j,k)*Surfarea(I)*surfAcor(i,j,k))*Yinit(I,J,K);

HEIGHTCOLUMNinit(I,J,K)$arex(I,J,K)..
HEIGHTinit(I,J,K)=E=(Minit(I,J,K)/(((KYAinit(I,J,K)*pi/4*((diacor(i,j,k)*DIA(I,J,K))**2)))*((((1e-6)**3+(DCINinit(I,J,K)*DCOUTinit(I,J,K+1))*((DCINinit(I,J,K)+DCOUTinit(I,J,K+1))*0.5))**0.3333)+1E-6)+1E-6))*Yinit(I,J,K);
** (tpi + tpo) / 2 - (tsi + tso) / 2         (2)

*TRUEHEIGHTCOLUMNinit(I,J,K)$arex(I,J,K)..
*TRUEHEIGHTinit(I,J,K)=E=(HEIGHTinit(I,J,K)*1.15);

*SHELLCOST(I,J,K)$( arex(I,J,K))..
*SHELL(I,J,K)=E= (23805*(DIA(I,J,K)**0.57)*TRUEHEIGHT(I,J,K))*Y1(I,J,K);

*PACKING(I,J,K)$(arex(I,J,K))..
*PACK(I,J,K)=E= 638*((DIA(I,J,K)**2)*HEIGHT(I,J,K))*Y1(I,J,K);

*===============================================================================
OBJECTIVEinit.. TACinit =E=
        FixCost*sum((i,j,k),yinit(i,j,k))+
        AF*(SUM((I,J,K)$(arex(I,J,K)),((23805*((diacor(i,j,k)*DIA(I,J,K))**0.57)*1.15*HCor(i,j,k)*HEIGHTinit(I,J,K))+pi/4*packcostcor(i,j,k)*packcost(i,j,k)*((((diacor(i,j,k)*DIA(I,J,K))**2)*HCor(i,j,k)*HEIGHTinit(I,J,K))))))
        +(SUM(J,Linit(J)*AC(J)))+W*(SUM((I,J,K),PNHCinit(I,J,K)+SNHCinit(I,J,K)));

*===============================================================================
MODEL EXAMPLE1init /CRICH_OUTinit,CLEAN_OUTinit,AVLEAN1init,CRICH_INinit,CLEAN_INinit,TOTAL_MASS_RICHinit,TOTAL_MASS_LEANinit,STAGE_MASS_RICHinit,
STAGE_MASS_LEANinit,MONOT_RICHinit,
MONOT_LEANinit,MONOT_RICHSUBinit,MONOT_LEANSUBinit,Pinit,Sinit,N1init,FLOWRICHinit,FLOWLEANinit,EXUNITRinit,EXUNITLinit,LOG_M_RPS_LPSinit,
LOG_DC_RPS_LPS_RSinit,
LOG_DC_RPS_LPS_RS1init,LOG_DC_RPS_LPS_LSinit,  LOG_DC_RPS_LPS_LS1init,FLOWLVinit,kytransfermassinit,HEIGHTCOLUMNinit,OBJECTIVEinit/;
*===============================================================================
VARIABLES
TAC        TOTAL ANNUAL COST;
*===============================================================================
BINARY VARIABLE
Y1(I,J,K);
*===============================================================================
POSITIVE VARIABLES
CR(I,K)            RICH STREAM COMPOSITION AT LOCATION K
CL(J,K)            LEAN STREAM COMPOSITION AT LOCATION K
CRIN(I,J,K)
CLIN(I,J,K)

AVLEAN(J)
M(I,J,K)           MASS EXCHANGED
L(J)               FLOWRATE OF LEAN USED(J)ALL INCLUDED
FLRICH(I,J,K)
FLEAN(I,J,K)

DCIN(I,J,K)          COMPOSITION DIFERENCE BETWEEN PAIR OF STREAM (I.J) IN STAGE K
DCOUT(I,J,K)
*KAYFOUR(I,J,K)
FLV(I,J,K)
*DIA(I,J,K)
HEIGHT(I,J,K)
SHELL(I,J,K)
PACK(I,J,K)
AREA(I,J,K)
KY(I,J,K)
KYA(I,J,K)
KYAREA(I,J,K)
TRUEHEIGHT(I,J,K)
PNHC(I,J,K)        POSITIVE TOLERANCE
SNHC(I,J,K)        NEGATIVE TOLERANCE
NHC(I,J,K)         RELAXED BINARY VARIABLE
Y(I,J,K);

*===============================================================================
EQUATIONS
CRICH_OUT(I,K)
CLEAN_OUT(J,K)
*CLEANEXT_OUT(J,K)
AVLEAN1(J)
CRICH_IN(I,K)             ASIGNMENT OF RICH PROCESS STREAM INLET COMPOSITION
CLEAN_IN(J,K)             ASIGNMENT OF LEAN PROCESS STREAM INLET COMPOSITION
TOTAL_MASS_RICH(I)        TOTAL MASSS BALANCE OF RICH PROCESS STREAM RPS(I)
TOTAL_MASS_LEAN(J)        TOTAL MASS BALANCE OF LEAN PROCESS STREAM LPS(I)
*TOTAL_MASS_LEAN1(J)
STAGE_MASS_RICH(I,K)      STAGE MASS BALANCE OF RICH PROCESS STREAM RPS(I)
STAGE_MASS_LEAN(J,K)      STAGE MASS BALANCE OF LEAN PROCESS STREAM LPS(I)

MONOT_RICH(I,K)           MONOTONICITY ON CONCENTRATIONS - CONSTRAINT
MONOT_LEAN(J,K)           MONOTONICITY ON CONCENTRATIONS - CONSTRAINT
MONOT_RICHSUB(I,J,K)
MONOT_LEANSUB(I,J,K)


P(I,J,K)
S(I,J,K)
N1(I,J,K)

FLOWRICH(I,K)
FLOWLEAN(J,K)

EXUNITR(i,j,k)
EXUNITL(i,j,k)


LOG_M_RPS_LPS(I,J,K)      LOGICAL CONSTRAINT ON MASS EXCHANGED BETWEEN RPS(I) AND LPS(J)


LOG_DC_RPS_LPS_RS(I,J,K)  LOGICAL CONSTRAINT ON RICH SIDE COMPOSITION DIFFERENCE BETWEEN RPS(I) AND LPS(J)
LOG_DC_RPS_LPS_RS1(I,J,K)
LOG_DC_RPS_LPS_LS(I,J,K)  LOGICAL CONSTRAINT ON LEAN SIDE COMPOSITION DIFFERENCE BETWEEN RPS(I) AND LPS(J)
LOG_DC_RPS_LPS_LS1(I,J,K)

FLOWLV(I,J,K)
*KFOUREQU(I,J,K)
*KYTRANSFER(I,J,K)
KYTRANSFERMASS(I,J,K)
*AREAS(I,J,K)

*KYAREA1(I,J,K)
*SHELLCOST(I,J,K)
*PACKING(I,J,K)
HEIGHTCOLUMN(I,J,K)
TRUEHEIGHTCOLUMN(I,J,K)


OBJECTIVE                 OBJECTIVE FUNCTION;
PARAMETER
*Used in Logical constraint for mass exchange in match (I,J,K)
OMEGA(I,J);
OMEGA(I,J)=0.0001;
*MAX(0,LEAN(J,'CIN')-RICH(I,'CIN'),LEAN(J,'CIN')-RICH(I,'COUT'),
*LEAN(J,'COUT')-RICH(I,'CIN'),LEAN(J,'COUT')-RICH(I,'COUT'));
*MODEL EQUATIONS
*===============================================================================
*===============================================================================
*assignment of stream inlet compositions
CRICH_IN(I,K)$(RPS(I) AND COMP_IN_RICH(I,K)).. CR(I,K) =E= RICH(I,'CIN');
CLEAN_IN(J,K)$(LPS(J) AND COMP_IN_LEAN(J,K)).. CL(J,K) =E= LEAN(J,'CIN');


CRICH_OUT(I,K)$(RPS(I) AND COMP_OUT_RICH(I,K)).. CR(I,K) =E= RICH(I,'COUT');
CLEAN_OUT(J,K)$(LPS(J) AND COMP_OUT_LEAN(J,K)).. CL(J,K) =E= LEAN(J,'COUT');
*===============================================================================
P(I,J,K)$(ST(K) AND A_RPS(I,K)) .. PNHC(I,J,K) =E=.0000001;
S(I,J,K)$(ST(K) AND A_RPS(I,K)) .. SNHC(I,J,K) =E=.0000001;

N1(I,J,K)$(INT(K) AND A_RPS(I,K))..Y(I,J,K) =E= Y1(I,J,K)+(PNHC(I,J,K)-SNHC(I,J,K));
*=====================================================================================
*Available mass in lean stream J
AVLEAN1(J)..AVLEAN(J) =E= L(J)*(LEAN(J,'COUT')-LEAN(J,'CIN'));

*===============================================================================
*stream overall mass balance
TOTAL_MASS_RICH(I)$RPS(I) ..  RICH(I,'F')*(RICH(I,'CIN')-RICH(I,'COUT')) =E=
                              SUM((J,K)$(arex2 (I,J,K)), M(I,J,K));
*
TOTAL_MASS_LEAN(J)$LPS(J).. L(J)*(LEAN(J,'COUT')-LEAN(J,'CIN')) =E=SUM((I,K)$(arex2 (I,J,K)),M(I,J,K));

*=================================================================================
*stream stage mass exchange
STAGE_MASS_RICH(I,K)$(RPS(I) AND SUM(J,arex2 (I,J,K)))..
RICH(I,'F')*(CR(I,K)-CR(I,K+1)) =E= SUM(J$arex2 (I,J,K), M(I,J,K));

STAGE_MASS_LEAN(J,K)$(LPS(J) AND SUM(I,arex2 (I,J,K)))..
L(J)*(CL(J,K)-CL(J,K+1)) =E= SUM(I$arex2 (I,J,K), M(I,J,K));


FLOWRICH(I,K)$(RPS(I) AND SUM(J,arex2 (I,J,K)))..
RICH(I,'F')=E=SUM(J$arex2 (I,J,K),FLRICH(I,J,K));


FLOWLEAN(J,K)$(LPS(J) AND SUM(I,arex2 (I,J,K)))..
L(J) =E= SUM(I$arex2 (I,J,K), FLEAN(I,J,K));


EXUNITR(i,j,k)$(RPS(I) AND arex2 (I,J,K))..
FLRICH(I,J,K)*(CR(I,K)-CRIN(I,J,K+1))=E=M(I,J,K);

EXUNITL(i,j,k)$(LPS(J) AND arex2 (I,J,K))..
FLEAN(I,J,K)*(CLIN(I,J,K)-CL(J,K+1))=E=M(I,J,K);
*===============================================================================
*monotonic decrease of composition from k=1 to k=5
MONOT_RICH(I,K)$(RPS(I) AND ST(K) AND A_RPS(I,K)).. CR(I,K) =G= CR(I,K+1);
MONOT_LEAN(J,K)$(LPS(J) AND ST(K) AND A_LPS(J,K)).. CL(J,K) =G= CL(J,K+1);

MONOT_RICHSUB(I,J,K)$(RPS(I) AND ST(k) AND A_RPS(I,K)).. CR(I,K) =G= CRIN(I,J,K+1);
MONOT_LEANSUB(I,J,K)$(LPS(J) AND ST(k) AND A_LPS(J,K)).. CLIN(I,J,K) =G= CL(J,K+1);

*===============================================================================
*Logical constraint - Restrict ammount of mass exchanged in a arex  to lesser of the mass loads of R and L in the arex .

LOG_M_RPS_LPS(I,J,K)$(RPS(I) AND LPS(J) and arex2(i,j,k))..M(I,J,K) =L= MIN(RICH(I,'F')*(RICH(I,'CIN')-RICH(I,'COUT')),L(J)*(LEAN(J,'COUT')-LEAN(J,'CIN')))*Y(I,J,K);

*===============================================================================
*Calculation of exchanger driving forces

LOG_DC_RPS_LPS_RS(I,J,K)$(RPS(I) AND LPS(J) AND arex2 (I,J,K))..DCIN(I,J,K) =L= CR(I,K) - CLIN(I,J,K) + OMEGA(I,J)*(1-Y(I,J,K));
LOG_DC_RPS_LPS_RS1(I,J,K)$(RPS(I) AND LPS(J) AND arex2 (I,J,K))..DCIN(I,J,K ) =G= CR(I,K) - CLIN(I,J,K) - OMEGA(I,J)*(1-Y(I,J,K));
LOG_DC_RPS_LPS_LS(I,J,K)$(RPS(I) AND LPS(J) AND arex2 (I,J,K))..DCOUT(I,J,K+1) =L= CRIN(I,J,K+1) - CL(J,K+1) + OMEGA(I,J)*(1-Y(I,J,K));
LOG_DC_RPS_LPS_LS1(I,J,K)$(RPS(I) AND LPS(J) AND arex2 (I,J,K))..DCOUT(I,J,K+1) =G= CRIN(I,J,K+1) - CL(J,K+1) - OMEGA(I,J)*(1-Y(I,J,K));



*KFOUREQU(I,J,K)$arex(I,J,K)..
*KAYFOUR(I,J,K)=E=(13.1*(((FLRICH(I,J,K)/(RHOG(I,J)*(AREA(I,J,K)))))**2)*(Packfact(I))*(((VIS(J))/(RHOL(J)))**0.1))/((RHOG(I,J))*(RHOL(J)-RHOG(I,J)));

FLOWLV(I,J,K)$arex2(I,J,K)..
FLV(I,J,K)=E= ((FLEAN(I,J,K))/(FLRICH(I,J,K)))*(((RHOG(I,J))/(RHOL(J)))**(0.5));


*AREAS(I,J,K)$arex(I,J,K)..
*AREA(I,J,K)=E=(3.142*((DIA(I,J,K)**2)/4))*Y(I,J,K);

*KYTRANSFER(I,J,K)$arex(I,J,K)..
*KY(I,J,K)=E= (((FLRICH(I,J,K)/(RHOG(I,J)*(AREA(I,J,K))))/(porosity(i)))*(ag)*((((de(i))*(FLRICH(I,J,K)/(RHOG(I,J)*(AREA(I,J,K)))))/(porosity(i)*visrich(i,J)))**(-0.25))*(0.7**(-0.677))*(1))*Y(I,J,K);

KYTRANSFERMASS(I,J,K)$arex2(I,J,K)..
KYA(I,J,K)=E=(kw*kwcor(i,j,k)*Surfarea(I)*surfAcor(i,j,k));

HEIGHTCOLUMN(I,J,K)$arex2(I,J,K)..
HEIGHT(I,J,K)=E=(M(I,J,K)/(((KYA(I,J,K)*pi/4*((diacor(i,j,k)*DIA(I,J,K))**2)))*((((1e-6)**3+(DCIN(I,J,K)*DCOUT(I,J,K+1))*((DCIN(I,J,K)+DCOUT(I,J,K+1))*0.5))**0.3333)+1E-6)+1E-6))*Y(I,J,K) ;
** (tpi + tpo) / 2 - (tsi + tso) / 2         (2)

*TRUEHEIGHTCOLUMNinit(I,J,K)$arex(I,J,K)..
*TRUEHEIGHTinit(I,J,K)=E=(HEIGHTinit(I,J,K)*1.15);

*SHELLCOST(I,J,K)$( arex(I,J,K))..
*SHELL(I,J,K)=E= (23805*(DIA(I,J,K)**0.57)*TRUEHEIGHT(I,J,K))*Y1(I,J,K);

*PACKING(I,J,K)$(arex(I,J,K))..
*PACK(I,J,K)=E= 638*((DIA(I,J,K)**2)*HEIGHT(I,J,K))*Y1(I,J,K);

*===============================================================================
OBJECTIVE.. TAC =E=
        FixCost*sum((i,j,k),y(i,j,k))+
        AF*(SUM((I,J,K)$(arex2(I,J,K)),((23805*((diacor(i,j,k)*DIA(I,J,K))**0.57)*1.15*HCor(i,j,k)*HEIGHT(I,J,K))+pi/4*packcostcor(i,j,k)*packcost(i,j,k)*((((diacor(i,j,k)*DIA(I,J,K))**2)*HCor(i,j,k)*HEIGHT(I,J,K))))))
        +(SUM(J,L(J)*AC(J)))+W*(SUM((I,J,K),PNHC(I,J,K)+SNHC(I,J,K)));
*===============================================================================
MODEL EXAMPLE1 /CRICH_OUT,CLEAN_OUT,AVLEAN1,CRICH_IN,CLEAN_IN,TOTAL_MASS_RICH,TOTAL_MASS_LEAN,STAGE_MASS_RICH,STAGE_MASS_LEAN,MONOT_RICH,
MONOT_LEAN,MONOT_RICHSUB,MONOT_LEANSUB,P,S,N1,FLOWRICH,FLOWLEAN,EXUNITR,EXUNITL,LOG_M_RPS_LPS,LOG_DC_RPS_LPS_RS,
LOG_DC_RPS_LPS_RS1,LOG_DC_RPS_LPS_LS,  LOG_DC_RPS_LPS_LS1,kytransfermass,HEIGHTCOLUMN,OBJECTIVE/;
*===============================================================================  FLOWLV,
Parameter Objheight(i,j,k),objDia(i,j,k),objpackcost(i,j,k),objai(i,j,k),objkw(i,j,k);


1111111111111111111111111111111111111111111111111111
 SCALAR
MASS_EXCHANGED
LEAN_UTILITIES
UNIT_HEIGHT
UNIT_HEIGHT1
;
parameter   FLRichlat(i,j,k),fleanlat(i,j,k);


Sets    ii     number of finite elements             /1*200/
        jj     number of internal collocation points /1*3/ ;
*        MEs    a set of mass exchangers from MINLP   /1*12/;

Alias (jj,kk);

*design based on MINLP solution
Parameter
cinitR(i,j,k),
cinitl(i,j,k),
cdesR(i,j,k),
cdesL(i,j,k),
flowrvlat(i,j,k),
flowlvlat(i,j,k),
flowrmlat(i,j,k),
flowlmlat(i,j,k),
EXIST(i,j,k),
slopecR(i,j,k,ii,jj),
slopecL(i,j,k,ii,jj);



$ontext
         cinitR  initial rich stream concentration in kmolSO2 per kmolAir      /0.010/
        cinitL  initial lean stream concentration in kmolSO2 per kmolH2O      /0.0003/
        cdesR   destination concentratin of Rich stream                       /0.0061/
        cdesL   destination concentration of lean stream                      /0.000457/
        FlowRv   flowrate of air in rich stream in m3.s-1                      /3.17/
        FlowLv   flowrate of water in lean stream in m3.s-1                    /7.499/
*       FlowRm   flowrate of air in rich stream in kmol per hour               /60/
*        FlowLm   flowrate of water in lean stream in kmol per hour             /1500/
        FlowRm   flowrate of air in rich stream in mol per s               /16.6667/
        FlowLm   flowrate of water in lean stream in mol per s             /416.66/
$offtext
scalar
* MTC fixed for now
*        kl       mass transfer coefficient for liquid side in m.s-1           /0.0019/
*        kg       gass mass trnsfer coefficient in m.s-1                       /0.0009567/
*        aI       interfacial area Raschig (guess sort of)  per m              /1.1/
*original wrong values
       kl       mass transfer coefficient for liquid side in m.s-1           /0.00019/
 aI       interfacial area Raschig (guess sort of)  per m              /0.019/
*        densR   density of air  1.225kg.m-3 28.97 g.mol-1                     //
*        densL   density of water
*fixing the diameter for right now


        nfe                                 /200/
        ncp                                 /3/
*        time                                /10/
*        LiqHold                                  /0.1/
*        LiQEddyDif                               /0.1/
*        GasHold                                  /0.1/
*        GasEddyDif                               /0.1/
        KOGb    constant for calculting koga     /1.28E-5/
*
*         KOGb   random messing kogb around     /5.55E-5/
        KOGm                                     /0.64/
        KOGn                                     /0.84/
*        Henry    henry's law constant in molSO2prmolwater /0.0234/
       Henry    henry's law constant in molSO2prmolwater /1/

        iii,
        jjj,
        point;


Table a(jj,jj) First order derivatives collocation matrix
                  1                    2                      3
     1     0.19681547722366      0.39442431473909     0.37640306270047
     2     -0.06553542585020     0.29207341166523     0.51248582618842
     3     0.02377097434822     -0.04154875212600     0.11111111111111;

Parameter
        cguessR(i,j,k,ii,jj)
        cguessL(i,j,k,ii,jj)
*        cguessRint(i,j)
*        cguessLint(i,j)
         diameter(i,j,k)
        cfinalR(i,j,k,ii)
        cfinalL(i,j,k,ii)
        cfinalRsub(i,j,k,ii)
        cfinalLsub(i,j,k,ii)
        velocityL(i,j,k)
        velocityR(i,j,k)
*        velocityLsub(i,j,k)
*        velocityRsub(i,j,k)

             ;

*
* Initial guess of the decision variables
*




Variables cRs(i,j,k,ii,jj)  concentration of Rich stream along column
          cLs(i,j,k,ii,jj)  concentration of lean stream along column
          cr0(i,j,k,ii)
           cl0(i,j,k,ii)
           h0(i,j,k,ii)

          cdotR(i,j,k,ii,jj)
          cdotL(i,j,k,ii,jj)
          flux(i,j,k,ii,jj)      molar flux along column
          hs(i,j,k,ii,jj)
          Heights(i,j,k)
*          Diameter
*          KOGa
          CapCosts       objective function ;

 Equations  fobj         criterion definition
            ICL,
            ICR,
            itt,
*            ICRi,
            FCr,
            FCl,
*            ELMASSBAL    Mass balance over element
*            MBALOverall,
*            MTCEq,
*           TRateLiq,
           TRateVap,
*           ELMBal,elmbal2,
*           overallmbal,
*            EquilibEq,
*            RelHandHeq,
            FECOLcR,
        fecolch,
*            FECOLcRint(i,j) ,
            FECOLcL ,
*            FECOLcLint(i,j) ,
            CONcR,
            CONcL,
           CONtt,
            ODEcR,
            ODEcL;
*,
*fcl

* Objective Function
fobj.. CapCosts =e= 1;

TRateVap(i,j,k,ii,jj)$(exist(i,j,k))..  flux(i,j,k,ii,jj)=e=-kw*kwcor(i,j,k)*surfarea(i)*surfacor(i,j,k)*pi/4*((diameter(i,j,k)**2))*(cRs(i,j,k,ii,jj)-henry*cls(i,j,k,ii,jj)) ;


FECOLcR(i,j,k,ii,jj)$(ord(ii) le nfe and exist(i,j,k)).. crs(i,j,k,ii,jj)=e=cr0(i,j,k,ii)+ heights(i,j,k)*1/nfe*sum(kk,a(kk,jj)*cdotR(i,j,k,ii,jj))  ;
*FECOLcRint(i,j)$(ord(j) ge 1).. h(i)*cdotRint(i,j)=e=sum(k,adot(k,j)*cRint(i,k))  ;

FECOLcL(i,j,k,ii,jj)$(ord(ii) le nfe and exist(i,j,k)).. cls(i,j,k,ii,jj)=e=cl0(i,j,k,ii)+ heights(i,j,k)*1/nfe*sum(kk,a(kk,jj)*cdotl(i,j,k,ii,kk))  ;
*FECOLcLint(i,j)$(ord(j) ge 1)..  h(i)*cdotLint(i,j)=e=sum(k,adot(k,j)*cLint(i,k))  ;
FECOLcH(i,j,k,ii,jj)$(ord(ii) le nfe and exist(i,j,k)).. hs(i,j,k,ii,jj) =e= h0(i,j,k,ii) + heights(i,j,k)*1/nfe*sum(kk, a(kk,jj));

*continuity eqs

CONcR(i,j,k,ii)$(ord(ii) gt 1 and ord(ii) le nfe and exist(i,j,k))..
cr0(i,j,k,ii) =e= cr0(i,j,k,ii-1)+heights(i,j,k)*1/nfe*sum(jj, cdotR(i,j,k,ii-1,jj)*a(jj,'3'));

*
CONcL(i,j,k,ii)$(ord(ii) gt 1 and ord(ii) le nfe  and exist(i,j,k))..
cL0(i,j,k,ii) =e= cl0(i,j,k,ii-1)+heights(i,j,k)*1/nfe*sum(jj, cdotl(i,j,k,ii-1,jj)*a(jj,'3'));


CONtt(i,j,k,ii)$(ord(ii) gt 1 and ord(ii) le nfe)..
h0(i,j,k,ii) =e= h0(i,j,k,ii-1) + heights(i,j,k)*1/nfe*sum(jj, a(jj,'3'));



*Differenital Eqs
ODEcR(i,j,k,ii,jj)$(exist(i,j,k) and ord(ii) le nfe).. cdotR(i,j,k,ii,jj)=e=flux(i,j,k,ii,jj)/FlowRmlat(i,j,k);
ODECL(i,j,k,ii,jj)$(exist(i,j,k) and ord(ii) le nfe).. cdotL(i,j,k,ii,jj)=e=flux(i,j,k,ii,jj)/FlowLmlat(i,j,k);

*Initial conditions
ICR(i,j,k)$(exist(i,j,k)).. cR0(i,j,k,'1') =e= cinitR(i,j,k);
ICL(i,j,k)$(exist(i,j,k)).. cL0(i,j,k,'1') =e= cdesL(i,j,k);
itt(i,j,k).. h0(i,j,k,'1')=e=0;
*ICRi.. cRint('1','1') =e= cinitR;
FCR(i,j,k)$(exist(i,j,k)).. cRs(i,j,k,'200','3') =e= cdesR(i,j,k);
FCL(i,j,k)$(exist(i,j,k)).. cLs(i,j,k,'200','3') =e= cinitL(i,j,k);

Model Packedbed /icr, fcl,fcr,itt,contt,odecr,odecl,concl,concr,fecolcr,fecolcl,fecolch,tratevap,fobj/;

*  elmbal, elmbal2,    fecolch,  icl,      fcl, relhandheq,

parameter loverdee(i,j,k),kogap(i,j,k),kogasl(i,j,k),kogas(i,j,k),leanma(i,j,k),richma(i,j,k),leanmasub(i,j,k),richmasub(i,j,k),leanmadeet(i,j,k),richmadeet(i,j,k),
         richmafinal(i,j,k),leanmafinal(i,j,k),richmapack(i,j,k),leanmapack(i,j,k),richmapack2(i,j,k),leanmapack2(i,j,k),elementbalR(i,j,k,ii),elementbalL(i,j,k,ii);





*================================================================
*=============MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM===========
*================================================================
*================================================================
*                 RUN FOR MORE WITH CAP COSTS and
*          TO INCLUDE K AND DIAMETERS AS VARIABLES
*                        VAR NAMES: "SUB"222222222222222222222222222222222222222222222222222222222222
*================================================================
*================================================================
*=============MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM===========
*================================================================
*================================================================
*                 INITIALISING WITH PREVIOUS RUN
*================================================================

Variables cRsub(i,j,k,ii,jj)  concentration of Rich stream along column
          cLsub(i,j,k,ii,jj)  concentration of lean stream along column
          cdotRsub(i,j,k,ii,jj)
          cdotLsub(i,j,k,ii,jj)
          fluxsub(i,j,k,ii,jj)      molar flux along column
          cr0sub(i,j,k,ii)
          cl0sub(i,j,k,ii)
          h0sub(i,j,k,ii)
          hsub(i,j,k,ii,jj)
          Heightsub(i,j,k)
          diametersub(i,j,k),
          Areasub(i,j,k)
          VelocityRsub(i,j,k),
          VelocityLsub(i,j,k),
          KOGa(i,j,k)
          CapCostsub      objective function ;

*================================================================
*        New run that includes diameters and k as variables
*================================================================

 Equations  fobjsub         criterion definition
            ICLsub,
            ICRsub,fcrsub,ittsub,fclsub,
            TRateVapsub,
            AreaEQ,
            kogaEq,
            VelocityREQ,
            VelocityLEq,
           LoverDup,
            loverdlo,
            RelHandHeqsub,
            FECOLcRsub,
*            FECOLcRint(ii,jj) ,
            FECOLcLsub ,
         fecolchsub,
*            FECOLcLint(ii,jj) ,
            CONcRsub,
            CONcLsub,
            CONttsub,
            ODEcRsub,
            ODEcLsub;

* Objective Function
fobjsub.. CapCostsub =e=
         FixCost*sum((i,j,k),exist(i,j,k))+
         AF*(SUM((I,J,K),((23805*(Diametersub(i,j,k)**0.57)*1.15*heightsub(i,j,k)))))
         +AF*(sum((i,j,k),pi*(diaMETERSUB(i,j,k)**2)/4*HEIGHTsub(i,j,k)*Packcost(i,j,k)))
         + (SUM(J,L.l(J)*AC(J)));



TRateVapsub(i,j,k,ii,jj)$(exist(i,j,k))..  fluxsub(i,j,k,ii,jj)=e=-koga(i,j,k)*areasub(i,j,k)*surfarea(i)*surfacor(i,j,k)*(cRsub(i,j,k,ii,jj)-henry*clsub(i,j,k,ii,jj)) ;

*collocation Eqs

FECOLcRsub(i,j,k,ii,jj)$(ord(ii) le nfe and exist(i,j,k)).. crsub(i,j,k,ii,jj)=e=cr0sub(i,j,k,ii)+heightsub(i,j,k)*1/nfe*sum(kk,a(kk,jj)*cdotRsub(i,j,k,ii,jj))  ;

FECOLcLsub(i,j,k,ii,jj)$(ord(ii) le nfe and exist(i,j,k)).. clsub(i,j,k,ii,jj)=e=cl0sub(i,j,k,ii)+ heightsub(i,j,k)*1/nfe*sum(kk,a(kk,jj)*cdotlsub(i,j,k,ii,kk))  ;
*FECOLcLint(i,j)$(ord(j) ge 1)..  h(i)*cdotLint(i,j)=e=sum(k,adot(k,j)*cLint(i,k))  ;

*FECOLtt(i,j)$(ord(i) le nfe).. tt(i,j) =e= tt0(i)
*+height*h(i)*sum(k,a(k,j)) ;
FECOLcHsub(i,j,k,ii,jj)$(ord(ii) le nfe and exist(i,j,k)).. hsub(i,j,k,ii,jj) =e= h0sub(i,j,k,ii) + heightsub(i,j,k)*1/nfe*sum(kk, a(kk,jj));

*continuity eqs

CONcRsub(i,j,k,ii)$(ord(ii) gt 1 and ord(i) le nfe and exist(i,j,k))..
cr0sub(i,j,k,ii) =e= cr0sub(i,j,k,ii-1)+heightsub(i,j,k)*1/nfe*sum(jj, cdotRsub(i,j,k,ii-1,jj)*a(jj,'3'));

CONcLsub(i,j,k,ii)$(ord(ii) gt 1 and exist(i,j,k))..
cL0sub(i,j,k,ii) =e= cl0sub(i,j,k,ii-1)+heightsub(i,j,k)*1/nfe*sum(jj, cdotlsub(i,j,k,ii-1,jj)*a(jj,'3'));

CONttsub(i,j,k,ii)$(ord(ii) gt 1 and ord(ii) le nfe and exist(i,j,k))..
h0sub(i,j,k,ii) =e= h0sub(i,j,k,ii-1) + heightsub(i,j,k)*1/nfe*sum(jj, a(jj,'3'));

kogaEq(i,j,k)$(exist(i,j,k))..   KOGa(i,j,k) =e= (VelocityRsub(i,j,k))/(porosity(i)*PoroCor(i,j,k))*ag*(((de(i)*PartSizeCor(i,j,k)*(VelocityRsub(i,j,k)))/(porosity(i)*PoroCor(i,j,k)*visrich(i,J)))**(-0.25))*(0.7**(-0.677))*(1);



VelocityREQ(i,j,k)$(exist(i,j,k))..VelocityRsub(i,j,k)*Areasub(i,j,k)=e= flowrvlat(i,j,k);
VelocityLEq(i,j,k)$(exist(i,j,k))..VelocityLsub(i,j,k)*Areasub(i,j,k)=e= flowlvlat(i,j,k);
*kogaEq..KOGa =e= KOGb*((FlowRv/((3.14/4)*sqr(diametersub)))**KOGm)*((FlowLv/((3.14/4)*sqr(diametersub)))**KOGn);
*continuity eqs

AreaEQ(i,j,k)$(exist(i,j,k)).. areasub(i,j,k)=e=pi/4*(diametersub(i,j,k)**2);
*Differenital Eqs
ODEcRsub(i,j,k,ii,jj)$(exist(i,j,k)).. FlowRmlat(i,j,k)*cdotRsub(i,j,k,ii,jj)=e=fluxsub(i,j,k,ii,jj);
ODECLsub(i,j,k,ii,jj)$(exist(i,j,k)).. FlowLmlat(i,j,k)*cdotLsub(i,j,k,ii,jj)=e=fluxsub(i,j,k,ii,jj);

loverdup(i,j,k)$(exist(i,j,k))..heightsub(i,j,k) =l= 2000*diametersub(i,j,k);
loverdlo(i,j,k)$(exist(i,j,k))..heightsub(i,j,k) =g= 0.1*diametersub(i,j,k);

*Initial conditions
ICRsub(i,j,k)$(exist(i,j,k)).. cR0sub(i,j,k,'1') =e= cinitR(i,j,k);
ICLsub(i,j,k)$(exist(i,j,k)).. cL0sub(i,j,k,'1') =e= cdesL(i,j,k);
ittsub(i,j,k)$(exist(i,j,k)).. h0sub(i,j,k,'1')=e=0;
FCRsub(i,j,k)$(exist(i,j,k)).. cRsub(i,j,k,'200','3') =e= cdesR(i,j,k);
FCLsub(i,j,k)$(exist(i,j,k)).. cLsub(i,j,k,'200','3') =e= cinitL(i,j,k);

*Attempt at getting height to relate to element length
RelHandHeqsub(i,j,k,ii,jj)$(exist(i,j,k)).. hsub(i,j,k,ii,jj) =e= 1/nfe*heightsub(i,j,k) ;

*TTT.. time =e= transtime ;
*heightsub.up(i,j,k) = 5000*diametersub.l(i,j,k);
Model Packedbedsub /fecolchsub,ICRsub,ittsub,conttsub, fclsub,FCrsub,areaEQ,loverdup,loverdlo,VelocityREQ,VelocityLEQ,ODEcRsub,ODECLsub,CONcRsub,CONcLsub,FECOLcLsub,FECOLcRsub,TRateVapsub,fobjsub,kogaeq  /;

* h.l(i)=1;                fcrsub               fclsub,   RelHandHeqsub,,

* scalar
*RHOG   /1.14/
*RHOL /1000/
*VISRICH /0.0000188648/
*VIS /0.0011/
*Packfact /120/;
* surfarea /128/
* porosity /74/
*de /.0673/;

parameter CP(i,j,k),ReL(i,j,k),ReG(i,j,k),NewP(i,j,k),FLVlat(i,j,k), kayfourlat(i,j,k),flowlvlat(i,j,k), FPdrop(i,j,k) ,ActPdrop(i,j,k), HughesFP(i,j,k) ,HughesPD(i,j,k),capcostinit;

*=============WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW===================
*=============MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM===================
*========================================================================
*========================================================================
*                 RUN FOR MORE THERMOS AND PRESSURES
*                        VAR NAMES: "DEET"3333333333333333333333333333333333333333333333333333333333333333333333333333333333333
*========================================================================
*=============WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW===================
*=============MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM===================
*========================================================================
*                 INITIALISING WITH PREVIOUS RUN
*========================================================================

Variables cRdeet(i,j,k,ii,jj)  concentration of Rich stream along column
          cLdeet(i,j,k,ii,jj)  concentration of lean stream along column
          cdotRdeet(i,j,k,ii,jj)
          cdotLdeet(i,j,k,ii,jj)
          fluxdeet(i,j,k,ii,jj)      molar flux along column
          cr0deet(i,j,k,ii)
          cl0deet(i,j,k,ii)
          hdeet(i,j,k,ii,jj)
          h0deet(i,j,k,ii),
          packfactdeetvar(i,j,k),
          hv(i,j,k,ii)
          Heightdeet(i,j,k)
          diameterdeet(i,j,k),
          Areadeet(i,j,k)
          VelocityRdeet(i,j,k),
          VelocityLdeet(i,j,k),
          KOGadeet(i,j,k),
          HughesAct(i,j,k),
          HughesFlood(i,j,k),
         Reldeet(i,j,k),
         ReGdeet(i,j,k),
          CapCostdeet      objective function ;

*=====================================================================
*        New run that includes pressure drop constraint and L over D
*======================================================================

 Equations  fobjdeet         criterion definition
            ICLdeet,
            ICRdeet,fcrdeet,ittdeet, fcldeet,
           TRateVapdeet,
           AreaEQdeet,
           kogaEqdeet,
           VelocityREQdeet,
           VelocityLEqdeet,
          LoverDupdeet,
          loverdlodeet,
            RelHandHeqdeet,
            FECOLcRdeet,
         fecolchdeet,
*            FECOLcRint(ii,jj) ,
            FECOLcLdeet ,
*            FECOLcLint(ii,jj) ,
            CONcRdeet,
            CONcLdeet,
            CONttdeet,
            ODEcRdeet,
            ODEcLdeet,
            HughesPDdeet1,
            HughesPDdeet2,
            HughesPDdeet3,
         ReynoldsGdeet,
         ReynoldsLdeet
            ;

* Objective Function
fobjdeet.. CapCostdeet =e= FixCost*sum((i,j,k),exist(i,j,k))+
         AF*(SUM((I,J,K),((23805*(Diameterdeet(i,j,k)**0.57)*1.15*heightdeet(i,j,k)*exist(i,j,k)))))
         +AF*(sum((i,j,k),pi*(diaMETERdeet(i,j,k)**2)/4*HEIGHTdeet(i,j,k)*Packcost(i,j,k)*exist(i,j,k)))
         +(SUM(J,L.l(J)*AC(J)));




TRateVapdeet(i,j,k,ii,jj)$(exist(i,j,k))..  fluxdeet(i,j,k,ii,jj)=e=-kogadeet(i,j,k)*areadeet(i,j,k)*surfarea(i)*surfacor(i,j,k)*(cRdeet(i,j,k,ii,jj)-henry*cldeet(i,j,k,ii,jj)) ;

*collocation Eqs

FECOLcRdeet(i,j,k,ii,jj)$(ord(ii) le nfe and exist(i,j,k)).. crdeet(i,j,k,ii,jj)=e=cr0deet(i,j,k,ii)+ 1/nfe*heightdeet(i,j,k)*sum(kk,a(kk,jj)*cdotRdeet(i,j,k,ii,jj))  ;

FECOLcLdeet(i,j,k,ii,jj)$(ord(ii) le nfe and exist(i,j,k)).. cldeet(i,j,k,ii,jj)=e=cl0deet(i,j,k,ii)+ 1/nfe*heightdeet(i,j,k)*sum(kk,a(kk,jj)*cdotldeet(i,j,k,ii,kk))  ;
*FECOLcLint(i,j)$(ord(j) ge 1)..  h(i)*cdotLint(i,j)=e=sum(k,adot(k,j)*cLint(i,k))  ;
FECOLcHdeet(i,j,k,ii,jj)$(ord(ii) le nfe and exist(i,j,k)).. hdeet(i,j,k,ii,jj) =e= h0deet(i,j,k,ii) + heightdeet(i,j,k)*1/nfe*sum(kk, a(kk,jj));
*FECOLtt(i,j)$(ord(i) le nfe).. tt(i,j) =e= tt0(i)
*+height*h(i)*sum(k,a(k,j)) ;

*continuity eqs

CONcRdeet(i,j,k,ii)$(ord(ii) gt 1 and ord(i) le nfe and exist(i,j,k))..
cr0deet(i,j,k,ii) =e= cr0deet(i,j,k,ii-1)+1/nfe*heightdeet(i,j,k)*sum(jj, cdotRdeet(i,j,k,ii-1,jj)*a(jj,'3'));

CONcLdeet(i,j,k,ii)$(ord(ii) gt 1 and exist(i,j,k))..
cL0deet(i,j,k,ii) =e= cl0deet(i,j,k,ii-1)+1/nfe*heightdeet(i,j,k)*sum(jj, cdotldeet(i,j,k,ii-1,jj)*a(jj,'3'));

CONttdeet(i,j,k,ii)$(ord(ii) gt 1 and ord(ii) le nfe and exist(i,j,k))..
h0deet(i,j,k,ii) =e= h0deet(i,j,k,ii-1) + 1/nfe*heightdeet(i,j,k)*sum(jj, a(jj,'3'));

kogaEqdeet(i,j,k)$(exist(i,j,k))..   KOGadeet(i,j,k) =e= (VelocityRdeet(i,j,k))/(porosity(i)*PoroCor(i,j,k))*ag*((((de(i)*partsizecor(i,j,k))*(VelocityRdeet(i,j,k)))/(porosity(i)*PoroCor(i,j,k)*visrich(i,J)))**(-0.25))*(0.7**(-0.677))*(1);


VelocityREQdeet(i,j,k)$(exist(i,j,k))..VelocityRdeet(i,j,k)*Areadeet(i,j,k)=e= flowrvlat(i,j,k);
VelocityLEqdeet(i,j,k)$(exist(i,j,k))..VelocityLdeet(i,j,k)*Areadeet(i,j,k)=e= flowlvlat(i,j,k);
*kogaEq..KOGa =e= KOGb*((FlowRv/((3.14/4)*sqr(diametersub)))**KOGm)*((FlowLv/((3.14/4)*sqr(diametersub)))**KOGn);
*continuity eqs

AreaEQdeet(i,j,k)$(exist(i,j,k)).. areadeet(i,j,k)=e=pi/4*sqr(diameterdeet(i,j,k));
*Differenital Eqs
ODEcRdeet(i,j,k,ii,jj)$(exist(i,j,k)).. FlowRmlat(i,j,k)*cdotRdeet(i,j,k,ii,jj)=e=fluxdeet(i,j,k,ii,jj);
ODECLdeet(i,j,k,ii,jj)$(exist(i,j,k)).. FlowLmlat(i,j,k)*cdotLdeet(i,j,k,ii,jj)=e=fluxdeet(i,j,k,ii,jj);

loverdupdeet(i,j,k)$(exist(i,j,k))..heightdeet(i,j,k) =l= 25*diameterdeet(i,j,k);
loverdlodeet(i,j,k)$(exist(i,j,k))..heightdeet(i,j,k) =g= 2*diameterdeet(i,j,k);

*Flooding calcs
*no longer anyhting to do with hughes
HughesPDdeet1(i,j,k)$(exist(i,j,k)).. 249.089/0.3048*0.12*((packfactdeetvar(i,j,k)*0.3048)**0.7)  =e= HughesFlood(i,j,k);

HughesPDdeet2(i,j,k)$(exist(i,j,k)).. HughesAct(i,j,k) =e=(94*((ReLdeet(i,j,k)**1.11)/(ReGdeet(i,j,k)**1.8))+4.4)*6*(1-porosity(i)*PoroCor(i,j,k))/(de(i)*partsizecor(i,j,k)*(porosity(i)*PoroCor(i,j,k)**3))*RHOG(i,j)*(velocityRdeet(i,j,k)**2);

ReynoldsGdeet(i,j,k)$(exist(i,j,k))..ReGdeet(i,j,k) =e=   RHOG(i,j)*velocityRdeet(i,j,k)*de(i)*partsizecor(i,j,k)/visrich(i,j);

ReynoldsLdeet(i,j,k)$(exist(i,j,k))..ReLdeet(i,j,k)=e= RHOL(j)*velocityldeet(i,j,k)*de(i)*partsizecor(i,j,k)/vis(j);
*PARTICLE DIAMETER IS THE 0.5 and 0.08 is voidage of Raschig This stuff is from  M. Jamialahmadi et al. / Int. J. Heat and Fluid Flow 26 (2005) 156\96172


HughesPDdeet3(i,j,k)$(exist(i,j,k)).. HughesFlood(i,j,k) =g= HughesAct(i,j,k);

*Initial conditions
ICRdeet(i,j,k)$(exist(i,j,k)).. cR0deet(i,j,k,'1') =e= cinitR(i,j,k);
ICLdeet(i,j,k)$(exist(i,j,k)).. cL0deet(i,j,k,'1') =e= cdesL(i,j,k);
ittdeet(i,j,k)$(exist(i,j,k)).. h0deet(i,j,k,'1')=e=0;
FCRdeet(i,j,k)$(exist(i,j,k)).. cRdeet(i,j,k,'200','3') =e= cdesR(i,j,k);
FCLdeet(i,j,k)$(exist(i,j,k)).. cLdeet(i,j,k,'200','3') =e= cinitL(i,j,k);

*Attempt at getting height to relate to element length
RelHandHeqdeet(i,j,k,ii,jj)$(exist(i,j,k)).. hdeet(i,j,k,ii,jj) =e= 1/nfe*heightdeet(i,j,k) ;

*TTT.. time =e= transtime ;
*heightsub.up(i,j,k) = 5000*diametersub.l(i,j,k);
Model Packedbeddeet /fecolchdeet,ICRdeet,ittdeet,conttdeet,FCRdeet,fcldeet,ReynoldsGdeet,ReynoldsLdeet, loverdlodeet,loverdupdeet,hughesPDdeet1,hughesPDdeet2,hughesPDdeet3,areaEQdeet,VelocityREQdeet,VelocityLEQdeet,ODEcRdeet,ODECLdeet,CONcRdeet,CONcLdeet,FECOLcLdeet,FECOLcRdeet,TRateVapdeet,fobjdeet,kogaeqdeet  /;
*      ICLdeet,     RelHandHeqdeet,
parameter loverdeedeet(i,j,k),HughesPDdeetl(i,j,k),HughesPDact(i,j,k),hughestarget(i,j,k),Aid(i,j,k),ReGAi(i,j,k),ReLAi(i,j,k);

$ontext
Equation from Perry's... Only valid for Raschig rings of CS
y = 397431x2 - 53449x + 2366.1


$offtext

*=============WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW===================
*=============MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM===================
*========================================================================
*========================================================================
*                 Final NLP run that includes interfacial area and everything from above
*                        VAR NAMES: "FINAL"444444444444444444444444444444444444444444444444444444444444444444444444444444444444
*========================================================================
*=============WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW===================
*=============MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM===================
*========================================================================
*                 INITIALISING WITH PREVIOUS RUN
*========================================================================

Variables cRfinal(i,j,k,ii,jj)  concentration of Rich stream along column
          cLfinal(i,j,k,ii,jj)  concentration of lean stream along column
          cdotRfinal(i,j,k,ii,jj)
          cdotLfinal(i,j,k,ii,jj)
          fluxfinal(i,j,k,ii,jj)      molar flux along column
          cr0final(i,j,k,ii)
          cl0final(i,j,k,ii)
          hfinal(i,j,k,ii,jj)
          h0final(i,j,k,ii),
          packfactfinalvar(i,j,k),
          hv(i,j,k,ii)
          Heightfinal(i,j,k)
          diameterfinal(i,j,k),
          Areafinal(i,j,k)
          VelocityRfinal(i,j,k),
          VelocityLfinal(i,j,k),
          KOGafinal(i,j,k),
          HughesActfinal(i,j,k),
          HughesFloodfinal(i,j,k),
         ReLfinal(i,j,k),
         ReGfinal(i,j,k) ,
         aifinal(i,j,k) interfacial area of the packing
          CapCostfinal      objective function ;

*=====================================================================
*        New run that includes pressure drop constraint and L over D
*======================================================================

 Equations  fobjfinal         criterion definition
            ICLfinal,
            ICRfinal,fcrfinal,ittfinal, fclfinal,
           TRateVapfinal,
           AreaEQfinal,
           kogaEqfinal,
           VelocityREQfinal,
           VelocityLEqfinal,
          LoverDupfinal,
          loverdlofinal,
            RelHandHeqfinal,
            FECOLcRfinal,
            FecolcHfinal,
*            FECOLcRint(ii,jj) ,
            FECOLcLfinal ,
*            FECOLcLint(ii,jj) ,
            CONcRfinal,
            CONcLfinal,
            CONttfinal,
            ODEcRfinal,
            ODEcLfinal,
            ReynoldsGfinal,
            ReynoldsLfinal,
            HughesPDfinal1,
            HughesPDfinal2,
            HughesPDfinal3,
         Aidfinal
            ;

* Objective Function
fobjfinal.. CapCostfinal =e= FixCost*sum((i,j,k),exist(i,j,k))+
         AF*(SUM((I,J,K),((23805*(Diameterfinal(i,j,k)**0.57)*1.15*heightfinal(i,j,k)*exist(i,j,k)))))
         +AF*(sum((i,j,k),pi*(diaMETERfinal(i,j,k)**2)/4*HEIGHTfinal(i,j,k)*Packcost(i,j,k)*exist(i,j,k)))
         +(SUM(J,L.l(J)*AC(J)));


TRateVapfinal(i,j,k,ii,jj)$(exist(i,j,k))..  fluxfinal(i,j,k,ii,jj)=e=-kogafinal(i,j,k)*aifinal(i,j,k)*areafinal(i,j,k)*(cRfinal(i,j,k,ii,jj)-henry*clfinal(i,j,k,ii,jj)) ;

*collocation Eqs

FECOLcRfinal(i,j,k,ii,jj)$(ord(ii) le nfe and exist(i,j,k)).. crfinal(i,j,k,ii,jj)=e=cr0final(i,j,k,ii)+ 1/nfe*heightfinal(i,j,k)*sum(kk,a(kk,jj)*cdotRfinal(i,j,k,ii,jj))  ;

FECOLcLfinal(i,j,k,ii,jj)$(ord(ii) le nfe and exist(i,j,k)).. clfinal(i,j,k,ii,jj)=e=cl0final(i,j,k,ii)+ 1/nfe*heightfinal(i,j,k)*sum(kk,a(kk,jj)*cdotlfinal(i,j,k,ii,kk))  ;
*FECOLcLint(i,j)$(ord(j) ge 1)..  h(i)*cdotLint(i,j)=e=sum(k,adot(k,j)*cLint(i,k))  ;
FECOLcHfinal(i,j,k,ii,jj)$(ord(ii) le nfe and exist(i,j,k)).. hfinal(i,j,k,ii,jj) =e= h0final(i,j,k,ii) + heightfinal(i,j,k)*1/nfe*sum(kk, a(kk,jj));

*FECOLtt(i,j)$(ord(i) le nfe).. tt(i,j) =e= tt0(i)
*+height*h(i)*sum(k,a(k,j)) ;

*continuity eqs

CONcRfinal(i,j,k,ii)$(ord(ii) gt 1 and ord(i) le nfe and exist(i,j,k))..
cr0final(i,j,k,ii) =e= cr0final(i,j,k,ii-1)+1/nfe*heightfinal(i,j,k)*sum(jj, cdotRfinal(i,j,k,ii-1,jj)*a(jj,'3'));

CONcLfinal(i,j,k,ii)$(ord(ii) gt 1 and exist(i,j,k))..
cL0final(i,j,k,ii) =e= cl0final(i,j,k,ii-1)+1/nfe*heightfinal(i,j,k)*sum(jj, cdotlfinal(i,j,k,ii-1,jj)*a(jj,'3'));

CONttfinal(i,j,k,ii)$(ord(ii) gt 1 and ord(ii) le nfe and exist(i,j,k))..
h0final(i,j,k,ii) =e= h0final(i,j,k,ii-1) + 1/nfe*heightfinal(i,j,k)*sum(jj, a(jj,'3'));

kogaEqfinal(i,j,k)$(exist(i,j,k))..   KOGafinal(i,j,k) =e= (VelocityRfinal(i,j,k))/(porosity(i)*porocor(i,j,k))*ag*((((de(i)*partsizecor(i,j,k))*(VelocityRfinal(i,j,k)))/(porosity(i)*porocor(i,j,k)*visrich(i,J)))**(-0.25))*(0.7**(-0.677))*(1);


VelocityREQfinal(i,j,k)$(exist(i,j,k))..VelocityRfinal(i,j,k)*Areafinal(i,j,k)=e= flowrvlat(i,j,k);
VelocityLEqfinal(i,j,k)$(exist(i,j,k))..VelocityLfinal(i,j,k)*Areafinal(i,j,k)=e= flowlvlat(i,j,k);
*kogaEq..KOGa =e= KOGb*((FlowRv/((3.14/4)*sqr(diametersub)))**KOGm)*((FlowLv/((3.14/4)*sqr(diametersub)))**KOGn);
*continuity eqs

AreaEQfinal(i,j,k)$(exist(i,j,k)).. areafinal(i,j,k)=e=pi/4*sqr(diameterfinal(i,j,k));
*Differenital Eqs
ODEcRfinal(i,j,k,ii,jj)$(exist(i,j,k)).. FlowRmlat(i,j,k)*cdotRfinal(i,j,k,ii,jj)=e=fluxfinal(i,j,k,ii,jj);
ODECLfinal(i,j,k,ii,jj)$(exist(i,j,k)).. FlowLmlat(i,j,k)*cdotLfinal(i,j,k,ii,jj)=e=fluxfinal(i,j,k,ii,jj);

loverdupfinal(i,j,k)$(exist(i,j,k))..heightfinal(i,j,k) =l= 25*diameterfinal(i,j,k);
loverdlofinal(i,j,k)$(exist(i,j,k))..heightfinal(i,j,k) =g= 2*diameterfinal(i,j,k);

*Flooding calcs
*this appears to be in in H20/ft

*HughesPDfinal1(i,j,k)$(exist(i,j,k)).. 93.9*(packfactfinalvar(i,j,k))**0.7  =e= HughesFloodfinal(i,j,k);

*this is in kpa/m
*1 inch H20 = 249.088908333 Pa
HughesPDfinal1(i,j,k)$(exist(i,j,k)).. 249.089/0.3048*(0.12*(packfactfinalvar(i,j,k)*0.3048)**0.7)  =e= HughesFloodfinal(i,j,k);

HughesPDfinal2(i,j,k)$(exist(i,j,k)).. HughesActfinal(i,j,k) =e=(94*((ReLfinal(i,j,k)**1.11)/(ReGfinal(i,j,k)**1.8))+4.4)*6*(1-0.92)/(0.05*(0.92**3))*RHOG(i,j)*(velocityRfinal(i,j,k)**2);

ReynoldsGfinal(i,j,k)$(exist(i,j,k))..ReGfinal(i,j,k) =e=   RHOG(i,j)*velocityRfinal(i,j,k)/(visrich(i,j)*ap(i,j,k));

ReynoldsLfinal(i,j,k)$(exist(i,j,k))..ReLfinal(i,j,k)=e= RHOL(j)*velocitylfinal(i,j,k)/(vis(j)*aifinal(i,j,k));


Aidfinal(i,j,k)$(exist(i,j,k))..aifinal(i,j,k)=e=Ap(i,j,k)*surfAcor(i,j,k)*(1-exp(-1.45*((0.075/surften(j))**0.75)*((RHOL(j)*velocityRfinal(i,j,k)/(vis(j)*ap(i,j,k)))**0.1)*((ap(i,j,k)*(velocityRfinal(i,j,k)**2)/9.81)**(-0.05))*((RHOL(j)*(velocityRfinal(i,j,k)**2)/(ap(i,j,k)*surften(j)))**0.2)));

*HughesPDfinal1(i,j,k)$(exist(i,j,k)).. 12.2*(packfactfinalvar(i,j,k))**0.7  =e= HughesFloodfinal(i,j,k);

*HughesPDfinal2(i,j,k)$(exist(i,j,k)).. HughesActfinal(i,j,k) =e= 22.3*(packfactfinalvar(i,j,k))*(vis(j)**0.2)*(sqr(velocityRfinal(i,j,k)))*((10**(0.035*velocityLfinal(i,j,k)))/(9.81*RHOG(i,j)));


HughesPDfinal3(i,j,k)$(exist(i,j,k)).. HughesFloodfinal(i,j,k) =g= HughesActfinal(i,j,k);

*Initial conditions
ICRfinal(i,j,k)$(exist(i,j,k)).. cR0final(i,j,k,'1') =e= cinitR(i,j,k);
ICLfinal(i,j,k)$(exist(i,j,k)).. cL0final(i,j,k,'1') =e= cdesL(i,j,k);
ittfinal(i,j,k)$(exist(i,j,k)).. h0final(i,j,k,'1')=e=0;
FCRfinal(i,j,k)$(exist(i,j,k)).. cRfinal(i,j,k,'200','3') =e= cdesR(i,j,k);
FCLfinal(i,j,k)$(exist(i,j,k)).. cLfinal(i,j,k,'200','3') =e= cinitL(i,j,k);

*Attempt at getting height to relate to element length
RelHandHeqfinal(i,j,k,ii,jj)$(exist(i,j,k)).. hfinal(i,j,k,ii,jj) =e= 1/nfe*heightfinal(i,j,k) ;

*TTT.. time =e= transtime ;
*heightsub.up(i,j,k) = 5000*diametersub.l(i,j,k);
Model Packedbedfinal /aidfinal,ICLfinal,ICRfinal,ittfinal,conttfinal,FCRfinal,loverdlofinal,ReynoldsGfinal,ReynoldsLfinal, loverdupfinal,hughesPDfinal1,hughesPDfinal2,hughesPDfinal3,areaEQfinal,VelocityREQfinal,VelocityLEQfinal,ODEcRfinal,ODECLfinal,CONcRfinal,CONcLfinal,FECOLcLfinal,FECOLcRfinal,TRateVapfinal,fobjfinal,kogaeqfinal  /;
*   fclfinal,         RelHandHeqfinal,
parameter loverdeefinal(i,j,k),HughesPDfinall(i,j,k),HughesPDact(i,j,k),hughestarget(i,j,k);

*display hughesactfinal.l;



*=============WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW===================
*=============MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM===================
*========================================================================
*========================================================================
*          NLP run with all from above plus packing characteristics
*                        VAR NAMES: "PACK"555555555555555555555555555555555555555555555555555555555555555555555555555555555555555555555
*========================================================================
*=============WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW===================
*=============MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM===================
*========================================================================
*                 INITIALISING WITH PREVIOUS RUN
*========================================================================

Variables cRpack(i,j,k,ii,jj)  concentration of Rich stream along column
          cLpack(i,j,k,ii,jj)  concentration of lean stream along column
          cdotRpack(i,j,k,ii,jj)
          cdotLpack(i,j,k,ii,jj)
          fluxpack(i,j,k,ii,jj)      molar flux along column
          cr0pack(i,j,k,ii)
          cl0pack(i,j,k,ii)
          hpack(i,j,k,ii,jj)
          h0pack(i,j,k,ii),
          packfactpackvar(i,j,k),
          packingsize(i,j,k),
          hvpack(i,j,k,ii)
          Heightpack(i,j,k)
          diameterpack(i,j,k),
          Areapack(i,j,k),
         SpecAreaPacking(i,j,k),
         PackDens(i,j,k),
         PackVoid(i,j,k),
         PackCostVar(i,j,k),
          VelocityRpack(i,j,k),
          VelocityLpack(i,j,k),
          KOGapack(i,j,k),
          HughesActpack(i,j,k),
          HughesFloodpack(i,j,k),
         ReLpack(i,j,k),
         ReGpack(i,j,k) ,
         aipack(i,j,k) interfacial area of the packing
          CapCostpack      objective function ;

*=====================================================================
*        New run that includes pressure drop constraint and L over D
*======================================================================

 Equations  fobjpack         criterion definition
            ICLpack,
            ICRpack,fcrpack,ittpack,fclpack,
           TRateVappack,
           AreaEQpack,
           kogaEqpack,
           PackcostingEQ,
           VelocityREQpack,
           VelocityLEqpack,
          LoverDuppack,
          loverdlopack,
            RelHandHeqpack,
            FECOLcRpack,
           FEcolchpack,
*            FECOLcRint(ii,jj) ,
            FECOLcLpack ,
*            FECOLcLint(ii,jj) ,
            CONcRpack,
            CONcLpack,
            CONttpack,
            ODEcRpack,
            ODEcLpack,
            ReynoldsGpack,
            ReynoldsLpack,
            HughesPDpack1,
            HughesPDpack2,
            HughesPDpack3,
            Aidpack,
            packingfactorEQ,
            AreaofPackingEQ,
            PackingDensityEQ,
            PackVoidEQ,
            PackingsizeConstraint
            ;

* Objective Function
fobjpack.. CapCostpack =e= FixCost*sum((i,j,k),exist(i,j,k))+
         AF*(SUM((I,J,K),((23805*(Diameterpack(i,j,k)**0.57)*1.15*heightpack(i,j,k)*exist(i,j,k)))))
         +AF*(sum((i,j,k),pi*(diaMETERpack(i,j,k)**2)/4*HEIGHTpack(i,j,k)*Packcostvar(i,j,k)*exist(i,j,k)))
         +(SUM(J,L.l(J)*AC(J)));


TRateVappack(i,j,k,ii,jj)$(exist(i,j,k))..  fluxpack(i,j,k,ii,jj)=e=-kogapack(i,j,k)*aipack(i,j,k)*areapack(i,j,k)*(cRpack(i,j,k,ii,jj)-henry*clpack(i,j,k,ii,jj)) ;

*collocation Eqs

FECOLcRpack(i,j,k,ii,jj)$(ord(ii) le nfe and exist(i,j,k)).. crpack(i,j,k,ii,jj)=e=cr0pack(i,j,k,ii)+ heightpack(i,j,k)*1/nfe*sum(kk,a(kk,jj)*cdotRpack(i,j,k,ii,jj))  ;

FECOLcLpack(i,j,k,ii,jj)$(ord(ii) le nfe and exist(i,j,k)).. clpack(i,j,k,ii,jj)=e=cl0pack(i,j,k,ii)+ heightpack(i,j,k)*1/nfe*sum(kk,a(kk,jj)*cdotlpack(i,j,k,ii,kk))  ;
*FECOLcLint(i,j)$(ord(j) ge 1)..  h(i)*cdotLint(i,j)=e=sum(k,adot(k,j)*cLint(i,k))  ;
FECOLcHpack(i,j,k,ii,jj)$(ord(ii) le nfe and exist(i,j,k)).. hpack(i,j,k,ii,jj) =e= h0pack(i,j,k,ii) + heightpack(i,j,k)*1/nfe*sum(kk, a(kk,jj));

*FECOLtt(i,j)$(ord(i) le nfe).. tt(i,j) =e= tt0(i)
*+height*h(i)*sum(k,a(k,j)) ;

*continuity eqs

CONcRpack(i,j,k,ii)$(ord(ii) gt 1 and ord(i) le nfe and exist(i,j,k))..
cr0pack(i,j,k,ii) =e= cr0pack(i,j,k,ii-1)+heightpack(i,j,k)*1/nfe*sum(jj, cdotRpack(i,j,k,ii-1,jj)*a(jj,'3'));

CONcLpack(i,j,k,ii)$(ord(ii) gt 1 and exist(i,j,k))..
cL0pack(i,j,k,ii) =e= cl0pack(i,j,k,ii-1)+heightpack(i,j,k)*1/nfe*sum(jj, cdotlpack(i,j,k,ii-1,jj)*a(jj,'3'));

CONttpack(i,j,k,ii)$(ord(ii) gt 1 and ord(ii) le nfe and exist(i,j,k))..
h0pack(i,j,k,ii) =e= h0pack(i,j,k,ii-1) + heightpack(i,j,k)*1/nfe*sum(jj, a(jj,'3'));

*kogaEqpack(i,j,k)$(exist(i,j,k))..log(KOGapack(i,j,k)) =e= log(KOGb)+KOGm*log(VelocityRpack(i,j,k))
*                                              +KOGn*log(VelocityLpack(i,j,k));
*THIS POROSITY IS FIXED> CHANGE THIS

kogaEqpack(i,j,k)$(exist(i,j,k))..   KOGapack(i,j,k) =e= (VelocityRpack(i,j,k))/(PackVoid(i,j,k))*ag*((((packingsize(i,j,k))*(VelocityRpack(i,j,k)))/(PackVoid(i,j,k)*visrich(i,J)))**(-0.25))*(0.7**(-0.677))*(1)*exist(I,J,K);


VelocityREQpack(i,j,k)$(exist(i,j,k))..VelocityRpack(i,j,k)*Areapack(i,j,k)=e= flowrvlat(i,j,k);
VelocityLEqpack(i,j,k)$(exist(i,j,k))..VelocityLpack(i,j,k)*Areapack(i,j,k)=e= flowlvlat(i,j,k);
*kogaEq..KOGa =e= KOGb*((FlowRv/((3.14/4)*sqr(diametersub)))**KOGm)*((FlowLv/((3.14/4)*sqr(diametersub)))**KOGn);
*continuity eqs

AreaEQpack(i,j,k)$(exist(i,j,k)).. areapack(i,j,k)=e=pi/4*sqr(diameterpack(i,j,k));
*Differenital Eqs
ODEcRpack(i,j,k,ii,jj)$(exist(i,j,k)).. FlowRmlat(i,j,k)*cdotRpack(i,j,k,ii,jj)=e=fluxpack(i,j,k,ii,jj);
ODECLpack(i,j,k,ii,jj)$(exist(i,j,k)).. FlowLmlat(i,j,k)*cdotLpack(i,j,k,ii,jj)=e=fluxpack(i,j,k,ii,jj);

loverduppack(i,j,k)$(exist(i,j,k))..heightpack(i,j,k) =l= 25*diameterpack(i,j,k);
loverdlopack(i,j,k)$(exist(i,j,k))..heightpack(i,j,k) =g= 2*diameterpack(i,j,k);

*Flooding calcs
*this appears to be in in H20/ft

*HughesPDpack1(i,j,k)$(exist(i,j,k)).. 93.9*(packfactpackvar(i,j,k))**0.7  =e= HughesFloodpack(i,j,k);
$ontext
In packed columns, some of the ultimate performance depends on the column diameter. When
random packings are used, there are many reports of an increase in HETP with column
diameter [15]. Tower diameter is related also to the packing size, and Robbins recommends
that the tower diameter should be at least 8 times the packing size, and if not, the diameter
calculations should be repeated with different packing. The ratio of maximum random packing
size to tower diameter depends, however, on the type of packing used. Although the 1:8 ratio
is in more common use for most packings, some types of packing require a larger ratio of about
1:15, and recent data indicates that Raschig rings require a ratio approaching 1:20 [7, 21].

http://cdn.intechopen.com/pdfs-wm/45966.pdf

$offtext

*PARTICLE DIAMETER IS THE 0.5 and 0.08 is voidage of Raschig This stuff is from  M. Jamialahmadi et al. / Int. J. Heat and Fluid Flow 26 (2005) 156\96172



*this is in kpa/m
*1 inch H20 = 249.088908333 Pa
HughesPDpack1(i,j,k)$(exist(i,j,k)).. 249.089/0.3048*(0.12*(packfactpackvar(i,j,k)*0.3048)**0.7)  =e= HughesFloodpack(i,j,k);

HughesPDpack2(i,j,k)$(exist(i,j,k)).. HughesActpack(i,j,k) =e=(94*((ReLpack(i,j,k)**1.11)/(ReGpack(i,j,k)**1.8))+4.4)*6*(1-PackVoid(i,j,k))/(packingsize(i,j,k)*(PackVoid(i,j,k)**3))*RHOG(i,j)*(velocityRpack(i,j,k)**2);

ReynoldsGpack(i,j,k)$(exist(i,j,k))..ReGpack(i,j,k) =e=   RHOG(i,j)*velocityRpack(i,j,k)/(visrich(i,j)*SpecAreaPacking(i,j,k));

ReynoldsLpack(i,j,k)$(exist(i,j,k))..ReLpack(i,j,k)=e= RHOL(j)*velocitylpack(i,j,k)/(vis(j)*aipack(i,j,k));
*Packing critical surface tension is 0.075 N/m (not sure about it. Got from Hughes for different packing)
*check ap(i,j,k)

Aidpack(i,j,k)$(exist(i,j,k))..aipack(i,j,k)=e=SpecAreaPacking(i,j,k)*(1-exp(-1.45*((0.075/surften(j))**0.75)*((RHOL(j)*velocityRpack(i,j,k)/(vis(j)*SpecAreaPacking(i,j,k)))**0.1)*((SpecAreaPacking(i,j,k)*(velocityRpack(i,j,k)**2)/9.81)**(-0.05))*((RHOL(j)*(velocityRpack(i,j,k)**2)/(SpecAreaPacking(i,j,k)*surften(j)))**0.2)));

*HughesPDpack1(i,j,k)$(exist(i,j,k)).. 12.2*(packfactpackvar(i,j,k))**0.7  =e= HughesFloodpack(i,j,k);

*HughesPDpack2(i,j,k)$(exist(i,j,k)).. HughesActpack(i,j,k) =e= 22.3*(packfactpackvar(i,j,k))*(vis(j)**0.2)*(sqr(velocityRpack(i,j,k)))*((10**(0.035*velocityLpack(i,j,k)))/(9.81*RHOG(i,j)));

packingfactorEQ(i,j,k)$(exist(i,j,k)).. packfactpackvar(i,j,k)=e= (2.0034)*packingsize(i,j,k)**(-1.564);

AreaofPackingEQ(i,j,k)$(exist(i,j,k))..     SpecAreaPacking(i,j,k)=e= (5.0147)*packingsize(i,j,k)**(-0.978);
PackingDensityEQ(i,j,k)$(exist(i,j,k))..    PackDens(i,j,k) =e= (-4E+06)*(packingsize(i,j,k)**3) + 653592*(packingsize(i,j,k))**2 - 31489*packingsize(i,j,k) + 1146.5;
PackVoidEQ(i,j,k)$(exist(i,j,k))..          PackVoid(i,j,k)=e=  0.0569*log(packingsize(i,j,k))+0.9114;
PackCostingEQ(i,j,k)..                      PackCostVar(i,j,k)=e= 397431*packingsize(i,j,k)**2 - 53449*packingsize(i,j,k) + 2366.1;

PackingsizeConstraint(i,j,k)$(exist(i,j,k))..   packingsize(i,j,k)*20=g=diameterpack(i,j,k);

$ontext
Here are the packing characteristic equn for Raschig Rings:
voidage: (in %void) Void=  0.0569*ln(size)+0.9114; R2 =0.8553
density:  y = (-4E+06)x**3 + 653592(x)**2 - 31489x + 1146.5;   R\B2 = 0.9697
area: (in m2/m3) y = 5.0147x**0.978;    R\B2 = 0.9983
packing factor: y = 2.0034x**(-1.564);   R\B2 = 0.9967
Cost for CS RASCHIG: y = 397431x2 - 53449x + 2366.1;  R\B2 = 0.9752

$offtext

HughesPDpack3(i,j,k)$(exist(i,j,k)).. HughesFloodpack(i,j,k) =g= HughesActpack(i,j,k);

*Initial conditions
ICRpack(i,j,k)$(exist(i,j,k)).. cR0pack(i,j,k,'1') =e= cinitR(i,j,k);
ICLpack(i,j,k)$(exist(i,j,k)).. cL0pack(i,j,k,'1') =e= cdesL(i,j,k);
ittpack(i,j,k)$(exist(i,j,k)).. h0pack(i,j,k,'1')=e=0;
FCRpack(i,j,k)$(exist(i,j,k)).. cRpack(i,j,k,'200','3') =e= cdesR(i,j,k);
FCLpack(i,j,k)$(exist(i,j,k)).. cLpack(i,j,k,'200','3') =e= cinitL(i,j,k);
*FCL.. cL('4','3') =e= cinitL;

*Attempt at getting height to relate to element length
RelHandHeqpack(i,j,k,ii,jj)$(exist(i,j,k)).. hpack(i,j,k,ii,jj) =e= 1/nfe*heightpack(i,j,k) ;

*TTT.. time =e= transtime ;
*heightsub.up(i,j,k) = 5000*diametersub.l(i,j,k);
Model Packedbedpack /FECOLcHpack,fclpack,packingfactorEQ,AreaofPackingEQ,packCostingEQ,packingsizeconstraint, PackingDensityEQ,PackVoidEQ,aidpack,ICRpack,ittpack,conttpack,FCRpack,loverdlopack,ReynoldsGpack,ReynoldsLpack, loverduppack,hughesPDpack1,hughesPDpack2,hughesPDpack3,areaEQpack,VelocityREQpack,VelocityLEQpack,ODEcRpack,ODECLpack,CONcRpack,CONcLpack,FECOLcLpack,FECOLcRpack,TRateVappack,fobjpack,kogaeqpack  /;

*      RelHandHeqpack, ICLpack,

parameter Diacond(i,j,k),KWCORCond(i,j,k),HCORcond(i,j,k);



*=============WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW===================
*=============MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM===================
*========================================================================
*========================================================================
*          Just a re-run to see if it will improve
*                        VAR NAMES: "PACK2"6666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666
*========================================================================
*=============WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW===================
*=============MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM===================
*========================================================================
*                 INITIALISING WITH PREVIOUS RUN
*========================================================================

Variables cRpack2(i,j,k,ii,jj)  concentration of Rich stream along column
          cLpack2(i,j,k,ii,jj)  concentration of lean stream along column
          cdotRpack2(i,j,k,ii,jj)
          cdotLpack2(i,j,k,ii,jj)
          fluxpack2(i,j,k,ii,jj)      molar flux along column
          cr0pack2(i,j,k,ii)
          cl0pack2(i,j,k,ii)
          hpack2(i,j,k,ii,jj)
          h0pack2(i,j,k,ii),
          packfactpackvar2(i,j,k),
          packingsize2(i,j,k),
          hvpack2(i,j,k,ii)
          Heightpack2(i,j,k)
          diameterpack2(i,j,k),
          Areapack2(i,j,k),
         SpecAreaPacking2(i,j,k),
         PackDens2(i,j,k),
         PackVoid2(i,j,k),
         PackCostVar2(i,j,k),
          VelocityRpack2(i,j,k),
          VelocityLpack2(i,j,k),
          KOGapack2(i,j,k),
          HughesActpack2(i,j,k),
          HughesFloodpack2(i,j,k),
         ReLpack2(i,j,k),
         ReGpack2(i,j,k) ,
         aipack2(i,j,k) interfacial area of the packing
          CapCostpack2      objective function ;

*=====================================================================
*        New run that includes pressure drop constraint and L over D
*======================================================================

 Equations  fobjpack2         criterion definition
            ICLpack2,
            ICRpack2,fcrpack2,ittpack2,fclpack2,
           TRateVappack2,
           AreaEQpack2,
           kogaEqpack2,
           PackcostingEQ2,
           VelocityREQpack2,
           VelocityLEqpack2,
          LoverDuppack2,
          loverdlopack2,
            RelHandHeqpack2,
            FECOLcRpack2,
         FECOLCHpack2,
*            FECOLcRint(ii,jj) ,
            FECOLcLpack2,
*            FECOLcLint(ii,jj) ,
            CONcRpack2,
            CONcLpack2,
            CONttpack2,
            ODEcRpack2,
            ODEcLpack2,
            ReynoldsGpack2,
            ReynoldsLpack2,
            HughesPDpack12,
            HughesPDpack22,
            HughesPDpack32,
            Aidpack2,
            packingfactorEQ2,
            AreaofPackingEQ2,
            PackingDensityEQ2,
            PackVoidEQ2,
            PackingsizeConstraint2
            ;

* Objective Function
fobjpack2.. CapCostpack2 =e= FixCost*sum((i,j,k),exist(i,j,k))+
         AF*(SUM((I,J,K),((23805*(Diameterpack2(i,j,k)**0.57)*1.15*heightpack2(i,j,k)))))
         +AF*(sum((i,j,k),pi*(diaMETERpack2(i,j,k)**2)/4*HEIGHTpack2(i,j,k)*Packcostvar2(i,j,k)))
         +(SUM(J,L.l(J)*AC(J)));

*            *exist(i,j,k)   *exist(i,j,k)
TRateVappack2(i,j,k,ii,jj)$(exist(i,j,k))..  fluxpack2(i,j,k,ii,jj)=e=-kogapack2(i,j,k)*aipack2(i,j,k)*areapack2(i,j,k)*(cRpack2(i,j,k,ii,jj)-henry*clpack2(i,j,k,ii,jj)) ;

*collocation Eqs

FECOLcRpack2(i,j,k,ii,jj)$(ord(ii) le nfe and exist(i,j,k)).. crpack2(i,j,k,ii,jj)=e=cr0pack2(i,j,k,ii)+ heightpack2(i,j,k)*1/nfe*sum(kk,a(kk,jj)*cdotRpack2(i,j,k,ii,jj))  ;

FECOLcLpack2(i,j,k,ii,jj)$(ord(ii) le nfe and exist(i,j,k)).. clpack2(i,j,k,ii,jj)=e=cl0pack2(i,j,k,ii)+ heightpack2(i,j,k)*1/nfe*sum(kk,a(kk,jj)*cdotlpack2(i,j,k,ii,kk))  ;
*FECOLcLint(i,j)$(ord(j) ge 1)..  h(i)*cdotLint(i,j)=e=sum(k,adot(k,j)*cLint(i,k))  ;
FECOLcHpack2(i,j,k,ii,jj)$(ord(ii) le nfe and exist(i,j,k)).. hpack2(i,j,k,ii,jj) =e= h0pack2(i,j,k,ii) + heightpack2(i,j,k)*1/nfe*sum(kk, a(kk,jj));

*FECOLtt(i,j)$(ord(i) le nfe).. tt(i,j) =e= tt0(i)
*+height*h(i)*sum(k,a(k,j)) ;

*continuity eqs

CONcRpack2(i,j,k,ii)$(ord(ii) gt 1 and ord(i) le nfe and exist(i,j,k))..
cr0pack2(i,j,k,ii) =e= cr0pack2(i,j,k,ii-1)+heightpack2(i,j,k)*1/nfe*sum(jj, cdotRpack2(i,j,k,ii-1,jj)*a(jj,'3'));

CONcLpack2(i,j,k,ii)$(ord(ii) gt 1 and exist(i,j,k))..
cL0pack2(i,j,k,ii) =e= cl0pack2(i,j,k,ii-1)+heightpack2(i,j,k)*1/nfe*sum(jj, cdotlpack2(i,j,k,ii-1,jj)*a(jj,'3'));

CONttpack2(i,j,k,ii)$(ord(ii) gt 1 and ord(ii) le nfe and exist(i,j,k))..
h0pack2(i,j,k,ii) =e= h0pack2(i,j,k,ii-1) + heightpack2(i,j,k)*1/nfe*sum(jj, a(jj,'3'));

*kogaEqpack(i,j,k)$(exist(i,j,k))..log(KOGapack(i,j,k)) =e= log(KOGb)+KOGm*log(VelocityRpack(i,j,k))
*                                              +KOGn*log(VelocityLpack(i,j,k));
*THIS POROSITY IS FIXED> CHANGE THIS

kogaEqpack2(i,j,k)$(exist(i,j,k))..   KOGapack2(i,j,k) =e= (VelocityRpack2(i,j,k))/(PackVoid2(i,j,k))*ag*((((packingsize2(i,j,k))*(VelocityRpack2(i,j,k)))/(PackVoid2(i,j,k)*visrich(i,J)))**(-0.25))*(0.7**(-0.677))*(1);


VelocityREQpack2(i,j,k)$(exist(i,j,k))..VelocityRpack2(i,j,k)*Areapack2(i,j,k)=e= flowrvlat(i,j,k);
VelocityLEqpack2(i,j,k)$(exist(i,j,k))..VelocityLpack2(i,j,k)*Areapack2(i,j,k)=e= flowlvlat(i,j,k);
*kogaEq..KOGa =e= KOGb*((FlowRv/((3.14/4)*sqr(diametersub)))**KOGm)*((FlowLv/((3.14/4)*sqr(diametersub)))**KOGn);
*continuity eqs

AreaEQpack2(i,j,k)$(exist(i,j,k)).. areapack2(i,j,k)=e=pi/4*sqr(diameterpack2(i,j,k));
*Differenital Eqs
ODEcRpack2(i,j,k,ii,jj)$(exist(i,j,k)).. FlowRmlat(i,j,k)*cdotRpack2(i,j,k,ii,jj)=e=fluxpack2(i,j,k,ii,jj);
ODECLpack2(i,j,k,ii,jj)$(exist(i,j,k)).. FlowLmlat(i,j,k)*cdotLpack2(i,j,k,ii,jj)=e=fluxpack2(i,j,k,ii,jj);

loverduppack2(i,j,k)$(exist(i,j,k))..heightpack2(i,j,k) =l= 25*diameterpack2(i,j,k);
loverdlopack2(i,j,k)$(exist(i,j,k))..heightpack2(i,j,k) =g= 2*diameterpack2(i,j,k);

*Flooding calcs
*this appears to be in in H20/ft

*HughesPDpack1(i,j,k)$(exist(i,j,k)).. 93.9*(packfactpackvar(i,j,k))**0.7  =e= HughesFloodpack(i,j,k);
$ontext
In packed columns, some of the ultimate performance depends on the column diameter. When
random packings are used, there are many reports of an increase in HETP with column
diameter [15]. Tower diameter is related also to the packing size, and Robbins recommends
that the tower diameter should be at least 8 times the packing size, and if not, the diameter
calculations should be repeated with different packing. The ratio of maximum random packing
size to tower diameter depends, however, on the type of packing used. Although the 1:8 ratio
is in more common use for most packings, some types of packing require a larger ratio of about
1:15, and recent data indicates that Raschig rings require a ratio approaching 1:20 [7, 21].

http://cdn.intechopen.com/pdfs-wm/45966.pdf

$offtext

*PARTICLE DIAMETER IS THE 0.5 and 0.08 is voidage of Raschig This stuff is from  M. Jamialahmadi et al. / Int. J. Heat and Fluid Flow 26 (2005) 156\96172



*this is in kpa/m
*1 inch H20 = 249.088908333 Pa
HughesPDpack12(i,j,k)$(exist(i,j,k)).. 249.089/0.3048*(0.12*(packfactpackvar2(i,j,k)*0.3048)**0.7)  =e= HughesFloodpack2(i,j,k);

HughesPDpack22(i,j,k)$(exist(i,j,k)).. HughesActpack2(i,j,k) =e=(94*((ReLpack2(i,j,k)**1.11)/(ReGpack2(i,j,k)**1.8))+4.4)*6*(1-PackVoid2(i,j,k))/(packingsize2(i,j,k)*(PackVoid2(i,j,k)**3))*RHOG(i,j)*(velocityRpack2(i,j,k)**2);

ReynoldsGpack2(i,j,k)$(exist(i,j,k))..ReGpack2(i,j,k) =e=   RHOG(i,j)*velocityRpack2(i,j,k)/(visrich(i,j)*SpecAreaPacking2(i,j,k));

ReynoldsLpack2(i,j,k)$(exist(i,j,k))..ReLpack2(i,j,k)=e= RHOL(j)*velocitylpack2(i,j,k)/(vis(j)*aipack2(i,j,k));
*Packing critical surface tension is 0.075 N/m (not sure about it. Got from Hughes for different packing)
*check ap(i,j,k)

Aidpack2(i,j,k)$(exist(i,j,k))..aipack2(i,j,k)=e=SpecAreaPacking2(i,j,k)*(1-exp(-1.45*((0.075/surften(j))**0.75)*((RHOL(j)*velocityRpack2(i,j,k)/(vis(j)*SpecAreaPacking2(i,j,k)))**0.1)*((SpecAreaPacking2(i,j,k)*(velocityRpack2(i,j,k)**2)/9.81)**(-0.05))*((RHOL(j)*(velocityRpack2(i,j,k)**2)/(SpecAreaPacking2(i,j,k)*surften(j)))**0.2)));

*HughesPDpack1(i,j,k)$(exist(i,j,k)).. 12.2*(packfactpackvar(i,j,k))**0.7  =e= HughesFloodpack(i,j,k);

*HughesPDpack2(i,j,k)$(exist(i,j,k)).. HughesActpack(i,j,k) =e= 22.3*(packfactpackvar(i,j,k))*(vis(j)**0.2)*(sqr(velocityRpack(i,j,k)))*((10**(0.035*velocityLpack(i,j,k)))/(9.81*RHOG(i,j)));

packingfactorEQ2(i,j,k)$(exist(i,j,k)).. packfactpackvar2(i,j,k)=e= (2.0034)*packingsize2(i,j,k)**(-1.564);

AreaofPackingEQ2(i,j,k)$(exist(i,j,k))..     SpecAreaPacking2(i,j,k)=e= (5.0147)*packingsize2(i,j,k)**(-0.978);
PackingDensityEQ2(i,j,k)$(exist(i,j,k))..    PackDens2(i,j,k) =e= (-4E+06)*(packingsize2(i,j,k)**3) + 653592*(packingsize2(i,j,k))**2 - 31489*packingsize2(i,j,k) + 1146.5;
PackVoidEQ2(i,j,k)$(exist(i,j,k))..          PackVoid2(i,j,k)=e=  0.0569*log(packingsize2(i,j,k))+0.9114;
PackCostingEQ2(i,j,k)..                      PackCostVar2(i,j,k)=e= 397431*packingsize2(i,j,k)**2 - 53449*packingsize2(i,j,k) + 2366.1;

PackingsizeConstraint2(i,j,k)$(exist(i,j,k))..   packingsize2(i,j,k)*20=g=diameterpack2(i,j,k);

$ontext
Here are the packing characteristic equn for Raschig Rings:
voidage: (in %void) Void=  0.0569*ln(size)+0.9114; R2 =0.8553
density:  y = (-4E+06)x**3 + 653592(x)**2 - 31489x + 1146.5;   R\B2 = 0.9697
area: (in m2/m3) y = 5.0147x**0.978;    R\B2 = 0.9983
packing factor: y = 2.0034x**(-1.564);   R\B2 = 0.9967
Cost for CS RASCHIG: y = 397431x2 - 53449x + 2366.1;  R\B2 = 0.9752

$offtext

HughesPDpack32(i,j,k)$(exist(i,j,k)).. HughesFloodpack2(i,j,k) =g= HughesActpack2(i,j,k);

*Initial conditions
ICRpack2(i,j,k)$(exist(i,j,k)).. cR0pack2(i,j,k,'1') =e= cinitR(i,j,k);
ICLpack2(i,j,k)$(exist(i,j,k)).. cL0pack2(i,j,k,'1') =e= cdesL(i,j,k);
ittpack2(i,j,k)$(exist(i,j,k)).. h0pack2(i,j,k,'1')=e=0;
FCRpack2(i,j,k)$(exist(i,j,k)).. cRpack2(i,j,k,'200','3') =e= cdesR(i,j,k);
FCLpack2(i,j,k)$(exist(i,j,k)).. cLpack2(i,j,k,'200','3') =e= cinitL(i,j,k);

*Attempt at getting height to relate to element length
RelHandHeqpack2(i,j,k,ii,jj)$(exist(i,j,k)).. hpack2(i,j,k,ii,jj) =e= 1/nfe*heightpack2(i,j,k) ;

*TTT.. time =e= transtime ;
*heightsub.up(i,j,k) = 5000*diametersub.l(i,j,k);
Model Packedbedpack2 /FECOLcHpack2,packingfactorEQ2,AreaofPackingEQ2,packCostingEQ2,packingsizeconstraint2, fclpack2,  PackingDensityEQ2,PackVoidEQ2,aidpack2,ICRpack2,FCRpack2,ittpack2,conttpack2,loverdlopack2,ReynoldsGpack2,ReynoldsLpack2, loverduppack2,hughesPDpack12,hughesPDpack22,hughesPDpack32,areaEQpack2,VelocityREQpack2,VelocityLEQpack2,ODEcRpack2,ODECLpack2,CONcRpack2,CONcLpack2,FECOLcLpack2,FECOLcRpack2,TRateVappack2,fobjpack2,kogaeqpack2  /;

*=============WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW=================== RelHandHeqpack2,
*=============MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM===================
*========================================================================
*
*                 INITIALISATION AND MODEL LOOPS
*
*========================================================================
*=============MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM===================
*=============WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW===================



parameter minlpmassL(i,j,k),minlpmassR(i,j,k);


while(icounter <= 2,


*=============WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW===================
*=============MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM===================
*========================================================================
*
*              FIRST MINLP INITS and SOLVE STATEMENT
*
*========================================================================
*=============MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM===================
*=============WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW===================
*===============================================================================
*INITIALISATIONS
*Initialisation for exchanger approach composition between RPS(I) AND LPS(J)
DCINinit.L(I,J,K)$(RPS(I) AND LPS(J) AND arex(I,J,K))=RICH(I,'CIN')-LEAN(J,'CIN') ;
DCOUTinit.L(I,J,K+1)$(RPS(I) AND LPS(J) AND arex (I,J,K))=RICH(I,'CIN')-LEAN(J,'CIN');
DCINinit.LO(I,J,K)$(RPS(I) AND LPS(J) AND arex (I,J,K))=EMAC;
DCOUTinit.LO(I,J,K+1)$(RPS(I) AND LPS(J) AND arex (I,J,K))=EMAC;
DCINinit.UP(I,J,K)$(RPS(I) AND LPS(J) AND arex (I,J,K))=1;
DCOUTinit.UP(I,J,K+1)$(RPS(I) AND LPS(J) AND arex (I,J,K))=1;


FLRICHinit.L(I,J,K)=.1;
FLRICHinit.LO(I,J,K)=.01;
FLRICHinit.UP(I,J,K)= RICH(I,'F');

FLEANinit.L(I,J,K)=.1;
FLEANinit.LO(I,J,K)=.01;
FLEANinit.UP(I,J,K)=10;

CRINinit.L(i,j,k)=RICH(I,'CIN');
*CRIN.LO(i,j,k)=RICH(I,'COUT');

CLINinit.L(i,j,k)=LEAN(J,'CIN');
*CLIN.LO(i,j,k)=LEAN(J,'CIN');

Linit.L('1')=.1;  Linit.LO('1')=.01;  Linit.UP('1')=1.5862;
Linit.L('2')=.1;  Linit.LO('2')=.01;  Linit.UP('2')=2;

*DIAinit.L(I,J,K)$(arex(I,J,K))=1;
*DIAinit.LO(I,J,K)$(arex(I,J,K))=.01;
*DIA.UP(I,J,K)=1.5;

FLVinit.L(I,J,K)=.1;
FLVinit.LO(I,J,K)=.01;
*FLV.UP(I,J,K)=2;

*KAYFOURinit.L(I,J,K)$(arex(I,J,K))=.1;
*KAYFOURinit.LO(I,J,K)$(arex(I,J,K))=.01;
*KAYFOUR.UP(I,J,K)=.75;

AREAinit.L(I,J,K)$(arex(I,J,K))=.1;
AREAinit.LO(I,J,K)$(arex(I,J,K))=.01;
*AREA.UP(I,J,K)=2;

KYAinit.L(I,J,K)$(arex(I,J,K))=1;
KYAinit.LO(I,J,K)$(arex(I,J,K))=.01;
*KYA.UP(I,J,K)=6;

*KYinit.L(I,J,K)$(arex(I,J,K))=.1;
*KYinit.LO(I,J,K)$(arex(I,J,K))=.001;
*KY.UP(I,J,K)=10;

HEIGHTinit.L(I,J,K)$(arex(I,J,K))=1;
HEIGHTinit.LO(I,J,K)$(arex(I,J,K))=.001;
*HEIGHT.UP(I,J,K)= 15;

TRUEHEIGHTinit.L(I,J,K)$(arex(I,J,K))=.1;
TRUEHEIGHTinit.LO(I,J,K)$(arex(I,J,K))=.000001;
*TRUEHEIGHT.UP(I,J,K)= 15;


*Initialisations for M(I,J,K) between RPS(I) and LPS(J)
*$ONTEXT
Minit.L(I,J,K)$(RPS(I) AND arex (I,J,K))=(RICH(I,'F')*(RICH(I,'CIN')-RICH(I,'COUT')));
Minit.L(I,J,K)$(RPS(I) AND arex (I,J,K))=MIN(RICH(I,'F')*(RICH(I,'CIN')-RICH(I,'COUT')),Linit.L(J)*(LEAN(J,'COUT')-LEAN(J,'CIN')));
*Minit.LO(I,J,K)$(RPS(I) AND LPS(J) AND arex (I,J,K))=MIN(RICH(I,'F')*(RICH(I,'CIN')-RICH(I,'COUT')),Linit.L(J)*(LEAN(J,'COUT')-LEAN(J,'CIN')));
*M.L(I,J,K)$(RPS(I) AND LUT(J) AND arex (I,J,K)) = RICH(I,'F')*(RICH(I,'CIN')-RICH(I,'COUT'));

Minit.UP(I,J,K)$(RPS(I) AND LPS(J) AND arex (I,J,K))=MIN(RICH(I,'F')*(RICH(I,'CIN')-RICH(I,'COUT')),Linit.L(J)*(LEAN(J,'COUT')-LEAN(J,'CIN')));
Minit.UP(I,J,K)$(RPS(I) AND arex (I,J,K)) = RICH(I,'F')*(RICH(I,'CIN')-RICH(I,'COUT'));

*Intialisations and bounds for intermediate compositions
*$OFFTEXT

$ONTEXT
CR.L(I,K)$(A_RPS(I,K) OR LAST(K))=RICH(I,'CIN');
CL.L(J,K)$(A_LPS(J,K) OR A_CKL_FIRST(J,K))=LEAN(J,'CIN');

CR.LO(I,K)$(A_RPS(I,K) OR LAST(K))=RICH(I,'COUT');
CR.UP(I,K)$(A_RPS(I,K) OR COMP_IN_RICH(I,K))=RICH(I,'CIN');

CL.LO(J,K)$(A_LPS(J,K) OR A_CKL_FIRST(J,K-1))=LEAN(J,'CIN');
CL.UP(J,K)$(A_LPS(J,K))=LEAN(J,'COUT');
CL.UP(J,K)$(LPS(J) AND A_CKL_FIRST(J,K-1))=LEAN(J,'Cin');
$OFFTEXT

*$ONTEXT
CRinit.L(I,K)$(A_RPS(I,K))=RICH(I,'COUT');
CLinit.L(J,K)$(A_LPS(J,K) AND COMP_IN_LEAN(J,K))=LEAN(J,'CIN');

CRinit.LO(I,K)$(A_RPS(I,K) AND LAST(K))=RICH(I,'COUT');
CRinit.UP(I,K)$(A_RPS(I,K) AND COMP_IN_RICH(I,K))=RICH(I,'CIN');

CLinit.LO(J,K)$(A_LPS(J,K) AND COMP_IN_LEAN(J,K))=LEAN(J,'CIN');
CLinit.UP(J,K)$(A_LPS(J,K) AND COMP_OUT_LEAN(J,K))=LEAN(J,'COUT');


tacinit.l=725000;
*$OFFTEXT

*===============================================================================
EXAMPLE1init.optfile=1;
OPTION DOMLIM =10000;
OPTION ITERLIM =200000;
SOLVE EXAMPLE1init USING MINLP MINIMIZING TACinit;

*=============WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW===================
*=============MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM===================
*========================================================================
*
*              FIRST MINLP INITS and SOLVE STATEMENT
*
*========================================================================
*=============MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM===================
*=============WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW===================
*===============================================================================
*INITIALISATIONS
arex2(i,j,k)=0;
arex2(i,j,k)$(HEIGHTinit.L(I,J,K)>0.08)=1;
display arex2;

*INITIALISATIONS
*Initialisation for exchanger approach composition between RPS(I) AND LPS(J)
DCIN.L(I,J,K)$(RPS(I) AND LPS(J) AND arex2(I,J,K))=DCINinit.L(I,J,K);
DCOUT.L(I,J,K+1)$(RPS(I) AND LPS(J) AND arex2 (I,J,K))=DCoutinit.L(I,J,K);
DCIN.LO(I,J,K)$(RPS(I) AND LPS(J) AND arex2 (I,J,K))=EMAC;
DCOUT.LO(I,J,K+1)$(RPS(I) AND LPS(J) AND arex2 (I,J,K))=EMAC;
*DCIN.UP(I,J,K)$(RPS(I) AND LPS(J) AND arex (I,J,K))=1;
*DCOUT.UP(I,J,K+1)$(RPS(I) AND LPS(J) AND arex (I,J,K))=1;
*y.l(i,j,k)=arex2(i,j,k);

FLRICH.L(I,J,K)$(arex2(i,j,k) and yinit.l(i,j,k))=flrichinit.l(i,j,k);
*FLRICH.LO(I,J,K)$(yinit.l(i,j,k))=.01;
FLRICH.UP(I,J,K)= RICH(I,'F');

FLEAN.L(I,J,K)$(arex2(i,j,k) and yinit.l(i,j,k))=FLEANinit.L(I,J,K);
*FLEAN.LO(I,J,K)=.01;
*FLEAN.UP(I,J,K)=15;

CRIN.L(i,j,k)$(arex2(i,j,k) and yinit.l(i,j,k))=CRINinit.L(i,j,k);
*CRIN.LO(i,j,k)=RICH(I,'COUT');

CLIN.L(i,j,k)$(arex2(i,j,k) and yinit.l(i,j,k))=CLINinit.L(i,j,k);
*CLIN.LO(i,j,k)=LEAN(J,'CIN');

L.L('1')=Linit.l('1');
*L.LO('1')=.01;  L.UP('1')=1.5862;
L.L('2')=Linit.l('2');
* L.LO('2')=.01;  L.UP('2')=2;

*DIA(I,J,K)$(arex2(i,j,k) and yinit.l(i,j,k))=diainit(i,j,k);
*DIA.LO(I,J,K)$(yinit.l(i,j,k))=.01;
*DIA.UP(I,J,K)=1.5;

FLV.L(I,J,K)$(arex2(i,j,k) and yinit.l(i,j,k))=FLVinit.L(I,J,K);
*FLV.LO(I,J,K)$(yinit.l(i,j,k))=.0001;
*FLV.UP(I,J,K)$(yinit.l(i,j,k))=5;

*KAYFOUR.L(I,J,K)=KAYFOURinit.L(I,J,K);
*KAYFOUR.LO(I,J,K)$(yinit.l(i,j,k))=.000001;
*KAYFOUR.UP(I,J,K)=.75;

*AREA.L(I,J,K)=AREAinit.L(I,J,K);
*AREA.LO(I,J,K)$(yinit.l(i,j,k))=.00001;
*AREA.UP(I,J,K)=2;

KYA.L(I,J,K)$(arex2(i,j,k) and yinit.l(i,j,k))=KYAinit.L(I,J,K);
*KYA.LO(I,J,K)$(yinit.l(i,j,k))=.0001;
*KYA.UP(I,J,K)=6;

*KY.L(I,J,K)=KYinit.L(I,J,K);
*KY.LO(I,J,K)$(arex2(i,j,k) and yinit.l(i,j,k))=.00001;
*KY.UP(I,J,K)=10;

HEIGHT.L(I,J,K)$(arex2(i,j,k) and yinit.l(i,j,k))=HEIGHTinit.L(I,J,K);
HEIGHT.LO(I,J,K)$(arex2(i,j,k) and yinit.l(i,j,k))=0.01;
*HEIGHT.UP(I,J,K)= 15;

TRUEHEIGHT.L(I,J,K)$(arex2(i,j,k) and yinit.l(i,j,k))=TRUEHEIGHTinit.L(I,J,K);
*TRUEHEIGHT.LO(I,J,K)=.001;
*TRUEHEIGHT.UP(I,J,K)= 15;

Tac.l=tacinit.l;
*Initialisations for M(I,J,K) between RPS(I) and LPS(J)
*$ONTEXT
*M.L(I,J,K)$(RPS(I) AND arex2 (I,J,K))=Minit.L(I,J,K);
M.L(I,J,K)$(RPS(I) AND arex2 (I,J,K))=Minit.L(I,J,K);
*M.LO(I,J,K)$(RPS(I) AND LPS(J) AND arex2 (I,J,K))=MIN(RICH(I,'F')*(RICH(I,'CIN')-RICH(I,'COUT')),L.L(J)*(LEAN(J,'COUT')-LEAN(J,'CIN')));
*M.L(I,J,K)$(RPS(I) AND LUT(J) AND arex (I,J,K)) = RICH(I,'F')*(RICH(I,'CIN')-RICH(I,'COUT'));

*M.UP(I,J,K)$(RPS(I) AND LPS(J) AND arex (I,J,K))=MIN(RICH(I,'F')*(RICH(I,'CIN')-RICH(I,'COUT')),L.L(J)*(LEAN(J,'COUT')-LEAN(J,'CIN')));
*M.UP(I,J,K)$(RPS(I) AND arex (I,J,K)) = RICH(I,'F')*(RICH(I,'CIN')-RICH(I,'COUT'));

CR.L(I,K)$(A_RPS(I,K))=CRinit.L(I,K);
CL.L(J,K)$(A_LPS(J,K) AND COMP_IN_LEAN(J,K))=CLinit.L(J,K);


*Intialisations and bounds for intermediate compositions
*$OFFTEXT


$ONTEXT
EXUNITR(i,j,k)$(RPS(I) AND arex2 (I,J,K))..
FLRICH(I,J,K)*(CR(I,K)-CRIN(I,J,K+1))=E=M(I,J,K);

EXUNITL(i,j,k)$(LPS(J) AND arex2 (I,J,K))..
FLEAN(I,J,K)*(CLIN(I,J,K)-CL(J,K+1))=E=M(I,J,K);

CR.L(I,K)$(A_RPS(I,K) OR LAST(K))=RICH(I,'CIN');
CL.L(J,K)$(A_LPS(J,K) OR A_CKL_FIRST(J,K))=LEAN(J,'CIN');

CR.LO(I,K)$(A_RPS(I,K) OR LAST(K))=RICH(I,'COUT');
CR.UP(I,K)$(A_RPS(I,K) OR COMP_IN_RICH(I,K))=RICH(I,'CIN');

CL.LO(J,K)$(A_LPS(J,K) OR A_CKL_FIRST(J,K-1))=LEAN(J,'CIN');
CL.UP(J,K)$(A_LPS(J,K))=LEAN(J,'COUT');
CL.UP(J,K)$(LPS(J) AND A_CKL_FIRST(J,K-1))=LEAN(J,'Cin');
$OFFTEXT

*$ONTEXT
*CR.L(I,K)$(A_RPS(I,K))=CRinit.L(I,K);
*CL.L(J,K)$(A_LPS(J,K) AND COMP_IN_LEAN(J,K))=CLinit.L(J,K);

*CR.LO(I,K)$(A_RPS(I,K) AND LAST(K))=RICH(I,'COUT');
*CR.UP(I,K)$(A_RPS(I,K) AND COMP_IN_RICH(I,K))=RICH(I,'CIN');

*CL.LO(J,K)$(A_LPS(J,K) AND COMP_IN_LEAN(J,K))=LEAN(J,'CIN');
*CL.UP(J,K)$(A_LPS(J,K) AND COMP_OUT_LEAN(J,K))=LEAN(J,'COUT');

*$OFFTEXT

*===============================================================================
EXAMPLE1.optfile=1;
OPTION DOMLIM =10000;
OPTION ITERLIM =200000;
SOLVE EXAMPLE1 USING MINLP MINIMIZING TAC;
*POSTPROCESSING

Objheight(i,j,k)= HCor(i,j,k)*HEIGHT.l(I,J,K);
objDia(i,j,k)=diacor(i,j,k)*DIA(I,J,K);
objpackcost(i,j,k)=packcostcor(i,j,k)*packcost(i,j,k);
objai(i,j,k)= Surfarea(I)*surfAcor(i,j,k);
objkw(i,j,k)= kw*kwcor(i,j,k);

display  Objheight,objdia,objai,objpackcost,objkw;
minlpmassR(i,j,k)=(CR.l(I,K)-CRIN.l(I,J,K+1))*flrich.l(i,j,k);

minlpmassL(i,j,k)= (clin.l(i,j,k)-cl.l(j,k+1))*flean.l(i,j,k);
* FLRICH(I,J,K)*(CR(I,K)-CRIN(I,J,K+1))
display   minlpmassL,minlpmassR;


*=============WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW===================
*=============MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM===================
*========================================================================
*
*                 FIRST NLP INITS and SOLVE STATEMENT
*
*========================================================================
*=============MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM===================
*=============WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW===================

Exist(i,j,k)=y.l(i,j,k);
FLRichlat(i,j,k)$(Exist(i,j,k))=FLRICH.l(i,j,k);
*m.l(I,j,k)/(CR.l(I,K)-CR.l(I,K+1));
fleanlat(i,j,k)$(Exist(i,j,k))= FLEAN.l(i,j,k);

cinitR(i,j,k)$EXIST(i,j,k)=cr.l(i,k);
cinitl(i,j,k)$EXIST(i,j,k)=cl.l(j,k+1);
cdesR(i,j,k)$EXIST(i,j,k)=crin.l(i,j,k+1);
cdesL(i,j,k)$EXIST(i,j,k)=clin.l(i,j,k);

flowrmlat(i,j,k)=FLRichlat(i,j,k);
flowlmlat(i,j,k)=FLEANlat(i,j,k);
flowrvlat(i,j,k)=FLRichlat(i,j,k)/RHOG(i,j);
flowlvlat(i,j,k)=FLEANlat(i,j,k)/rhol(j);

display   fleanlat,flrichlat,cinitR, cinitl,cdesR,cdesL,flowrvlat, flowlvlat,flowrmlat, flowlmlat, EXIST;
point = 0;
slopecR(i,j,k,ii,jj) = (cdesR(i,j,k)-cinitR(i,j,k))/(nfe*ncp);
slopecL(i,j,k,ii,jj) = (cdesL(i,j,k)-cinitL(i,j,k))/(nfe*ncp);
diameter(i,j,k)=dia(i,j,k)*diaCor(i,j,k);
*diameter(i,j,k)=10;
*for (iii = 1 to nfe,
*    for (jjj = 1 to ncp,
*         point = point+1;
*        cguessR(i,j,k,ii,jj) = slopecR(i,j,k,ii,jj)*point+cinitR(i,j,k);
*        cguessL(i,j,k,ii,jj) = slopecL(i,j,k,ii,jj)*point+cinitL(i,j,k);
*     );
*);

cguessR(i,j,k,ii,jj)=CinitR(i,j,k)+(cdesR(i,j,k)-cinitR(i,j,k))/2   ;
cguessL(i,j,k,ii,jj) =Cinitl(i,j,k)+(cdesL(i,j,k)-cinitL(i,j,k))/2;

cguessR(i,j,k,'1','1')=CinitR(i,j,k);
cguessR(i,j,k,'200','3')=CdesR(i,j,k);
cguessl(i,j,k,'1','1')=Cinitl(i,j,k);
cguessl(i,j,k,'200','3')=Cdesl(i,j,k);

*hs.lo(i,j,k,ii,jj)$exist(i,j,k)=0.00001;
*hs.up(i,j,k,ii)$exist(i,j,k)=500;

hs.l(i,j,k,ii,jj)$exist(i,j,k)=height.l(i,j,k)/10;
* diameter.l = 0.5;
 heights.l(i,j,k)$exist(i,j,k) = height.l(i,j,k);
heights.lo(i,j,k)$exist(i,j,k)=0.001;
* heights.lo(i,j,k)$exist(i,j,k) = 0.2;
 cRs.l(i,j,k,ii,jj)$exist(i,j,k)  = cguessR(i,j,k,ii,jj);
 cLs.l(i,j,k,ii,jj)$exist(i,j,k)  = cguessL(i,j,k,ii,jj);
*cRs.l(i,j,k,ii,jj)$exist(i,j,k)  = 0.01;
*cLs.l(i,j,k,ii,jj)$exist(i,j,k)  = 0.01;

*capcosts.l=sum((i,j,k),height.l(i,j,k));
*capcosts.lo=0.1;
 cRs.lo(i,j,k,ii,jj)$exist(i,j,k)  = 0.0;
 cLs.lo(i,j,k,ii,jj)$exist(i,j,k)  = 0.0;

* cRs.up(i,j,k,ii,jj)  = 0.5;
* cLs.up(i,j,k,ii,jj)  = 0.5;

cr0.lo(i,j,k,ii)$exist(i,j,k)  = 0.0;
cl0.lo(i,j,k,ii)$exist(i,j,k)  = 0.0;
cr0.l(i,j,k,ii)  = 0.001;
cl0.l(i,j,k,ii)  = 0.001;
*cr0.up(i,j,k,ii)  = 0.5;
*cl0.up(i,j,k,ii)  = 0.5;

*h0.lo(i,j,k,ii)$exist(i,j,k)  = 0.01;
h0.l(i,j,k,ii)$exist(i,j,k)  = height.l(i,j,k)/10;
*h0.up(i,j,k,ii)$exist(i,j,k)  = 100000;
* cRint.l(i,j)  = cguessR(i,j);
* cLint.l(i,j)  = cguessL(i,j);

 cdotR.l(i,j,k,ii,jj)$exist(i,j,k) = -1E-4 ;
*cdotR.up(i,j,k,ii,jj) = -1E-12 ;
*cdotR.lo(i,j,k,ii,jj) = -0.1 ;
 cdotL.l(i,j,k,ii,jj)$exist(i,j,k) = -1e-4 ;
*cdotL.up(i,j,k,ii,jj) = -1E-12 ;
*cdotL.lo(i,j,k,ii,jj) = -0.1 ;

flux.l(i,j,k,ii,jj)$exist(i,j,k) = -1e-3 ;
flux.up(i,j,k,ii,jj)$exist(i,j,k) = 0 ;
*flux.lo(i,j,k,ii,jj)$exist(i,j,k) = -0.1 ;

*fobj.lo=0;

*option nlp = coinipopt;
* option nlp = baron;
 option nlp = conopt;
* option nlp = minos;
*hicks.optfile = 1;

Solve PackedBed minimizing CapCosts using nlp;

velocityR(i,j,k) = flowRvlat(i,j,k)/(pi/4*sqr(diameter(i,j,k)));
velocityL(i,j,k) = flowLvlat(i,j,k)/(pi/4*sqr(diameter(i,j,k)));
loverdee1(i,j,k) = heights.l(i,j,k)/diameter(i,j,k);

display h0.l,cr0.l,cl0.l,CRs.l,CLs.l, heights.l,diameter, hs.l,velocityR,velocityl,loverdee1;
* option nlp = conopt;
* Solve hicks minimizing phi using nlp;

$OFFUPPER
$OFFSYMXREF OFFSYMLIST

leanma(i,j,k)=(cl0.l(i,j,k,'1')-cls.l(i,j,k,'200','3'))*flowlmlat(i,j,k);

Richma(i,j,k)=(cr0.l(i,j,k,'1')-crs.l(i,j,k,'200','3'))*flowrmlat(i,j,k);


costof1 = FixCost*sum((i,j,k),exist(i,j,k))+
         AF*(SUM((I,J,K),((23805*(Diameter(i,j,k)**0.57)*1.15*heights.l(i,j,k)*exist(i,j,k)))))
         +AF*(sum((i,j,k),pi*(diaMETER(i,j,k)**2)/4*HEIGHTs.l(i,j,k)*Packcost(i,j,k)*exist(i,j,k)))
         +(SUM(J,L.l(J)*AC(J)));

elementbalL(i,j,k,ii)= FlowLmlat(i,j,k)*(cl0.l(i,j,k,ii)-cL0.l(i,j,k,ii-1));
elementbalR(i,j,k,ii)= FlowRmlat(i,j,k)*(cr0.l(i,j,k,ii)-cr0.l(i,j,k,ii-1));

display leanma,richma,costof1,elementbalR,elementbalL;
*=============WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW===================
*=============MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM===================
*========================================================================
*
*                 2nd NLP INITS and SOLVE STATEMENT
*
*========================================================================
*=============MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM===================
*=============WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW===================

CapCostinit =costof1 ;
cRsub.l(i,j,k,ii,jj)=crs.l(i,j,k,ii,jj);
crsub.lo(i,j,k,ii,jj)=  0;
*crs.l(i,j,k,ii,jj)/1000000;
*crsub.up(i,j,k,ii,jj)= 1;
*crs.l(i,j,k,ii,jj)*15;

cR0sub.l(i,j,k,ii)=cr0.l(i,j,k,ii);
cr0sub.lo(i,j,k,ii)=  0;
*cr0.l(i,j,k,ii)/10000;
*cr0sub.up(i,j,k,ii)=cr0.l(i,j,k,ii)*15;

cLsub.l(i,j,k,ii,jj)=cls.l(i,j,k,ii,jj);
clsub.lo(i,j,k,ii,jj)=0;
*cls.l(i,j,k,ii,jj)/1000000;
*clsub.up(i,j,k,ii,jj)=1;
*cls.l(i,j,k,ii,jj)*15;

cL0sub.l(i,j,k,ii)=cl0.l(i,j,k,ii);
cl0sub.lo(i,j,k,ii)=  0;
*cl0.l(i,j,k,ii)/100000;
*cl0sub.up(i,j,k,ii)=cl0.l(i,j,k,ii)*15;

cdotRsub.l(i,j,k,ii,jj)=cdotR.l(i,j,k,ii,jj);
*cdotRsub.lo(i,j,k,ii,jj)=cdotR.l(i,j,k,ii,jj)-abs(cdotR.l(i,j,k,ii,jj))*10000;
*cdotRsub.up(i,j,k,ii,jj)= cdotR.l(i,j,k,ii,jj)+abs(cdotR.l(i,j,k,ii,jj))*5;

cdotLsub.l(i,j,k,ii,jj)=cdotl.l(i,j,k,ii,jj);
*cdotlsub.lo(i,j,k,ii,jj)=cdotl.l(i,j,k,ii,jj)-abs(cdotl.l(i,j,k,ii,jj))*10000;
*cdotlsub.up(i,j,k,ii,jj)= cdotl.l(i,j,k,ii,jj)+abs(cdotl.l(i,j,k,ii,jj))*5;

fluxsub.l(i,j,k,ii,jj)=flux.l(i,j,k,ii,jj);
* fluxsub.lo(i,j,k,ii,jj)= -1;
*flux.l(i,j,k,ii,jj)-abs(flux.l(i,j,k,ii,jj))*10000;
* fluxsub.up(i,j,k,ii,jj)= 0;
*flux.l(i,j,k,ii,jj)+abs(flux.l(i,j,k,ii,jj))*5;

hsub.l(i,j,k,ii,jj)=hs.l(i,j,k,ii,jj);
hsub.lo(i,j,k,ii,jj)=0;
*hsub.up(i,j,k,ii)=hs.l(i,j,k,ii)*25;

h0sub.l(i,j,k,ii)=h0.l(i,j,k,ii);
h0sub.lo(i,j,k,ii)=0;
*h0sub.up(i,j,k,ii)=h0.l(i,j,k,ii)*25;

Heightsub.l(i,j,k)$(exist(i,j,k))=heights.l(i,j,k)*1;

Heightsub.lo(i,j,k)$(exist(i,j,k))=0.00000001;
*Heightsub.up(i,j,k)$(exist(i,j,k))=heights.l(i,j,k)*25;

diametersub.l(i,j,k)$(exist(i,j,k))=diameter(i,j,k);
diametersub.lo(i,j,k)$(exist(i,j,k)) = 0.00000000001;
*diametersub.up(i,j,k)$(exist(i,j,k))=diameter(i,j,k)*100;

areasub.l(i,j,k)$(exist(i,j,k))=pi/4*sqr(diameter(i,j,k));
areasub.lo(i,j,k)$(exist(i,j,k))=0.0;
areasub.up(i,j,k)$(exist(i,j,k))=100;

capcostsub.lo=15000;
capcostsub.l=capcostinit;
*capcostsub.up=100000000;

VelocityRsub.l(i,j,k)$(exist(i,j,k))=velocityR(i,j,k);
VelocityRsub.lo(i,j,k)=0.0000001;
VelocityRsub.up(i,j,k)$(exist(i,j,k))=10000;

VelocityLsub.l(i,j,k)$(exist(i,j,k))=velocityL(i,j,k);
VelocityLsub.lo(i,j,k)=0.000000001;
VelocityLsub.up(i,j,k)$(exist(i,j,k))=10000;


koga.l(i,j,k)$(exist(i,j,k))=kw;
koga.lo(i,j,k)$(exist(i,j,k))=0;
*koga.up(i,j,k)$(exist(i,j,k))=0.21;

* height.fx = 150;
*option Rtnwmi=1E-8;
*Rtnwmi=1E-8;
*option nlp = coinipopt;
*optcr=0.05;
*option nlp = baron;
option nlp = conopt;
* option nlp = minos;
*hicks.optfile = 1;

Solve PackedBedsub minimizing CapCostsub using nlp;


loverdee(i,j,k)$(exist(i,j,k))=heightsub.l(i,j,k)/diametersub.l(i,j,k);
KOGap(i,j,k)$(exist(i,j,k)) = KOGb*((FlowRvlat(i,j,k)/((3.14/4)*sqr(diameter(i,j,k))))**KOGm)*((FlowLvlat(i,j,k)/((3.14/4)*sqr(diameter(i,j,k))))**KOGn);
KOGasl(i,j,k)$(exist(i,j,k)) = log(KOGb)+KOGm*log(FlowRvlat(i,j,k)/((3.14/4)*sqr(diametersub.l(i,j,k))))+KOGn*log(FlowLvlat(i,j,k)/((3.14/4)*sqr(diametersub.l(i,j,k))));
*KOGag = log(KOGb)+KOGm*log(FlowRv/((3.14/4)*sqr(diametersub.l)))+KOGn*log(FlowLv/((3.14/4)*sqr(diametersub.l)));
kogas(i,j,k)$(exist(i,j,k)) =  exp(kogasl(i,j,k));

display CRsub.l,CLsub.l, heightsub.l,diametersub.l, velocityRsub.l,velocityLsub.l,hsub.l,kogap,kogas,kogasl,loverdee,koga.l;

ReG(i,j,k)$(exist(i,j,k))= RHOG(i,j)*velocityRsub.l(i,j,k)*0.05/visrich(i,j);
*PARTICLE DIAMETER IS THE 0.5 and 0.08 is voidage of Raschig This stuff is from  M. Jamialahmadi et al. / Int. J. Heat and Fluid Flow 26 (2005) 156\96172
ReL(i,j,k)$(exist(i,j,k))= RHOL(j)*velocitylsub.l(i,j,k)*0.05/vis(j);
NewP(i,j,k)$(exist(i,j,k))= (94*((ReL(i,j,k)**1.11)/(ReG(i,j,k)**1.8))+4.4)*6*(1-0.92)/(0.05*(0.92**3))*RHOG(i,j)*(velocityRsub.l(i,j,k)**2);

Fpdrop(i,j,k)$(exist(i,j,k)) = 0.12*(30.48)**0.7;

ActPdrop(i,j,k)$(exist(i,j,k))= 0;

CP(i,j,k)$(exist(i,j,k))= velocityRsub.l(i,j,k)*sqrt(RHOG(i,j)/(RHOL(j)-RHOG(i,j)))*sqrt(packfact(i))*vis(j)**0.005;

FLVlat(i,j,k)$(exist(i,j,k))= ((flowlmlat(I,J,K))/(FLowRMlat(I,J,K)))*(((RHOG(i,j))/(RHOL(j)))**(0.5));

KAYFOURlat(I,J,K)$exist(i,j,k)=13.1*(((FlowRmlat(I,J,K)/(RHOG(i,j)*((3.14/4)*sqr(diametersub.l(I,J,K))))))**2)*(Packfact(i))*(((VIS(j))/(RHOL(j)))**0.1)/((RHOG(i,j))*(RHOL(j)-RHOG(i,j)));

FLOWLVlat(I,J,K)$exist(i,j,k)= ((flowlmlat(I,J,K))/(FLowRMlat(I,J,K)))*(((RHOG(i,j))/(RHOL(j)))**(0.5));

hughesFp(i,j,k)$(exist(i,j,k)) = 249.089/0.3048*(0.12*(packfact(i)*0.3048)**0.7) ;
HughesPD(i,j,k)$(exist(i,j,k)) = 22.3*(Packfact(i))*(vis(j)**0.2)*(sqr(velocityRsub.l(i,j,k)))*((10**(0.035*velocityLsub.l(i,j,k)))/(9.81*RHOG(i,j)));

display ReG,ReL,NewP,cp,flvlat,fpdrop,kayfourlat,flowlvlat,actpdrop,HughesFp,hughesPD;

leanmasub(i,j,k)=(cl0sub.l(i,j,k,'1')-clsub.l(i,j,k,'200','3'))*flowlmlat(i,j,k);

Richmasub(i,j,k)=(cr0sub.l(i,j,k,'1')-crsub.l(i,j,k,'200','3'))*flowrmlat(i,j,k);
 display leanmasub,richmasub;

*=============WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW===================
*=============MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM===================
*========================================================================
*
*                 3rd NLP INITS and SOLVE STATEMENT
*                        MODEL "DEET"
*
*========================================================================
*=============MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM===================
*=============WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW===================

*CapCostinit = sum((i,j,k), (23805*(Diameter(i,j,k)**0.57)*1.15*heights.l(i,j,k)*exist(i,j,k))+(638*(sqr(Diameter(i,j,k)))*heights.l(i,j,k)*exist(i,j,k)));

ReLDeet.l(i,j,k)=ReL(i,j,k);
ReGDeet.l(i,j,k)=ReG(i,j,k);

cRdeet.l(i,j,k,ii,jj)=crsub.l(i,j,k,ii,jj);
*crdeet.lo(i,j,k,ii,jj)=  0;
*crs.l(i,j,k,ii,jj)/1000000;
*crdeet.up(i,j,k,ii,jj)= 1;
*crs.l(i,j,k,ii,jj)*15;

cR0deet.l(i,j,k,ii)=cr0sub.l(i,j,k,ii);
cr0deet.lo(i,j,k,ii)=  0;
*cr0.l(i,j,k,ii)/10000;
*cr0sub.up(i,j,k,ii)=cr0.l(i,j,k,ii)*15;

cLdeet.l(i,j,k,ii,jj)=clsub.l(i,j,k,ii,jj);
*cldeet.lo(i,j,k,ii,jj)=0;
*cls.l(i,j,k,ii,jj)/1000000;
cldeet.up(i,j,k,ii,jj)=1;
*cls.l(i,j,k,ii,jj)*15;

 cL0deet.l(i,j,k,ii)=cl0sub.l(i,j,k,ii);
cl0deet.lo(i,j,k,ii)=  0;
*cl0.l(i,j,k,ii)/100000;
*cl0sub.up(i,j,k,ii)=cl0.l(i,j,k,ii)*15;

cdotRdeet.l(i,j,k,ii,jj)=cdotRsub.l(i,j,k,ii,jj);
*cdotRsub.lo(i,j,k,ii,jj)=cdotR.l(i,j,k,ii,jj)-abs(cdotR.l(i,j,k,ii,jj))*10000;
*cdotRsub.up(i,j,k,ii,jj)= cdotR.l(i,j,k,ii,jj)+abs(cdotR.l(i,j,k,ii,jj))*5;

cdotLdeet.l(i,j,k,ii,jj)=cdotlsub.l(i,j,k,ii,jj);
*cdotlsub.lo(i,j,k,ii,jj)=cdotl.l(i,j,k,ii,jj)-abs(cdotl.l(i,j,k,ii,jj))*10000;
*cdotlsub.up(i,j,k,ii,jj)= cdotl.l(i,j,k,ii,jj)+abs(cdotl.l(i,j,k,ii,jj))*5;

fluxdeet.l(i,j,k,ii,jj)=fluxsub.l(i,j,k,ii,jj);
 fluxdeet.lo(i,j,k,ii,jj)= -1;
*flux.l(i,j,k,ii,jj)-abs(flux.l(i,j,k,ii,jj))*10000;
* fluxdeet.up(i,j,k,ii,jj)= 0;
*flux.l(i,j,k,ii,jj)+abs(flux.l(i,j,k,ii,jj))*5;

hdeet.l(i,j,k,ii,jj)=hsub.l(i,j,k,ii,jj);
hdeet.lo(i,j,k,ii,jj)=0;
*hsub.up(i,j,k,ii)=hs.l(i,j,k,ii)*25;

h0deet.l(i,j,k,ii)=h0sub.l(i,j,k,ii);
h0deet.lo(i,j,k,ii)=0;
*h0sub.up(i,j,k,ii)=h0.l(i,j,k,ii)*25;

Heightdeet.l(i,j,k)$(exist(i,j,k))=heightsub.l(i,j,k)*1;

Heightdeet.lo(i,j,k)$(exist(i,j,k))=0.01;
*Heightsub.up(i,j,k)$(exist(i,j,k))=heights.l(i,j,k)*25;

diameterdeet.l(i,j,k)$(exist(i,j,k))=diametersub.l(i,j,k);
diameterdeet.lo(i,j,k)$(exist(i,j,k)) = 0.001;
*diametersub.up(i,j,k)$(exist(i,j,k))=diameter(i,j,k)*100;

areadeet.l(i,j,k)$(exist(i,j,k))=pi/4*sqr(diametersub.l(i,j,k));
areadeet.lo(i,j,k)$(exist(i,j,k))=0.0;
areadeet.up(i,j,k)$(exist(i,j,k))=100;

capcostdeet.lo=0;
capcostdeet.l=capcostsub.l;
*capcostsub.up=10000000000;

VelocityRdeet.l(i,j,k)$(exist(i,j,k))=velocityRsub.l(i,j,k);
VelocityRdeet.lo(i,j,k)=0.00000001;
VelocityRdeet.up(i,j,k)$(exist(i,j,k))=15;

VelocityLdeet.l(i,j,k)$(exist(i,j,k))=velocityLsub.l(i,j,k);
VelocityLdeet.lo(i,j,k)=0.000001;
VelocityLdeet.up(i,j,k)$(exist(i,j,k))=100;

kogadeet.l(i,j,k)$(exist(i,j,k))=koga.l(i,j,k);
kogadeet.lo(i,j,k)$(exist(i,j,k))=1E-15;
*koga.up(i,j,k)$(exist(i,j,k))=0.21;

packfactdeetvar.l(i,j,k) =120;
*packfact;
packfactdeetvar.lo(i,j,k) =80;

HughesAct.l(i,j,k) =hughesFP(i,j,k);

Hughesflood.l(i,j,k) =HughesPD(i,j,k);

*option nlp = coinipopt;
*optcr=0.05;
*option nlp = baron;
option nlp = conopt;
* option nlp = minos;
*hicks.optfile = 1;

Solve PackedBeddeet minimizing CapCostdeet using nlp;


loverdeedeet(i,j,k)$(exist(i,j,k))=heightdeet.l(i,j,k)/diameterdeet.l(i,j,k);

HughesTarget(i,j,k)$(exist(i,j,k))=93.9*(packfactdeetvar.l(i,j,k))**0.7;
HughesPDdeetl(i,j,k)$(exist(i,j,k)) = 22.3*(packfactdeetvar.l(i,j,k))*(vis(j)**0.2)*(sqr(velocityRdeet.l(i,j,k)))*((10**(0.035*velocityLdeet.l(i,j,k)))/(9.81*RHOG(i,j)));
HughesPDact(i,j,k)$(exist(i,j,k)) = 22.3*(packfact(i))*(vis(j)**0.2)*(sqr(velocityRdeet.l(i,j,k)))*((10**(0.035*velocityLdeet.l(i,j,k)))/(9.81*RHOG(i,j)));

Aid(i,j,k)$(exist(i,j,k))=Ap(i,j,k)*(1-exp(-1.45*((0.075/surften(j))**0.75)*((RHOL(j)*velocityRdeet.l(i,j,k)/(vis(j)*ap(i,j,k)))**0.1)*((ap(i,j,k)*(velocityRdeet.l(i,j,k)**2)/9.81)**(-0.05))*((RHOL(j)*(velocityRdeet.l(i,j,k)**2)/(ap(i,j,k)*surften(j)))**0.2)));

ReGai(i,j,k)$(exist(i,j,k)) =   RHOG(i,j)*velocityRdeet.l(i,j,k)/(visrich(i,j)*ap(i,j,k));

ReLai(i,j,k)$(exist(i,j,k))= RHOL(j)*velocityldeet.l(i,j,k)/(vis(j)*aid(i,j,k));

display aid,ReGai,ReLai,CRdeet.l,CLdeet.l, heightdeet.l,diameterdeet.l, velocityRdeet.l,velocityLdeet.l,hdeet.l,loverdeedeet,kogadeet.l,hughesFP,hughestarget,hughespddeetl,HughesPDact, hughesact.l,hughesflood.l;
leanmadeet(i,j,k)=(cl0deet.l(i,j,k,'1')-cldeet.l(i,j,k,'200','3'))*flowlmlat(i,j,k);

Richmadeet(i,j,k)=(cr0deet.l(i,j,k,'1')-crdeet.l(i,j,k,'200','3'))*flowrmlat(i,j,k);
 display leanmadeet,richmadeet;
*=============WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW===================
*=============MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM===================
*========================================================================
*
*                 FINAL NLP INITS and SOLVE STATEMENT
*
*========================================================================
*=============MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM===================
*=============WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW===================
ReLfinal.l(i,j,k)$(exist(i,j,k))=ReLai(i,j,k);
ReGfinal.l(i,j,k)$(exist(i,j,k))=ReGai(i,j,k);

ReLfinal.lo(i,j,k)$(exist(i,j,k))=0;
ReGfinal.lo(i,j,k)$(exist(i,j,k))=0;


aifinal.l(i,j,k)$(exist(i,j,k))=aid(i,j,k);
aifinal.lo(i,j,k)$(exist(i,j,k))=0;

cRfinal.l(i,j,k,ii,jj)$(exist(i,j,k))=crdeet.l(i,j,k,ii,jj);
*crfinal.lo(i,j,k,ii,jj)=  0;
*crs.l(i,j,k,ii,jj)/1000000;
*crfinal.up(i,j,k,ii,jj)= 1;
*crs.l(i,j,k,ii,jj)*15;

cR0final.l(i,j,k,ii)$(exist(i,j,k))=cr0deet.l(i,j,k,ii);
cr0final.lo(i,j,k,ii)=  0;
*cr0.l(i,j,k,ii)/10000;
*cr0deet.up(i,j,k,ii)=cr0.l(i,j,k,ii)*15;

cLfinal.l(i,j,k,ii,jj)$(exist(i,j,k))=cldeet.l(i,j,k,ii,jj);
clfinal.lo(i,j,k,ii,jj)=0;
*cls.l(i,j,k,ii,jj)/1000000;
*clfinal.up(i,j,k,ii,jj)=1;
*cls.l(i,j,k,ii,jj)*15;

 cL0final.l(i,j,k,ii)$(exist(i,j,k))=cl0deet.l(i,j,k,ii);
cl0final.lo(i,j,k,ii)=  0;
*cl0.l(i,j,k,ii)/100000;
*cl0deet.up(i,j,k,ii)=cl0.l(i,j,k,ii)*15;

cdotRfinal.l(i,j,k,ii,jj)$(exist(i,j,k))=cdotRdeet.l(i,j,k,ii,jj);
*cdotRdeet.lo(i,j,k,ii,jj)=cdotR.l(i,j,k,ii,jj)-abs(cdotR.l(i,j,k,ii,jj))*10000;
*cdotRdeet.up(i,j,k,ii,jj)= cdotR.l(i,j,k,ii,jj)+abs(cdotR.l(i,j,k,ii,jj))*5;

cdotLfinal.l(i,j,k,ii,jj)$(exist(i,j,k))=cdotldeet.l(i,j,k,ii,jj);
*cdotldeet.lo(i,j,k,ii,jj)=cdotl.l(i,j,k,ii,jj)-abs(cdotl.l(i,j,k,ii,jj))*10000;
*cdotldeet.up(i,j,k,ii,jj)= cdotl.l(i,j,k,ii,jj)+abs(cdotl.l(i,j,k,ii,jj))*5;

fluxfinal.l(i,j,k,ii,jj)$(exist(i,j,k))=fluxdeet.l(i,j,k,ii,jj);
* fluxfinal.lo(i,j,k,ii,jj)$(exist(i,j,k))= -1;
*flux.l(i,j,k,ii,jj)-abs(flux.l(i,j,k,ii,jj))*10000;
* fluxfinal.up(i,j,k,ii,jj)$(exist(i,j,k))= 0;
*flux.l(i,j,k,ii,jj)+abs(flux.l(i,j,k,ii,jj))*5;

hfinal.l(i,j,k,ii,jj)$(exist(i,j,k))=hdeet.l(i,j,k,ii,jj);
hfinal.lo(i,j,k,ii,jj)=0;
*hdeet.up(i,j,k,ii)=hs.l(i,j,k,ii)*25;

h0final.l(i,j,k,ii)$(exist(i,j,k))=h0deet.l(i,j,k,ii);
h0final.lo(i,j,k,ii)=0;
*h0deet.up(i,j,k,ii)=h0.l(i,j,k,ii)*25;

Heightfinal.l(i,j,k)$(exist(i,j,k))=heightdeet.l(i,j,k)*1;

*Heightfinal.lo(i,j,k)$(exist(i,j,k))=0.1;
*Heightdeet.up(i,j,k)$(exist(i,j,k))=heights.l(i,j,k)*25;

diameterfinal.l(i,j,k)$(exist(i,j,k))=diameterdeet.l(i,j,k);
diameterfinal.lo(i,j,k)$(exist(i,j,k)) = 0.001;
*diameterdeet.up(i,j,k)$(exist(i,j,k))=diameter(i,j,k)*100;

areafinal.l(i,j,k)$(exist(i,j,k))=pi/4*sqr(diameterdeet.l(i,j,k));
*areafinal.lo(i,j,k)$(exist(i,j,k))=0.0;
*areafinal.up(i,j,k)$(exist(i,j,k))=100;

capcostfinal.lo=0;
capcostfinal.l=capcostdeet.l;
*capcostdeet.up=10000000000;

VelocityRfinal.l(i,j,k)$(exist(i,j,k))=velocityRdeet.l(i,j,k);
VelocityRfinal.lo(i,j,k)=0.0000001;
VelocityRfinal.up(i,j,k)$(exist(i,j,k))=20;

VelocityLfinal.l(i,j,k)$(exist(i,j,k))=velocityLdeet.l(i,j,k);
VelocityLfinal.lo(i,j,k)=0.0000001;
VelocityLfinal.up(i,j,k)$(exist(i,j,k))=20;

kogafinal.l(i,j,k)$(exist(i,j,k))=kogadeet.l(i,j,k);
kogafinal.lo(i,j,k)$(exist(i,j,k))=1E-15;
*koga.up(i,j,k)$(exist(i,j,k))=0.21;

packfactfinalvar.l(i,j,k)$(exist(i,j,k)) =packfactdeetvar.l(i,j,k) ;
*packfact;
packfactfinalvar.lo(i,j,k)$(exist(i,j,k)) =80;

*packfactfinalvar.up(i,j,k) =5000;

HughesActfinal.l(i,j,k)$(exist(i,j,k)) =hughesACT.l(i,j,k);
HughesActfinal.lo(i,j,k)$(exist(i,j,k)) =0;
Hughesfloodfinal.l(i,j,k)$(exist(i,j,k)) =Hughesflood.l(i,j,k);
Hughesfloodfinal.lo(i,j,k)$(exist(i,j,k)) =0;



*option nlp = coinipopt;
*optcr=0.05;
*option nlp = baron;
option nlp = conopt;
* option nlp = minos;
*hicks.optfile = 1;

Solve PackedBedfinal minimizing CapCostfinal using nlp;


loverdeefinal(i,j,k)$(exist(i,j,k))=heightfinal.l(i,j,k)/diameterfinal.l(i,j,k);

HughesTarget(i,j,k)$(exist(i,j,k))=93.9*(packfactfinalvar.l(i,j,k))**0.7;
HughesPDfinall(i,j,k)$(exist(i,j,k)) = 22.3*(packfactfinalvar.l(i,j,k))*(vis(j)**0.2)*(sqr(velocityRfinal.l(i,j,k)))*((10**(0.035*velocityLfinal.l(i,j,k)))/(9.81*RHOG(i,j)));
HughesPDact(i,j,k)$(exist(i,j,k)) = 22.3*(packfact(i))*(vis(j)**0.2)*(sqr(velocityRfinal.l(i,j,k)))*((10**(0.035*velocityLfinal.l(i,j,k)))/(9.81*RHOG(i,j)));


display aifinal.l,CRfinal.l,CLfinal.l, heightfinal.l,diameterfinal.l, velocityRfinal.l,velocityLfinal.l,hfinal.l,loverdeefinal,kogafinal.l,hughesFP,hughestarget,HughesFloodfinal.l,HughesActfinal.l,hughespdfinall,HughesPDact, hughesact.l,hughesflood.l;
leanmafinal(i,j,k)=(cl0final.l(i,j,k,'1')-clfinal.l(i,j,k,'200','3'))*flowlmlat(i,j,k);

Richmafinal(i,j,k)=(cr0final.l(i,j,k,'1')-crfinal.l(i,j,k,'200','3'))*flowrmlat(i,j,k);
 display leanmafinal,richmafinal;
*=============WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW===================
*=============MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM===================
*========================================================================
*
*                Packing NLP INITS and SOLVE STATEMENT
*
*========================================================================
*=============MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM===================
*=============WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW===================
packfactpackvar.l(i,j,k)$(exist(i,j,k))=packfactfinalvar.l(i,j,k);
packfactpackvar.lo(i,j,k)$(exist(i,j,k))=0;
*packfactpackvar.lo(i,j,k)=100;
packfactpackvar.up(i,j,k)$(exist(i,j,k))=4000;

packingsize.l(i,j,k)$(exist(i,j,k))=0.05;
*packingsize.lo(i,j,k)=0.00;
packingsize.lo(i,j,k)$(exist(i,j,k))=0.006;
*packingsize.up(i,j,k)=0.08;

SpecAreaPacking.l(i,j,k)$(exist(i,j,k))=120;
SpecAreaPacking.lo(i,j,k)$(exist(i,j,k))=5;
*SpecAreaPacking.up(i,j,k)=800;

PackDens.l(i,j,k)$(exist(i,j,k))=660;
PackDens.lo(i,j,k)$(exist(i,j,k))=0;
*PackDens.lo(i,j,k)=550;
*PackDens.up(i,j,k)=1000;

PackVoid.l(i,j,k)$(exist(i,j,k))=0.7;
PackVoid.lo(i,j,k)$(exist(i,j,k))=0.5;
*PackVoid.lo(i,j,k)=0.74;
*PackVoid.up(i,j,k)=0.8;


ReLpack.l(i,j,k)$(exist(i,j,k))=ReLfinal.l(i,j,k);
ReGpack.l(i,j,k)$(exist(i,j,k))=ReGfinal.l(i,j,k);
ReGpack.lo(i,j,k)$(exist(i,j,k))=1;

aipack.l(i,j,k)$(exist(i,j,k))=aifinal.l(i,j,k);


cRpack.l(i,j,k,ii,jj)$(exist(i,j,k))=crfinal.l(i,j,k,ii,jj);
crpack.lo(i,j,k,ii,jj)=  0;
*crs.l(i,j,k,ii,jj)/1000000;
*crpack.up(i,j,k,ii,jj)= 1;
*crs.l(i,j,k,ii,jj)*15;

cR0pack.l(i,j,k,ii)$(exist(i,j,k))=cr0final.l(i,j,k,ii);
*cr0pack.lo(i,j,k,ii)$(exist(i,j,k))=  0;
*cr0.l(i,j,k,ii)/10000;
*cr0final.up(i,j,k,ii)=cr0.l(i,j,k,ii)*15;

cLpack.l(i,j,k,ii,jj)$(exist(i,j,k))=clfinal.l(i,j,k,ii,jj);
clpack.lo(i,j,k,ii,jj)=0;
*cls.l(i,j,k,ii,jj)/1000000;
*clpack.up(i,j,k,ii,jj)=1;
*cls.l(i,j,k,ii,jj)*15;

 cL0pack.l(i,j,k,ii)$(exist(i,j,k))=cl0final.l(i,j,k,ii);
*cl0pack.lo(i,j,k,ii)$(exist(i,j,k))=  0;
*cl0.l(i,j,k,ii)/100000;
*cl0final.up(i,j,k,ii)=cl0.l(i,j,k,ii)*15;

cdotRpack.l(i,j,k,ii,jj)$(exist(i,j,k))=cdotRfinal.l(i,j,k,ii,jj);
*cdotRfinal.lo(i,j,k,ii,jj)=cdotR.l(i,j,k,ii,jj)-abs(cdotR.l(i,j,k,ii,jj))*10000;
*cdotRfinal.up(i,j,k,ii,jj)=  0;
*cdotR.l(i,j,k,ii,jj)+abs(cdotR.l(i,j,k,ii,jj))*5;

cdotLpack.l(i,j,k,ii,jj)=cdotlfinal.l(i,j,k,ii,jj);
*cdotlfinal.lo(i,j,k,ii,jj)=cdotl.l(i,j,k,ii,jj)-abs(cdotl.l(i,j,k,ii,jj))*10000;
*cdotlfinal.up(i,j,k,ii,jj)= cdotl.l(i,j,k,ii,jj)+abs(cdotl.l(i,j,k,ii,jj))*5;

fluxpack.l(i,j,k,ii,jj)$(exist(i,j,k))=fluxfinal.l(i,j,k,ii,jj);
* fluxpack.lo(i,j,k,ii,jj)= -1;
*flux.l(i,j,k,ii,jj)-abs(flux.l(i,j,k,ii,jj))*10000;
* fluxpack.up(i,j,k,ii,jj)$(exist(i,j,k))= 0;
*flux.l(i,j,k,ii,jj)+abs(flux.l(i,j,k,ii,jj))*5;

hpack.l(i,j,k,ii,jj)$(exist(i,j,k))=hfinal.l(i,j,k,ii,jj);
hpack.lo(i,j,k,ii,jj)$(exist(i,j,k))=0;
*hfinal.up(i,j,k,ii)=hs.l(i,j,k,ii)*25;

h0pack.l(i,j,k,ii)$(exist(i,j,k))=h0final.l(i,j,k,ii);
*h0pack.lo(i,j,k,ii)$(exist(i,j,k))=0.001;
*h0final.up(i,j,k,ii)=h0.l(i,j,k,ii)*25;

Heightpack.l(i,j,k)$(exist(i,j,k))=heightfinal.l(i,j,k)*1;

Heightpack.lo(i,j,k)$(exist(i,j,k))=0.15;
*Heightfinal.up(i,j,k)$(exist(i,j,k))=heights.l(i,j,k)*25;

diameterpack.l(i,j,k)$(exist(i,j,k))=diameterfinal.l(i,j,k);
diameterpack.lo(i,j,k)$(exist(i,j,k)) = 0.001;
*diameterfinal.up(i,j,k)$(exist(i,j,k))=diameter(i,j,k)*100;

areapack.l(i,j,k)$(exist(i,j,k))=pi/4*sqr(diameterfinal.l(i,j,k));
areapack.lo(i,j,k)$(exist(i,j,k))=0.0;
*areapack.up(i,j,k)$(exist(i,j,k))=100;

*capcostpack.lo=1000;
capcostpack.l=capcostfinal.l;
*capcostfinal.up=100000000;

VelocityRpack.l(i,j,k)$(exist(i,j,k))=velocityRfinal.l(i,j,k);
VelocityRpack.lo(i,j,k)=0.000001;
*VelocityRpack.up(i,j,k)$(exist(i,j,k))=5;

VelocityLpack.l(i,j,k)$(exist(i,j,k))=velocityLfinal.l(i,j,k);
VelocityLpack.lo(i,j,k)=0.000001;
*VelocityLpack.up(i,j,k)$(exist(i,j,k))=5;

kogapack.l(i,j,k)$(exist(i,j,k))=kogafinal.l(i,j,k);
kogapack.lo(i,j,k)$(exist(i,j,k))=1E-15;
*koga.up(i,j,k)$(exist(i,j,k))=0.21;

packfactpackvar.l(i,j,k)$(exist(i,j,k)) =packfactfinalvar.l(i,j,k) ;
*packfact;
packfactpackvar.lo(i,j,k)$(exist(i,j,k)) =80;

PackcostVar.l(i,j,k)$(exist(i,j,k))=packcost(i,j,k);

*packfactpackvar.up(i,j,k) =5000;

HughesActpack.l(i,j,k)$(exist(i,j,k)) =hughesACTfinal.l(i,j,k);

Hughesfloodpack.l(i,j,k)$(exist(i,j,k)) =Hughesfloodfinal.l(i,j,k);

*option nlp = coinipopt;
*optcr=0.05;
*option nlp = baron;
option nlp = conopt;
* option nlp = minos;
*hicks.optfile = 1;

Solve PackedBedpack minimizing CapCostpack using nlp;


*loverdeepack(i,j,k)$(exist(i,j,k))=heightpack.l(i,j,k)/diameterpack.l(i,j,k);

*HughesTargetpack(i,j,k)$(exist(i,j,k))=93.9*(packfactpackvar.l(i,j,k))**0.7;
*HughesPDpackl(i,j,k)$(exist(i,j,k)) = 22.3*(packfactpackvar.l(i,j,k))*(vis(j)**0.2)*(sqr(velocityRpack.l(i,j,k)))*((10**(0.035*velocityLpack.l(i,j,k)))/(9.81*RHOG(i,j)));
*HughesPDactpack(i,j,k)$(exist(i,j,k)) = 22.3*(packfact(i))*(vis(j)**0.2)*(sqr(velocityRpack.l(i,j,k)))*((10**(0.035*velocityLpack.l(i,j,k)))/(9.81*RHOG(i,j)));


display aipack.l,CRpack.l,CLpack.l, heightpack.l,diameterpack.l,packfactpackvar.l,packingsize.l, velocityRpack.l,velocityLpack.l,hpack.l,kogapack.l,hughesFP,hughestarget,HughesFloodpack.l,HughesActpack.l,HughesPDact, hughesact.l,hughesflood.l;
 leanmapack(i,j,k)=(cl0pack.l(i,j,k,'1')-clpack.l(i,j,k,'200','3'))*flowlmlat(i,j,k);

Richmapack(i,j,k)=(cr0pack.l(i,j,k,'1')-crpack.l(i,j,k,'200','3'))*flowrmlat(i,j,k);
 display leanmapack,richmapack;
*=============WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW===================
*=============MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM===================
*========================================================================
*
*                Packing NLP INITS and SOLVE STATEMENT 2
*
*========================================================================
*=============MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM===================
*=============WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW===================
packfactpackvar2.l(i,j,k)$(exist(i,j,k))=packfactpackvar.l(i,j,k);
packfactpackvar2.lo(i,j,k)$(exist(i,j,k))=0;
*packfactpackvar.lo(i,j,k)=100;
*packfactpackvar2.up(i,j,k)$(exist(i,j,k))=4000;

packingsize2.l(i,j,k)$(exist(i,j,k))=packingsize.l(i,j,k);
*packingsize.lo(i,j,k)=0.00;
packingsize2.lo(i,j,k)$(exist(i,j,k))=0.006;
*packingsize.up(i,j,k)=0.08;

SpecAreaPacking2.l(i,j,k)$(exist(i,j,k))=SpecAreaPacking.l(i,j,k);
SpecAreaPacking2.lo(i,j,k)$(exist(i,j,k))=5;
*SpecAreaPacking.up(i,j,k)=800;

PackDens2.l(i,j,k)$(exist(i,j,k))=PackDens.l(i,j,k);
PackDens2.lo(i,j,k)$(exist(i,j,k))=0;
*PackDens.lo(i,j,k)=550;
*PackDens.up(i,j,k)=1000;

PackVoid2.l(i,j,k)$(exist(i,j,k))=PackVoid.l(i,j,k);
PackVoid2.lo(i,j,k)$(exist(i,j,k))=0.5;
*PackVoid.lo(i,j,k)=0.74;
*PackVoid.up(i,j,k)=0.8;


ReLpack2.l(i,j,k)$(exist(i,j,k))=ReLpack.l(i,j,k);
ReGpack2.l(i,j,k)$(exist(i,j,k))=ReGpack.l(i,j,k);
ReGpack2.lo(i,j,k)$(exist(i,j,k))=1;

aipack2.l(i,j,k)$(exist(i,j,k))=aipack.l(i,j,k);


cRpack2.l(i,j,k,ii,jj)$(exist(i,j,k))=cRpack.l(i,j,k,ii,jj);
crpack2.lo(i,j,k,ii,jj)=  0;
*crs.l(i,j,k,ii,jj)/1000000;
*crpack.up(i,j,k,ii,jj)= 1;
*crs.l(i,j,k,ii,jj)*15;

cR0pack2.l(i,j,k,ii)$(exist(i,j,k))=cR0pack.l(i,j,k,ii);
*cr0pack.lo(i,j,k,ii)$(exist(i,j,k))=  0;
*cr0.l(i,j,k,ii)/10000;
*cr0final.up(i,j,k,ii)=cr0.l(i,j,k,ii)*15;

cLpack2.l(i,j,k,ii,jj)$(exist(i,j,k))=cLpack.l(i,j,k,ii,jj);
clpack2.lo(i,j,k,ii,jj)=0;
*cls.l(i,j,k,ii,jj)/1000000;
*clpack.up(i,j,k,ii,jj)=1;
*cls.l(i,j,k,ii,jj)*15;

 cL0pack2.l(i,j,k,ii)$(exist(i,j,k))=cl0pack.l(i,j,k,ii);
*cl0pack.lo(i,j,k,ii)$(exist(i,j,k))=  0;
*cl0.l(i,j,k,ii)/100000;
*cl0final.up(i,j,k,ii)=cl0.l(i,j,k,ii)*15;

cdotRpack2.l(i,j,k,ii,jj)$(exist(i,j,k))=cdotRpack.l(i,j,k,ii,jj);
*cdotRfinal.lo(i,j,k,ii,jj)=cdotR.l(i,j,k,ii,jj)-abs(cdotR.l(i,j,k,ii,jj))*10000;
*cdotRfinal.up(i,j,k,ii,jj)=  0;
*cdotR.l(i,j,k,ii,jj)+abs(cdotR.l(i,j,k,ii,jj))*5;

cdotLpack2.l(i,j,k,ii,jj)=cdotlpack.l(i,j,k,ii,jj);
*cdotlfinal.lo(i,j,k,ii,jj)=cdotl.l(i,j,k,ii,jj)-abs(cdotl.l(i,j,k,ii,jj))*10000;
*cdotlfinal.up(i,j,k,ii,jj)= cdotl.l(i,j,k,ii,jj)+abs(cdotl.l(i,j,k,ii,jj))*5;

fluxpack2.l(i,j,k,ii,jj)$(exist(i,j,k))=fluxpack.l(i,j,k,ii,jj);
* fluxpack.lo(i,j,k,ii,jj)= -1;
*flux.l(i,j,k,ii,jj)-abs(flux.l(i,j,k,ii,jj))*10000;
* fluxpack.up(i,j,k,ii,jj)$(exist(i,j,k))= 0;
*flux.l(i,j,k,ii,jj)+abs(flux.l(i,j,k,ii,jj))*5;

hpack2.l(i,j,k,ii,jj)$(exist(i,j,k))=hpack.l(i,j,k,ii,jj);
hpack2.lo(i,j,k,ii,jj)$(exist(i,j,k))=0.0001;
*hfinal.up(i,j,k,ii)=hs.l(i,j,k,ii)*25;

h0pack2.l(i,j,k,ii)$(exist(i,j,k))=h0pack.l(i,j,k,ii);
*h0pack.lo(i,j,k,ii)$(exist(i,j,k))=0.001;
*h0final.up(i,j,k,ii)=h0.l(i,j,k,ii)*25;

Heightpack2.l(i,j,k)$(exist(i,j,k))=heightpack.l(i,j,k)*1;

*Heightpack2.lo(i,j,k)$(exist(i,j,k))=0.5;
*Heightfinal.up(i,j,k)$(exist(i,j,k))=heights.l(i,j,k)*25;

diameterpack2.l(i,j,k)$(exist(i,j,k))=diameterpack.l(i,j,k);
diameterpack2.lo(i,j,k)$(exist(i,j,k)) = 0.001;
*diameterfinal.up(i,j,k)$(exist(i,j,k))=diameter(i,j,k)*100;

areapack2.l(i,j,k)$(exist(i,j,k))=areapack.l(i,j,k);
areapack2.lo(i,j,k)$(exist(i,j,k))=0.0;
*areapack.up(i,j,k)$(exist(i,j,k))=100;

*capcostpack.lo=1000;
capcostpack2.l=capcostpack.l;
*capcostfinal.up=100000000;

VelocityRpack2.l(i,j,k)$(exist(i,j,k))=velocityRpack.l(i,j,k);
VelocityRpack2.lo(i,j,k)=0.000001;
*VelocityRpack.up(i,j,k)$(exist(i,j,k))=5;

VelocityLpack2.l(i,j,k)$(exist(i,j,k))=velocityLpack.l(i,j,k);
VelocityLpack2.lo(i,j,k)=0.000001;
*VelocityLpack.up(i,j,k)$(exist(i,j,k))=5;

kogapack2.l(i,j,k)$(exist(i,j,k))=kogapack.l(i,j,k);
kogapack2.lo(i,j,k)$(exist(i,j,k))=1E-15;
*koga.up(i,j,k)$(exist(i,j,k))=0.21;

packfactpackvar2.l(i,j,k)$(exist(i,j,k)) =packfactpackvar.l(i,j,k) ;
*packfact;
*packfactpackvar2.lo(i,j,k)$(exist(i,j,k)) =80;

PackcostVar2.l(i,j,k)$(exist(i,j,k))=packcostvar.l(i,j,k);

*packfactpackvar.up(i,j,k) =5000;

HughesActpack2.l(i,j,k)$(exist(i,j,k)) =HughesActpack.l(i,j,k);

Hughesfloodpack2.l(i,j,k)$(exist(i,j,k)) =Hughesfloodpack.l(i,j,k);

*option nlp = coinipopt;
*optcr=0.05;
*option nlp = baron;
option nlp = conopt;
* option nlp = minos;
*hicks.optfile = 1;

Solve PackedBedpack2 minimizing CapCostpack2 using nlp;


*loverdeepack(i,j,k)$(exist(i,j,k))=heightpack.l(i,j,k)/diameterpack.l(i,j,k);

*HughesTargetpack(i,j,k)$(exist(i,j,k))=93.9*(packfactpackvar.l(i,j,k))**0.7;
*HughesPDpackl(i,j,k)$(exist(i,j,k)) = 22.3*(packfactpackvar.l(i,j,k))*(vis(j)**0.2)*(sqr(velocityRpack.l(i,j,k)))*((10**(0.035*velocityLpack.l(i,j,k)))/(9.81*RHOG(i,j)));
*HughesPDactpack(i,j,k)$(exist(i,j,k)) = 22.3*(packfact(i))*(vis(j)**0.2)*(sqr(velocityRpack.l(i,j,k)))*((10**(0.035*velocityLpack.l(i,j,k)))/(9.81*RHOG(i,j)));


*display aipack.l,CRpack.l,CLpack.l, heightpack.l,diameterpack.l,packfactpackvar.l,packingsize.l, velocityRpack.l,velocityLpack.l,hpack.l,kogapack.l,hughesFP,hughestarget,HughesFloodpack.l,HughesActpack.l,HughesPDact, hughesact.l,hughesflood.l;

 leanmapack2(i,j,k)=(cl0pack2.l(i,j,k,'1')-clpack2.l(i,j,k,'200','3'))*flowlmlat(i,j,k);

Richmapack2(i,j,k)=(cr0pack2.l(i,j,k,'1')-crpack2.l(i,j,k,'200','3'))*flowrmlat(i,j,k);
 display leanmapack2,richmapack2;




*=============WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW===================
*=============MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM===================
*========================================================================
*
*                 CALCULATION OF CORRECTION FACTORS
*
*========================================================================
*=============MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM===================
*=============WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW===================


Diacond(i,j,k)$exist(i,j,k)=diameterpack.l(i,j,k)/Dia(i,j,k);
KWCORCond(i,j,k)$exist(i,j,k)=kogapack.l(i,j,k)/kw;
HCORcond(i,j,k)$exist(i,j,k)=heightpack.l(i,j,k)/height.l(i,j,k);

diacor(i,j,k)$(exist(i,j,k) and diacond(i,j,k) < 0.95) =0.95;
diacor(i,j,k)$(exist(i,j,k) and diacond(i,j,k) > 1.05)=1.05;
diacor(i,j,k)$(exist(i,j,k) and diacond(i,j,k) < 1.05 and diacond(i,j,k) > 0.95)=diacond(i,j,k);

KWCOR(i,j,k)$(exist(i,j,k) and KWCORcond(i,j,k) < 0.95) =0.95;
KWCOR(i,j,k)$(exist(i,j,k) and KWCORcond(i,j,k) > 1.05)=1.05;
KWCOR(i,j,k)$(exist(i,j,k) and KWCORcond(i,j,k) < 1.05 and KWCORcond(i,j,k) > 0.95)=KWCORcond(i,j,k);

HCOR(i,j,k)$(exist(i,j,k) and HCORcond(i,j,k) < 0.95) =0.95;
HCOR(i,j,k)$(exist(i,j,k) and HCORcond(i,j,k) > 1.05)=1.05;
HCOR(i,j,k)$(exist(i,j,k) and HCORcond(i,j,k) < 1.05 and HCORcond(i,j,k) > 0.95)=HCORcond(i,j,k);

execute_unload "Ex1Res1.gdx" tac.l,Y1.l,CR.l,crin.l,cl.l,clin.l,dcin.l,dcout.l,flrich.l,flean.l,flv.l,height.l,capcostpack.l,packcostvar.l,aipack.l,CRpack.l,CLpack.l, heightpack.l,
diameterpack.l,packfactpackvar.l,packingsize.l, velocityRpack.l,velocityLpack.l,hpack.l,
kogapack.l,hughesFP,hughestarget,HughesFloodpack.l,HughesActpack.l,HughesPDact, hughesact.l,hughesflood.l;

$ontext
*MINLP Results
execute 'gdxxrw.exe Ex1Res1.gdx var=tac.L rng=A!A2';
execute 'gdxxrw.exe Ex1Res1.gdx var=y1.L rng=A!B2';
execute 'gdxxrw.exe Ex1Res1.gdx var=cr.L rng=A!H2';
execute 'gdxxrw.exe Ex1Res1.gdx var=crin.L rng=A!H10';
execute 'gdxxrw.exe Ex1Res1.gdx var=cl.L rng=A!N2';
execute 'gdxxrw.exe Ex1Res1.gdx var=clin.L rng=A!N10';
execute 'gdxxrw.exe Ex1Res1.gdx var=flrich.L rng=A!U2';
execute 'gdxxrw.exe Ex1Res1.gdx var=flean.L rng=A!U10';
execute 'gdxxrw.exe Ex1Res1.gdx var=flean.L rng=A!I10';
execute 'gdxxrw.exe Ex1Res1.gdx var=height.L rng=A!B10';

*NLP Results
execute 'gdxxrw.exe Ex1Res1.gdx var=capcostpack.L rng=A!A20';
execute 'gdxxrw.exe Ex1Res1.gdx var=packcostvar.L rng=A!A26';
execute 'gdxxrw.exe Ex1Res1.gdx var=aipack.L rng=A!a32';
execute 'gdxxrw.exe Ex1Res1.gdx var=crpack.L rng=A!e20';
execute 'gdxxrw.exe Ex1Res1.gdx var=clpack.L rng=A!p20';
execute 'gdxxrw.exe Ex1Res1.gdx var=diameterpack.L rng=A!A40';
execute 'gdxxrw.exe Ex1Res1.gdx var=packfactpackvar.l rng=A!A46';
execute 'gdxxrw.exe Ex1Res1.gdx var=packingsize.L rng=A!e26';
execute 'gdxxrw.exe Ex1Res1.gdx var=kogapack.l rng=A!p35';
execute 'gdxxrw.exe Ex1Res1.gdx var=velocityRpack.l rng=A!z20';
execute 'gdxxrw.exe Ex1Res1.gdx var=velocityLpack.l rng=A!Z26';
execute 'gdxxrw.exe Ex1Res1.gdx var=HughesActpack.l rng=A!AE30';
execute 'gdxxrw.exe Ex1Res1.gdx var=HughesFloodpack.l rng=A!AJ20';

$offtext

$ontext
If (diacond(i,j,k) < 0.9,
 diacor(i,j,k)$exist(i,j,k)=0.9;
Elseif (diacond(i,j,k) > 1.1),
 diacor(i,j,k)$exist(i,j,k)=1.1 ;
else
diacor(i,j,k)$exist(i,j,k)=diacond(i,j,k);
) ;

If (KWCORcond(i,j,k) < 0.9,
 KWCOR(i,j,k)$exist(i,j,k)=0.9;
Elseif (KWCORcond(i,j,k) > 1.1),
 KWCOR(i,j,k)$exist(i,j,k)=1.1 ;
else
KWCOR(i,j,k)$exist(i,j,k)=kwcorcond(i,j,k);
) ;

If (HCORcond(i,j,k) < 0.9,
 HCOR(i,j,k)$exist(i,j,k)=0.9;
Elseif (HCORcond(i,j,k) > 1.1),
 HCOR(i,j,k)$exist(i,j,k)=1.1 ;
else
HCOR(i,j,k)$exist(i,j,k)=hcorcond(i,j,k);
) ;
$offtext
icounter=icounter+1;

display  HCORcond,HCOR,KWCOR,KWCORcond, diacor  ,diacond;
)

