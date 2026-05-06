1

   Abaqus 2024                                  Date 20-Apr-2026   Time 06:30:58
   For use by Supplied by Team-SolidSQUAD under license from Dassault Systemes or its subsidiary.

 mono_ep_test                                                                    
                                                                                 
 STEP    1     INCREMENT     1     STEP TIME    0.00    


                        S T E P       1     S T A T I C   A N A L Y S I S


                                                                                          

     AUTOMATIC TIME CONTROL WITH -
          A SUGGESTED INITIAL TIME INCREMENT OF                0.100    
          AND A TOTAL TIME PERIOD OF                            1.00    
          THE MINIMUM TIME INCREMENT ALLOWED IS                1.000E-05
          THE MAXIMUM TIME INCREMENT ALLOWED IS                0.100    

     LINEAR EQUATION SOLVER TYPE         DIRECT SPARSE

 CONVERGENCE TOLERANCE PARAMETERS FOR FORCE    
     CRITERION FOR RESIDUAL FORCE     FOR A NONLINEAR PROBLEM          5.000E-03
     CRITERION FOR DISP.    CORRECTION IN A NONLINEAR PROBLEM          1.000E-02
     INITIAL VALUE OF TIME AVERAGE FORCE                               1.000E-02
     AVERAGE FORCE     IS TIME AVERAGE FORCE    
     ALTERNATE CRIT. FOR RESIDUAL FORCE     FOR A NONLINEAR PROBLEM    2.000E-02
     CRITERION FOR ZERO FORCE     RELATIVE TO TIME AVRG. FORCE         1.000E-05
     CRITERION FOR RESIDUAL FORCE     WHEN THERE IS ZERO FLUX          1.000E-05
     CRITERION FOR DISP.    CORRECTION WHEN THERE IS ZERO FLUX         1.000E-03
     CRITERION FOR RESIDUAL FORCE     FOR A LINEAR INCREMENT           1.000E-08
     FIELD CONVERSION RATIO                                             1.00    
     CRITERION FOR ZERO FORCE     REL. TO TIME AVRG. MAX. FORCE        1.000E-05
     CRITERION FOR ZERO DISP.    RELATIVE TO CHARACTERISTIC LENGTH     1.000E-08

     VOLUMETRIC STRAIN COMPATIBILITY TOLERANCE FOR HYBRID SOLIDS       1.000E-05
     AXIAL STRAIN COMPATIBILITY TOLERANCE FOR HYBRID BEAMS             1.000E-05
     TRANS. SHEAR STRAIN COMPATIBILITY TOLERANCE FOR HYBRID BEAMS      1.000E-05
     SOFT CONTACT CONSTRAINT COMPATIBILITY TOLERANCE FOR P>P0          5.000E-03
     SOFT CONTACT CONSTRAINT COMPATIBILITY TOLERANCE FOR P=0.0         0.100    
     CONTACT FORCE ERROR TOLERANCE FOR CONVERT SDI=YES                 1.00    
     DISPLACEMENT COMPATIBILITY TOLERANCE FOR DCOUP ELEMENTS           1.000E-05
     ROTATION COMPATIBILITY TOLERANCE FOR DCOUP ELEMENTS               1.000E-05

 EQUILIBRIUM WILL BE CHECKED FOR SEVERE DISCONTINUITY ITERATIONS

 TIME INCREMENTATION CONTROL PARAMETERS:
     FIRST EQUILIBRIUM ITERATION FOR CONSECUTIVE DIVERGENCE CHECK              4
     EQUILIBRIUM ITERATION AT WHICH LOG. CONVERGENCE RATE CHECK BEGINS         8
     EQUILIBRIUM ITERATION AFTER WHICH ALTERNATE RESIDUAL IS USED              9
     MAXIMUM EQUILIBRIUM ITERATIONS ALLOWED                                   16
     EQUILIBRIUM ITERATION COUNT FOR CUT-BACK IN NEXT INCREMENT               10
     MAXIMUM EQUILIB. ITERS IN TWO INCREMENTS FOR TIME INCREMENT INCREASE      4
     MAXIMUM ITERATIONS FOR SEVERE DISCONTINUITIES                            50
     MAXIMUM ATTEMPTS ALLOWED IN AN INCREMENT                                  5
     MAXIMUM DISCON. ITERS IN TWO INCREMENTS FOR TIME INCREMENT INCREASE      50
     MAXIMUM CONTACT AUGMENTATIONS FOR *SURFACE BEHAVIOR,AUGMENTED LAGRANGE   50
     CUT-BACK FACTOR AFTER DIVERGENCE                                 0.2500    
     CUT-BACK FACTOR FOR TOO SLOW CONVERGENCE                         0.5000    
     CUT-BACK FACTOR AFTER TOO MANY EQUILIBRIUM ITERATIONS            0.7500    
     CUT-BACK FACTOR AFTER TOO MANY SEVERE DISCONTINUITY ITERATIONS   0.2500    
     CUT-BACK FACTOR AFTER PROBLEMS IN ELEMENT ASSEMBLY               0.2500    
     INCREASE FACTOR AFTER TWO INCREMENTS THAT CONVERGE QUICKLY        1.500    
     MAX. TIME INCREMENT INCREASE FACTOR ALLOWED                       1.500    
     MAX. TIME INCREMENT INCREASE FACTOR ALLOWED (DYNAMICS)            1.250    
     MAX. TIME INCREMENT INCREASE FACTOR ALLOWED (DIFFUSION)           2.000    
     MINIMUM TIME INCREMENT RATIO FOR EXTRAPOLATION TO OCCUR          0.1000    
     MAX. RATIO OF TIME INCREMENT TO STABILITY LIMIT                   1.000    
     FRACTION OF STABILITY LIMIT FOR NEW TIME INCREMENT               0.9500    
     TIME INCREMENT INCREASE FACTOR BEFORE A TIME POINT                1.000    
     GLOBAL STABILIZATION CONTROL IS NOT USED

          PRINT OF INCREMENT NUMBER, TIME, ETC., EVERY    1  INCREMENTS

     THE MAXIMUM NUMBER OF INCREMENTS IN THIS STEP IS                     100

     LINEAR EXTRAPOLATION WILL BE USED

     CHARACTERISTIC ELEMENT LENGTH     0.500    

     DETAILS REGARDING ACTUAL SOLUTION WAVEFRONT REQUESTED

     DETAILED OUTPUT OF DIAGNOSTICS TO DATABASE REQUESTED

     PRINT OF INCREMENT NUMBER, TIME, ETC., TO THE MESSAGE FILE EVERY     1  INCREMENTS

     COLLECTING MODEL CONSTRAINT INFORMATION FOR OVERCONSTRAINT CHECKS

     COLLECTING STEP CONSTRAINT INFORMATION FOR OVERCONSTRAINT CHECKS


  INCREMENT     1 STARTS. ATTEMPT NUMBER  1, TIME INCREMENT  0.100    
 
	SYMMETRIC NEW DIRECT SPARSE SOLVER RUNNING ON
 	1 HOST x 1 MPI RANK PER HOST x 1 THREAD PER RANK
        NUMBER OF EQUATIONS:  1575
        NUMBER OF RHS:        1
        NUMBER OF FLOPS:      2.825e+07
        SOLVER ELAPSED TIME:  18ms

               CONVERGENCE CHECKS FOR EQUILIBRIUM ITERATION     1


 AVERAGE FORCE                       22.4       TIME AVG. FORCE        22.4    
 LARGEST SCALED RESIDUAL FORCE       76.1       AT NODE        498   DOF  3
   INSTANCE: BAR-1                                                                           
  CORRESPONDING RESIDUAL FORCE       76.1    
 LARGEST INCREMENT OF DISP.         5.000E-02   AT NODE          1   DOF  1
   INSTANCE: BAR-1                                                                           
 LARGEST CORRECTION TO DISP.        5.000E-02   AT NODE          1   DOF  1
   INSTANCE: BAR-1                                                                           
          FORCE     EQUILIBRIUM NOT ACHIEVED WITHIN TOLERANCE.
 
	SYMMETRIC NEW DIRECT SPARSE SOLVER RUNNING ON
 	1 HOST x 1 MPI RANK PER HOST x 1 THREAD PER RANK
        NUMBER OF EQUATIONS:  1575
        NUMBER OF RHS:        1
        NUMBER OF FLOPS:      2.825e+07
        SOLVER ELAPSED TIME:  7ms

               CONVERGENCE CHECKS FOR EQUILIBRIUM ITERATION     2


 AVERAGE FORCE                       5.54       TIME AVG. FORCE        5.54    
 LARGEST SCALED RESIDUAL FORCE       59.9       AT NODE        488   DOF  1
   INSTANCE: BAR-1                                                                           
  CORRESPONDING RESIDUAL FORCE       59.9    
 LARGEST INCREMENT OF DISP.         5.000E-02   AT NODE          1   DOF  1
   INSTANCE: BAR-1                                                                           
 LARGEST CORRECTION TO DISP.       -4.161E-03   AT NODE        438   DOF  1
   INSTANCE: BAR-1                                                                           
          FORCE     EQUILIBRIUM NOT ACHIEVED WITHIN TOLERANCE.
 
	SYMMETRIC NEW DIRECT SPARSE SOLVER RUNNING ON
 	1 HOST x 1 MPI RANK PER HOST x 1 THREAD PER RANK
        NUMBER OF EQUATIONS:  1575
        NUMBER OF RHS:        1
        NUMBER OF FLOPS:      2.825e+07
        SOLVER ELAPSED TIME:  6ms

               CONVERGENCE CHECKS FOR EQUILIBRIUM ITERATION     3


 AVERAGE FORCE                       5.54       TIME AVG. FORCE        5.54    
 LARGEST SCALED RESIDUAL FORCE       2.19       AT NODE        483   DOF  3
   INSTANCE: BAR-1                                                                           
  CORRESPONDING RESIDUAL FORCE       2.19    
 LARGEST INCREMENT OF DISP.         5.000E-02   AT NODE          1   DOF  1
   INSTANCE: BAR-1                                                                           
 LARGEST CORRECTION TO DISP.        8.182E-04   AT NODE        488   DOF  1
   INSTANCE: BAR-1                                                                           
          FORCE     EQUILIBRIUM NOT ACHIEVED WITHIN TOLERANCE.
 
	SYMMETRIC NEW DIRECT SPARSE SOLVER RUNNING ON
 	1 HOST x 1 MPI RANK PER HOST x 1 THREAD PER RANK
        NUMBER OF EQUATIONS:  1575
        NUMBER OF RHS:        1
        NUMBER OF FLOPS:      2.825e+07
        SOLVER ELAPSED TIME:  6ms

               CONVERGENCE CHECKS FOR EQUILIBRIUM ITERATION     4


 AVERAGE FORCE                       5.55       TIME AVG. FORCE        5.55    
 LARGEST SCALED RESIDUAL FORCE     -0.236       AT NODE        463   DOF  1
   INSTANCE: BAR-1                                                                           
  CORRESPONDING RESIDUAL FORCE     -0.236    
 LARGEST INCREMENT OF DISP.         5.000E-02   AT NODE          1   DOF  1
   INSTANCE: BAR-1                                                                           
 LARGEST CORRECTION TO DISP.        7.233E-04   AT NODE        438   DOF  1
   INSTANCE: BAR-1                                                                           
          FORCE     EQUILIBRIUM NOT ACHIEVED WITHIN TOLERANCE.
 
	SYMMETRIC NEW DIRECT SPARSE SOLVER RUNNING ON
 	1 HOST x 1 MPI RANK PER HOST x 1 THREAD PER RANK
        NUMBER OF EQUATIONS:  1575
        NUMBER OF RHS:        1
        NUMBER OF FLOPS:      2.825e+07
        SOLVER ELAPSED TIME:  7ms

               CONVERGENCE CHECKS FOR EQUILIBRIUM ITERATION     5


 AVERAGE FORCE                       5.55       TIME AVG. FORCE        5.55    
 LARGEST SCALED RESIDUAL FORCE     -4.469E-03   AT NODE        463   DOF  1
   INSTANCE: BAR-1                                                                           
  CORRESPONDING RESIDUAL FORCE     -4.469E-03
 LARGEST INCREMENT OF DISP.         5.000E-02   AT NODE          1   DOF  1
   INSTANCE: BAR-1                                                                           
 LARGEST CORRECTION TO DISP.        8.155E-05   AT NODE        438   DOF  1
   INSTANCE: BAR-1                                                                           
          THE FORCE     EQUILIBRIUM EQUATIONS HAVE CONVERGED

 ITERATION SUMMARY FOR THE INCREMENT:   5 TOTAL ITERATIONS, OF WHICH
   0 ARE SEVERE DISCONTINUITY ITERATIONS AND  5 ARE EQUILIBRIUM ITERATIONS.

 TIME INCREMENT COMPLETED  0.100    ,  FRACTION OF STEP COMPLETED  0.100    
 STEP TIME COMPLETED       0.100    ,  TOTAL TIME COMPLETED        0.100    


  INCREMENT     2 STARTS. ATTEMPT NUMBER  1, TIME INCREMENT  0.100    
 
	SYMMETRIC NEW DIRECT SPARSE SOLVER RUNNING ON
 	1 HOST x 1 MPI RANK PER HOST x 1 THREAD PER RANK
        NUMBER OF EQUATIONS:  1575
        NUMBER OF RHS:        1
        NUMBER OF FLOPS:      2.825e+07
        SOLVER ELAPSED TIME:  7ms

               CONVERGENCE CHECKS FOR EQUILIBRIUM ITERATION     1


 AVERAGE FORCE                       7.00       TIME AVG. FORCE        6.27    
 LARGEST SCALED RESIDUAL FORCE       2.29       AT NODE        488   DOF  1
   INSTANCE: BAR-1                                                                           
  CORRESPONDING RESIDUAL FORCE       2.29    
 LARGEST INCREMENT OF DISP.         5.000E-02   AT NODE          1   DOF  1
   INSTANCE: BAR-1                                                                           
 LARGEST CORRECTION TO DISP.       -7.026E-04   AT NODE        488   DOF  1
   INSTANCE: BAR-1                                                                           
          FORCE     EQUILIBRIUM NOT ACHIEVED WITHIN TOLERANCE.
 
	SYMMETRIC NEW DIRECT SPARSE SOLVER RUNNING ON
 	1 HOST x 1 MPI RANK PER HOST x 1 THREAD PER RANK
        NUMBER OF EQUATIONS:  1575
        NUMBER OF RHS:        1
        NUMBER OF FLOPS:      2.825e+07
        SOLVER ELAPSED TIME:  7ms

               CONVERGENCE CHECKS FOR EQUILIBRIUM ITERATION     2


 AVERAGE FORCE                       7.00       TIME AVG. FORCE        6.27    
 LARGEST SCALED RESIDUAL FORCE      0.113       AT NODE        488   DOF  1
   INSTANCE: BAR-1                                                                           
  CORRESPONDING RESIDUAL FORCE      0.113    
 LARGEST INCREMENT OF DISP.         5.000E-02   AT NODE          1   DOF  1
   INSTANCE: BAR-1                                                                           
 LARGEST CORRECTION TO DISP.        1.039E-04   AT NODE        438   DOF  1
   INSTANCE: BAR-1                                                                           
          FORCE     EQUILIBRIUM NOT ACHIEVED WITHIN TOLERANCE.
 
	SYMMETRIC NEW DIRECT SPARSE SOLVER RUNNING ON
 	1 HOST x 1 MPI RANK PER HOST x 1 THREAD PER RANK
        NUMBER OF EQUATIONS:  1575
        NUMBER OF RHS:        1
        NUMBER OF FLOPS:      2.825e+07
        SOLVER ELAPSED TIME:  6ms

               CONVERGENCE CHECKS FOR EQUILIBRIUM ITERATION     3


 AVERAGE FORCE                       7.00       TIME AVG. FORCE        6.27    
 LARGEST SCALED RESIDUAL FORCE      2.893E-04   AT NODE        488   DOF  1
   INSTANCE: BAR-1                                                                           
  CORRESPONDING RESIDUAL FORCE      2.893E-04
 LARGEST INCREMENT OF DISP.         5.000E-02   AT NODE          1   DOF  1
   INSTANCE: BAR-1                                                                           
 LARGEST CORRECTION TO DISP.        4.059E-06   AT NODE        488   DOF  1
   INSTANCE: BAR-1                                                                           
          THE FORCE     EQUILIBRIUM EQUATIONS HAVE CONVERGED

 ITERATION SUMMARY FOR THE INCREMENT:   3 TOTAL ITERATIONS, OF WHICH
   0 ARE SEVERE DISCONTINUITY ITERATIONS AND  3 ARE EQUILIBRIUM ITERATIONS.

 TIME INCREMENT COMPLETED  0.100    ,  FRACTION OF STEP COMPLETED  0.200    
 STEP TIME COMPLETED       0.200    ,  TOTAL TIME COMPLETED        0.200    


  INCREMENT     3 STARTS. ATTEMPT NUMBER  1, TIME INCREMENT  0.100    
 
	SYMMETRIC NEW DIRECT SPARSE SOLVER RUNNING ON
 	1 HOST x 1 MPI RANK PER HOST x 1 THREAD PER RANK
        NUMBER OF EQUATIONS:  1575
        NUMBER OF RHS:        1
        NUMBER OF FLOPS:      2.825e+07
        SOLVER ELAPSED TIME:  6ms

               CONVERGENCE CHECKS FOR EQUILIBRIUM ITERATION     1


 AVERAGE FORCE                       7.30       TIME AVG. FORCE        6.62    
 LARGEST SCALED RESIDUAL FORCE       1.10       AT NODE        488   DOF  1
   INSTANCE: BAR-1                                                                           
  CORRESPONDING RESIDUAL FORCE       1.10    
 LARGEST INCREMENT OF DISP.         5.000E-02   AT NODE          1   DOF  1
   INSTANCE: BAR-1                                                                           
 LARGEST CORRECTION TO DISP.        6.462E-04   AT NODE        438   DOF  1
   INSTANCE: BAR-1                                                                           
          FORCE     EQUILIBRIUM NOT ACHIEVED WITHIN TOLERANCE.
 
	SYMMETRIC NEW DIRECT SPARSE SOLVER RUNNING ON
 	1 HOST x 1 MPI RANK PER HOST x 1 THREAD PER RANK
        NUMBER OF EQUATIONS:  1575
        NUMBER OF RHS:        1
        NUMBER OF FLOPS:      2.825e+07
        SOLVER ELAPSED TIME:  6ms

               CONVERGENCE CHECKS FOR EQUILIBRIUM ITERATION     2


 AVERAGE FORCE                       7.31       TIME AVG. FORCE        6.62    
 LARGEST SCALED RESIDUAL FORCE      3.358E-02   AT NODE        488   DOF  1
   INSTANCE: BAR-1                                                                           
  CORRESPONDING RESIDUAL FORCE      3.358E-02
 LARGEST INCREMENT OF DISP.         5.000E-02   AT NODE          1   DOF  1
   INSTANCE: BAR-1                                                                           
 LARGEST CORRECTION TO DISP.        6.833E-05   AT NODE        438   DOF  1
   INSTANCE: BAR-1                                                                           
          FORCE     EQUILIBRIUM NOT ACHIEVED WITHIN TOLERANCE.
 
	SYMMETRIC NEW DIRECT SPARSE SOLVER RUNNING ON
 	1 HOST x 1 MPI RANK PER HOST x 1 THREAD PER RANK
        NUMBER OF EQUATIONS:  1575
        NUMBER OF RHS:        1
        NUMBER OF FLOPS:      2.825e+07
        SOLVER ELAPSED TIME:  6ms

               CONVERGENCE CHECKS FOR EQUILIBRIUM ITERATION     3


 AVERAGE FORCE                       7.31       TIME AVG. FORCE        6.62    
 LARGEST SCALED RESIDUAL FORCE      2.847E-05   AT NODE        488   DOF  1
   INSTANCE: BAR-1                                                                           
  CORRESPONDING RESIDUAL FORCE      2.847E-05
 LARGEST INCREMENT OF DISP.         5.000E-02   AT NODE          1   DOF  1
   INSTANCE: BAR-1                                                                           
 LARGEST CORRECTION TO DISP.        2.042E-06   AT NODE        488   DOF  1
   INSTANCE: BAR-1                                                                           
          THE FORCE     EQUILIBRIUM EQUATIONS HAVE CONVERGED

 ITERATION SUMMARY FOR THE INCREMENT:   3 TOTAL ITERATIONS, OF WHICH
   0 ARE SEVERE DISCONTINUITY ITERATIONS AND  3 ARE EQUILIBRIUM ITERATIONS.

 TIME INCREMENT COMPLETED  0.100    ,  FRACTION OF STEP COMPLETED  0.300    
 STEP TIME COMPLETED       0.300    ,  TOTAL TIME COMPLETED        0.300    


  INCREMENT     4 STARTS. ATTEMPT NUMBER  1, TIME INCREMENT  0.100    
 
	SYMMETRIC NEW DIRECT SPARSE SOLVER RUNNING ON
 	1 HOST x 1 MPI RANK PER HOST x 1 THREAD PER RANK
        NUMBER OF EQUATIONS:  1575
        NUMBER OF RHS:        1
        NUMBER OF FLOPS:      2.825e+07
        SOLVER ELAPSED TIME:  6ms

               CONVERGENCE CHECKS FOR EQUILIBRIUM ITERATION     1


 AVERAGE FORCE                       7.91       TIME AVG. FORCE        6.94    
 LARGEST SCALED RESIDUAL FORCE      4.652E-02   AT NODE        493   DOF  3
   INSTANCE: BAR-1                                                                           
  CORRESPONDING RESIDUAL FORCE      4.652E-02
 LARGEST INCREMENT OF DISP.         5.000E-02   AT NODE          1   DOF  1
   INSTANCE: BAR-1                                                                           
 LARGEST CORRECTION TO DISP.        1.494E-03   AT NODE        363   DOF  1
   INSTANCE: BAR-1                                                                           
          FORCE     EQUILIBRIUM NOT ACHIEVED WITHIN TOLERANCE.
 
	SYMMETRIC NEW DIRECT SPARSE SOLVER RUNNING ON
 	1 HOST x 1 MPI RANK PER HOST x 1 THREAD PER RANK
        NUMBER OF EQUATIONS:  1575
        NUMBER OF RHS:        1
        NUMBER OF FLOPS:      2.825e+07
        SOLVER ELAPSED TIME:  7ms

               CONVERGENCE CHECKS FOR EQUILIBRIUM ITERATION     2


 AVERAGE FORCE                       7.86       TIME AVG. FORCE        6.93    
 LARGEST SCALED RESIDUAL FORCE     -6.905E-05   AT NODE        488   DOF  1
   INSTANCE: BAR-1                                                                           
  CORRESPONDING RESIDUAL FORCE     -6.905E-05
 LARGEST INCREMENT OF DISP.         5.000E-02   AT NODE          1   DOF  1
   INSTANCE: BAR-1                                                                           
 LARGEST CORRECTION TO DISP.        1.602E-05   AT NODE        371   DOF  1
   INSTANCE: BAR-1                                                                           
          THE FORCE     EQUILIBRIUM EQUATIONS HAVE CONVERGED

 ITERATION SUMMARY FOR THE INCREMENT:   2 TOTAL ITERATIONS, OF WHICH
   0 ARE SEVERE DISCONTINUITY ITERATIONS AND  2 ARE EQUILIBRIUM ITERATIONS.

 TIME INCREMENT COMPLETED  0.100    ,  FRACTION OF STEP COMPLETED  0.400    
 STEP TIME COMPLETED       0.400    ,  TOTAL TIME COMPLETED        0.400    


  INCREMENT     5 STARTS. ATTEMPT NUMBER  1, TIME INCREMENT  0.100    
 
	SYMMETRIC NEW DIRECT SPARSE SOLVER RUNNING ON
 	1 HOST x 1 MPI RANK PER HOST x 1 THREAD PER RANK
        NUMBER OF EQUATIONS:  1575
        NUMBER OF RHS:        1
        NUMBER OF FLOPS:      2.825e+07
        SOLVER ELAPSED TIME:  6ms

               CONVERGENCE CHECKS FOR EQUILIBRIUM ITERATION     1


 AVERAGE FORCE                       7.76       TIME AVG. FORCE        7.09    
 LARGEST SCALED RESIDUAL FORCE     -0.789       AT NODE        462   DOF  2
   INSTANCE: BAR-1                                                                           
  CORRESPONDING RESIDUAL FORCE     -0.789    
 LARGEST INCREMENT OF DISP.         5.000E-02   AT NODE          1   DOF  1
   INSTANCE: BAR-1                                                                           
 LARGEST CORRECTION TO DISP.       -3.234E-03   AT NODE        413   DOF  1
   INSTANCE: BAR-1                                                                           
          FORCE     EQUILIBRIUM NOT ACHIEVED WITHIN TOLERANCE.
 
	SYMMETRIC NEW DIRECT SPARSE SOLVER RUNNING ON
 	1 HOST x 1 MPI RANK PER HOST x 1 THREAD PER RANK
        NUMBER OF EQUATIONS:  1575
        NUMBER OF RHS:        1
        NUMBER OF FLOPS:      2.825e+07
        SOLVER ELAPSED TIME:  7ms

               CONVERGENCE CHECKS FOR EQUILIBRIUM ITERATION     2


 AVERAGE FORCE                       7.80       TIME AVG. FORCE        7.10    
 LARGEST SCALED RESIDUAL FORCE     -2.474E-02   AT NODE        483   DOF  3
   INSTANCE: BAR-1                                                                           
  CORRESPONDING RESIDUAL FORCE     -2.474E-02
 LARGEST INCREMENT OF DISP.         5.000E-02   AT NODE          1   DOF  1
   INSTANCE: BAR-1                                                                           
 LARGEST CORRECTION TO DISP.        2.854E-04   AT NODE        384   DOF  1
   INSTANCE: BAR-1                                                                           
          THE FORCE     EQUILIBRIUM EQUATIONS HAVE CONVERGED

 ITERATION SUMMARY FOR THE INCREMENT:   2 TOTAL ITERATIONS, OF WHICH
   0 ARE SEVERE DISCONTINUITY ITERATIONS AND  2 ARE EQUILIBRIUM ITERATIONS.

 TIME INCREMENT COMPLETED  0.100    ,  FRACTION OF STEP COMPLETED  0.500    
 STEP TIME COMPLETED       0.500    ,  TOTAL TIME COMPLETED        0.500    


  INCREMENT     6 STARTS. ATTEMPT NUMBER  1, TIME INCREMENT  0.100    
 
	SYMMETRIC NEW DIRECT SPARSE SOLVER RUNNING ON
 	1 HOST x 1 MPI RANK PER HOST x 1 THREAD PER RANK
        NUMBER OF EQUATIONS:  1575
        NUMBER OF RHS:        1
        NUMBER OF FLOPS:      2.825e+07
        SOLVER ELAPSED TIME:  6ms

               CONVERGENCE CHECKS FOR EQUILIBRIUM ITERATION     1


 AVERAGE FORCE                       8.18       TIME AVG. FORCE        7.28    
 LARGEST SCALED RESIDUAL FORCE     -0.147       AT NODE        462   DOF  2
   INSTANCE: BAR-1                                                                           
  CORRESPONDING RESIDUAL FORCE     -0.147    
 LARGEST INCREMENT OF DISP.         5.000E-02   AT NODE          1   DOF  1
   INSTANCE: BAR-1                                                                           
 LARGEST CORRECTION TO DISP.       -1.862E-03   AT NODE        363   DOF  1
   INSTANCE: BAR-1                                                                           
          FORCE     EQUILIBRIUM NOT ACHIEVED WITHIN TOLERANCE.
 
	SYMMETRIC NEW DIRECT SPARSE SOLVER RUNNING ON
 	1 HOST x 1 MPI RANK PER HOST x 1 THREAD PER RANK
        NUMBER OF EQUATIONS:  1575
        NUMBER OF RHS:        1
        NUMBER OF FLOPS:      2.825e+07
        SOLVER ELAPSED TIME:  6ms

               CONVERGENCE CHECKS FOR EQUILIBRIUM ITERATION     2


 AVERAGE FORCE                       8.25       TIME AVG. FORCE        7.29    
 LARGEST SCALED RESIDUAL FORCE     -1.813E-03   AT NODE        458   DOF  3
   INSTANCE: BAR-1                                                                           
  CORRESPONDING RESIDUAL FORCE     -1.813E-03
 LARGEST INCREMENT OF DISP.         5.000E-02   AT NODE          1   DOF  1
   INSTANCE: BAR-1                                                                           
 LARGEST CORRECTION TO DISP.        9.733E-05   AT NODE        413   DOF  1
   INSTANCE: BAR-1                                                                           
          THE FORCE     EQUILIBRIUM EQUATIONS HAVE CONVERGED

 ITERATION SUMMARY FOR THE INCREMENT:   2 TOTAL ITERATIONS, OF WHICH
   0 ARE SEVERE DISCONTINUITY ITERATIONS AND  2 ARE EQUILIBRIUM ITERATIONS.

 TIME INCREMENT COMPLETED  0.100    ,  FRACTION OF STEP COMPLETED  0.600    
 STEP TIME COMPLETED       0.600    ,  TOTAL TIME COMPLETED        0.600    


  INCREMENT     7 STARTS. ATTEMPT NUMBER  1, TIME INCREMENT  0.100    
 
	SYMMETRIC NEW DIRECT SPARSE SOLVER RUNNING ON
 	1 HOST x 1 MPI RANK PER HOST x 1 THREAD PER RANK
        NUMBER OF EQUATIONS:  1575
        NUMBER OF RHS:        1
        NUMBER OF FLOPS:      2.825e+07
        SOLVER ELAPSED TIME:  6ms

               CONVERGENCE CHECKS FOR EQUILIBRIUM ITERATION     1


 AVERAGE FORCE                       8.40       TIME AVG. FORCE        7.45    
 LARGEST SCALED RESIDUAL FORCE      0.132       AT NODE        463   DOF  1
   INSTANCE: BAR-1                                                                           
  CORRESPONDING RESIDUAL FORCE      0.132    
 LARGEST INCREMENT OF DISP.         5.000E-02   AT NODE          1   DOF  1
   INSTANCE: BAR-1                                                                           
 LARGEST CORRECTION TO DISP.        1.296E-03   AT NODE        363   DOF  1
   INSTANCE: BAR-1                                                                           
          FORCE     EQUILIBRIUM NOT ACHIEVED WITHIN TOLERANCE.
 
	SYMMETRIC NEW DIRECT SPARSE SOLVER RUNNING ON
 	1 HOST x 1 MPI RANK PER HOST x 1 THREAD PER RANK
        NUMBER OF EQUATIONS:  1575
        NUMBER OF RHS:        1
        NUMBER OF FLOPS:      2.825e+07
        SOLVER ELAPSED TIME:  7ms

               CONVERGENCE CHECKS FOR EQUILIBRIUM ITERATION     2


 AVERAGE FORCE                       8.44       TIME AVG. FORCE        7.46    
 LARGEST SCALED RESIDUAL FORCE      1.068E-03   AT NODE        488   DOF  1
   INSTANCE: BAR-1                                                                           
  CORRESPONDING RESIDUAL FORCE      1.068E-03
 LARGEST INCREMENT OF DISP.         5.000E-02   AT NODE          1   DOF  1
   INSTANCE: BAR-1                                                                           
 LARGEST CORRECTION TO DISP.        7.141E-05   AT NODE        388   DOF  1
   INSTANCE: BAR-1                                                                           
          THE FORCE     EQUILIBRIUM EQUATIONS HAVE CONVERGED

 ITERATION SUMMARY FOR THE INCREMENT:   2 TOTAL ITERATIONS, OF WHICH
   0 ARE SEVERE DISCONTINUITY ITERATIONS AND  2 ARE EQUILIBRIUM ITERATIONS.

 TIME INCREMENT COMPLETED  0.100    ,  FRACTION OF STEP COMPLETED  0.700    
 STEP TIME COMPLETED       0.700    ,  TOTAL TIME COMPLETED        0.700    


  INCREMENT     8 STARTS. ATTEMPT NUMBER  1, TIME INCREMENT  0.100    
 
	SYMMETRIC NEW DIRECT SPARSE SOLVER RUNNING ON
 	1 HOST x 1 MPI RANK PER HOST x 1 THREAD PER RANK
        NUMBER OF EQUATIONS:  1575
        NUMBER OF RHS:        1
        NUMBER OF FLOPS:      2.825e+07
        SOLVER ELAPSED TIME:  7ms

               CONVERGENCE CHECKS FOR EQUILIBRIUM ITERATION     1


 AVERAGE FORCE                       8.04       TIME AVG. FORCE        7.53    
 LARGEST SCALED RESIDUAL FORCE      3.468E-02   AT NODE        488   DOF  1
   INSTANCE: BAR-1                                                                           
  CORRESPONDING RESIDUAL FORCE      3.468E-02
 LARGEST INCREMENT OF DISP.         5.000E-02   AT NODE          1   DOF  1
   INSTANCE: BAR-1                                                                           
 LARGEST CORRECTION TO DISP.        5.151E-04   AT NODE        388   DOF  1
   INSTANCE: BAR-1                                                                           
 ESTIMATE OF DISP.    CORRECTION    1.872E-05
 FORCE     EQUILIB. ACCEPTED BASED ON SMALL RESIDUAL AND ESTIMATED CORRECTION

 ITERATION SUMMARY FOR THE INCREMENT:   1 TOTAL ITERATIONS, OF WHICH
   0 ARE SEVERE DISCONTINUITY ITERATIONS AND  1 ARE EQUILIBRIUM ITERATIONS.

 TIME INCREMENT COMPLETED  0.100    ,  FRACTION OF STEP COMPLETED  0.800    
 STEP TIME COMPLETED       0.800    ,  TOTAL TIME COMPLETED        0.800    


  INCREMENT     9 STARTS. ATTEMPT NUMBER  1, TIME INCREMENT  0.100    
 
	SYMMETRIC NEW DIRECT SPARSE SOLVER RUNNING ON
 	1 HOST x 1 MPI RANK PER HOST x 1 THREAD PER RANK
        NUMBER OF EQUATIONS:  1575
        NUMBER OF RHS:        1
        NUMBER OF FLOPS:      2.825e+07
        SOLVER ELAPSED TIME:  6ms

               CONVERGENCE CHECKS FOR EQUILIBRIUM ITERATION     1


 AVERAGE FORCE                       8.02       TIME AVG. FORCE        7.59    
 LARGEST SCALED RESIDUAL FORCE      8.441E-03   AT NODE        488   DOF  1
   INSTANCE: BAR-1                                                                           
  CORRESPONDING RESIDUAL FORCE      8.441E-03
 LARGEST INCREMENT OF DISP.         5.000E-02   AT NODE          1   DOF  1
   INSTANCE: BAR-1                                                                           
 LARGEST CORRECTION TO DISP.        1.495E-04   AT NODE        413   DOF  1
   INSTANCE: BAR-1                                                                           
          THE FORCE     EQUILIBRIUM EQUATIONS HAVE CONVERGED

 ITERATION SUMMARY FOR THE INCREMENT:   1 TOTAL ITERATIONS, OF WHICH
   0 ARE SEVERE DISCONTINUITY ITERATIONS AND  1 ARE EQUILIBRIUM ITERATIONS.

 TIME INCREMENT COMPLETED  0.100    ,  FRACTION OF STEP COMPLETED  0.900    
 STEP TIME COMPLETED       0.900    ,  TOTAL TIME COMPLETED        0.900    


  INCREMENT    10 STARTS. ATTEMPT NUMBER  1, TIME INCREMENT  0.100    
 
	SYMMETRIC NEW DIRECT SPARSE SOLVER RUNNING ON
 	1 HOST x 1 MPI RANK PER HOST x 1 THREAD PER RANK
        NUMBER OF EQUATIONS:  1575
        NUMBER OF RHS:        1
        NUMBER OF FLOPS:      2.825e+07
        SOLVER ELAPSED TIME:  6ms

               CONVERGENCE CHECKS FOR EQUILIBRIUM ITERATION     1


 AVERAGE FORCE                       8.05       TIME AVG. FORCE        7.63    
 LARGEST SCALED RESIDUAL FORCE     -1.495E-02   AT NODE        458   DOF  3
   INSTANCE: BAR-1                                                                           
  CORRESPONDING RESIDUAL FORCE     -1.495E-02
 LARGEST INCREMENT OF DISP.         5.000E-02   AT NODE          1   DOF  1
   INSTANCE: BAR-1                                                                           
 LARGEST CORRECTION TO DISP.        3.181E-04   AT NODE        413   DOF  1
   INSTANCE: BAR-1                                                                           
          THE FORCE     EQUILIBRIUM EQUATIONS HAVE CONVERGED

 ITERATION SUMMARY FOR THE INCREMENT:   1 TOTAL ITERATIONS, OF WHICH
   0 ARE SEVERE DISCONTINUITY ITERATIONS AND  1 ARE EQUILIBRIUM ITERATIONS.

 TIME INCREMENT COMPLETED  0.100    ,  FRACTION OF STEP COMPLETED   1.00    
 STEP TIME COMPLETED        1.00    ,  TOTAL TIME COMPLETED         1.00    


          THE ANALYSIS HAS BEEN COMPLETED



     ANALYSIS SUMMARY:
     TOTAL OF         10  INCREMENTS
                       0  CUTBACKS IN AUTOMATIC INCREMENTATION
                      22  ITERATIONS INCLUDING CONTACT ITERATIONS IF PRESENT
                      22  PASSES THROUGH THE EQUATION SOLVER OF WHICH 
                      22  INVOLVE MATRIX DECOMPOSITION, INCLUDING
                       0  DECOMPOSITION(S) OF THE MASS MATRIX
                       1  REORDERING OF EQUATIONS TO MINIMIZE WAVEFRONT
                       0  ADDITIONAL RESIDUAL EVALUATIONS FOR LINE SEARCHES
                       0  ADDITIONAL OPERATOR EVALUATIONS FOR LINE SEARCHES
                       6  WARNING MESSAGES DURING USER INPUT PROCESSING
                       0  WARNING MESSAGES DURING ANALYSIS
                       0  ANALYSIS WARNINGS ARE NUMERICAL PROBLEM MESSAGES
                       0  ANALYSIS WARNINGS ARE NEGATIVE EIGENVALUE MESSAGES
                       0  ERROR MESSAGES



     JOB TIME SUMMARY
       USER TIME (SEC)      =     0.60    
       SYSTEM TIME (SEC)    =      0.0    
       TOTAL CPU TIME (SEC) =     0.60    
       WALLCLOCK TIME (SEC) =            2
       MEMORY PEAK (GB)     =            0
