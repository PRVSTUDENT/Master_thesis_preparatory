1

   Abaqus 2024                                  Date 06-May-2026   Time 11:08:31
   For use by Supplied by Team-SolidSQUAD under license from Dassault Systemes or its subsidiary.

 Chaboche Unified Viscoplastic UMAT - 1 Cycle Validation Test                    
                                                                                 
 STEP    1     INCREMENT     1     STEP TIME    0.00    


                        S T E P       1     S T A T I C   A N A L Y S I S


                                                                                          

     AUTOMATIC TIME CONTROL WITH -
          A SUGGESTED INITIAL TIME INCREMENT OF                1.000E-03
          AND A TOTAL TIME PERIOD OF                            1.00    
          THE MINIMUM TIME INCREMENT ALLOWED IS                1.000E-08
          THE MAXIMUM TIME INCREMENT ALLOWED IS                5.000E-02

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

     CHARACTERISTIC ELEMENT LENGTH      4.67    

     DETAILS REGARDING ACTUAL SOLUTION WAVEFRONT REQUESTED

     DETAILED OUTPUT OF DIAGNOSTICS TO DATABASE REQUESTED

     PRINT OF INCREMENT NUMBER, TIME, ETC., TO THE MESSAGE FILE EVERY     1  INCREMENTS

     COLLECTING MODEL CONSTRAINT INFORMATION FOR OVERCONSTRAINT CHECKS

     COLLECTING STEP CONSTRAINT INFORMATION FOR OVERCONSTRAINT CHECKS


  INCREMENT     1 STARTS. ATTEMPT NUMBER  1, TIME INCREMENT  1.000E-03
 
	SYMMETRIC NEW DIRECT SPARSE SOLVER RUNNING ON
 	1 HOST x 1 MPI RANK PER HOST x 1 THREAD PER RANK
        NUMBER OF EQUATIONS:  24
        NUMBER OF RHS:        1
        NUMBER OF FLOPS:      4.900e+03
        SOLVER ELAPSED TIME:  24ms

 ***WARNING: SOLVER PROBLEM.  ZERO PIVOT WHEN PROCESSING NODE 8 INSTANCE 
             BLOCK_INST D.O.F. 2
  Typically a zero pivot is associated with an overconstraint in the model. 
 However, Abaqus was not able to identify any chains of constraints that might 
 lead to an overconstraint at this node. This suggests that the model might be 
 in fact insufficiently constrained in this particular degree of freedom. 
 Please check the constraints used in this model. 


 ***WARNING: SOLVER PROBLEM.  ZERO PIVOT WHEN PROCESSING NODE 8 INSTANCE 
             BLOCK_INST D.O.F. 3
  Typically a zero pivot is associated with an overconstraint in the model. 
 However, Abaqus was not able to identify any chains of constraints that might 
 lead to an overconstraint at this node. This suggests that the model might be 
 in fact insufficiently constrained in this particular degree of freedom. 
 Please check the constraints used in this model. 


 ***WARNING: SOLVER PROBLEM.  ZERO PIVOT WHEN PROCESSING NODE 3 INSTANCE 
             BLOCK_INST D.O.F. 2
  Typically a zero pivot is associated with an overconstraint in the model. 
 However, Abaqus was not able to identify any chains of constraints that might 
 lead to an overconstraint at this node. This suggests that the model might be 
 in fact insufficiently constrained in this particular degree of freedom. 
 Please check the constraints used in this model. 


 ***WARNING: SOLVER PROBLEM.  ZERO PIVOT WHEN PROCESSING NODE 3 INSTANCE 
             BLOCK_INST D.O.F. 3
  Typically a zero pivot is associated with an overconstraint in the model. 
 However, Abaqus was not able to identify any chains of constraints that might 
 lead to an overconstraint at this node. This suggests that the model might be 
 in fact insufficiently constrained in this particular degree of freedom. 
 Please check the constraints used in this model. 


 ***WARNING: SOLVER PROBLEM.  ZERO PIVOT WHEN PROCESSING NODE 4 INSTANCE 
             BLOCK_INST D.O.F. 2
  Typically a zero pivot is associated with an overconstraint in the model. 
 However, Abaqus was not able to identify any chains of constraints that might 
 lead to an overconstraint at this node. This suggests that the model might be 
 in fact insufficiently constrained in this particular degree of freedom. 
 Please check the constraints used in this model. 


 ***WARNING: SOLVER PROBLEM.  ZERO PIVOT WHEN PROCESSING NODE 6 INSTANCE 
             BLOCK_INST D.O.F. 2
  Typically a zero pivot is associated with an overconstraint in the model. 
 However, Abaqus was not able to identify any chains of constraints that might 
 lead to an overconstraint at this node. This suggests that the model might be 
 in fact insufficiently constrained in this particular degree of freedom. 
 Please check the constraints used in this model. 


 ***WARNING: SOLVER PROBLEM.  ZERO PIVOT WHEN PROCESSING NODE 6 INSTANCE 
             BLOCK_INST D.O.F. 3
  Typically a zero pivot is associated with an overconstraint in the model. 
 However, Abaqus was not able to identify any chains of constraints that might 
 lead to an overconstraint at this node. This suggests that the model might be 
 in fact insufficiently constrained in this particular degree of freedom. 
 Please check the constraints used in this model. 


 ***WARNING: SOLVER PROBLEM.  ZERO PIVOT WHEN PROCESSING NODE 2 INSTANCE 
             BLOCK_INST D.O.F. 2
  Typically a zero pivot is associated with an overconstraint in the model. 
 However, Abaqus was not able to identify any chains of constraints that might 
 lead to an overconstraint at this node. This suggests that the model might be 
 in fact insufficiently constrained in this particular degree of freedom. 
 Please check the constraints used in this model. 


 ***WARNING: SOLVER PROBLEM.  ZERO PIVOT WHEN PROCESSING NODE 2 INSTANCE 
             BLOCK_INST D.O.F. 3
  Typically a zero pivot is associated with an overconstraint in the model. 
 However, Abaqus was not able to identify any chains of constraints that might 
 lead to an overconstraint at this node. This suggests that the model might be 
 in fact insufficiently constrained in this particular degree of freedom. 
 Please check the constraints used in this model. 


 ***WARNING: SOLVER PROBLEM.  ZERO PIVOT WHEN PROCESSING NODE 5 INSTANCE 
             BLOCK_INST D.O.F. 2
  Typically a zero pivot is associated with an overconstraint in the model. 
 However, Abaqus was not able to identify any chains of constraints that might 
 lead to an overconstraint at this node. This suggests that the model might be 
 in fact insufficiently constrained in this particular degree of freedom. 
 Please check the constraints used in this model. 


 ***WARNING: SOLVER PROBLEM.  ZERO PIVOT WHEN PROCESSING NODE 5 INSTANCE 
             BLOCK_INST D.O.F. 3
  Typically a zero pivot is associated with an overconstraint in the model. 
 However, Abaqus was not able to identify any chains of constraints that might 
 lead to an overconstraint at this node. This suggests that the model might be 
 in fact insufficiently constrained in this particular degree of freedom. 
 Please check the constraints used in this model. 


 ***WARNING: SOLVER PROBLEM.  ZERO PIVOT WHEN PROCESSING NODE 7 INSTANCE 
             BLOCK_INST D.O.F. 2
  Typically a zero pivot is associated with an overconstraint in the model. 
 However, Abaqus was not able to identify any chains of constraints that might 
 lead to an overconstraint at this node. This suggests that the model might be 
 in fact insufficiently constrained in this particular degree of freedom. 
 Please check the constraints used in this model. 


 ***WARNING: SOLVER PROBLEM.  ZERO PIVOT WHEN PROCESSING NODE 7 INSTANCE 
             BLOCK_INST D.O.F. 3
  Typically a zero pivot is associated with an overconstraint in the model. 
 However, Abaqus was not able to identify any chains of constraints that might 
 lead to an overconstraint at this node. This suggests that the model might be 
 in fact insufficiently constrained in this particular degree of freedom. 
 Please check the constraints used in this model. 


 ***WARNING: Solver problem. Zero pivot when processing D.O.F. 2 of 7 nodes. 
             The nodes have been identified in node set 
             WarnNodeSolvProbZeroPiv_2_1_1_1_1.

 ***WARNING: Solver problem. Zero pivot when processing D.O.F. 3 of 6 nodes. 
             The nodes have been identified in node set 
             WarnNodeSolvProbZeroPiv_3_1_1_1_1.

               CONVERGENCE CHECKS FOR EQUILIBRIUM ITERATION     1


 AVERAGE FORCE                       0.00       TIME AVG. FORCE       1.000E-02
 ALL FORCE     RESIDUALS ARE ZERO
 LARGEST INCREMENT OF DISP.         5.000E-04   AT NODE          2   DOF  1
   INSTANCE: BLOCK_INST                                                                      
 LARGEST CORRECTION TO DISP.        5.000E-04   AT NODE          2   DOF  1
   INSTANCE: BLOCK_INST                                                                      
          THERE IS ZERO FORCE     EVERYWHERE

 ITERATION SUMMARY FOR THE INCREMENT:   1 TOTAL ITERATIONS, OF WHICH
   0 ARE SEVERE DISCONTINUITY ITERATIONS AND  1 ARE EQUILIBRIUM ITERATIONS.

 TIME INCREMENT COMPLETED  1.000E-03,  FRACTION OF STEP COMPLETED  1.000E-03
 STEP TIME COMPLETED       1.000E-03,  TOTAL TIME COMPLETED        1.000E-03


  INCREMENT     2 STARTS. ATTEMPT NUMBER  1, TIME INCREMENT  1.000E-03
 
	SYMMETRIC NEW DIRECT SPARSE SOLVER RUNNING ON
 	1 HOST x 1 MPI RANK PER HOST x 1 THREAD PER RANK
        NUMBER OF EQUATIONS:  24
        NUMBER OF RHS:        1
        NUMBER OF FLOPS:      4.900e+03
        SOLVER ELAPSED TIME:  1ms

               CONVERGENCE CHECKS FOR EQUILIBRIUM ITERATION     1


 AVERAGE FORCE                      3.183-318   TIME AVG. FORCE       1.000E-02
 LARGEST SCALED RESIDUAL FORCE      9.881-324   AT NODE          2   DOF  2
   INSTANCE: BLOCK_INST                                                                      
  CORRESPONDING RESIDUAL FORCE      9.881-324
 LARGEST INCREMENT OF DISP.         5.000E-04   AT NODE          2   DOF  1
   INSTANCE: BLOCK_INST                                                                      
 LARGEST CORRECTION TO DISP.        9.881-288   AT NODE          2   DOF  2
   INSTANCE: BLOCK_INST                                                                      
          THERE IS ZERO FORCE     EVERYWHERE
 

 ***WARNING: THERE IS ZERO FORCE EVERYWHERE IN THE MODEL BASED ON THE DEFAULT 
             CRITERION. PLEASE CHECK THE VALUE OF THE AVERAGE FORCE DURING THE 
             CURRENT ITERATION TO VERIFY THAT THE FORCE IS SMALL ENOUGH TO BE 
             TREATED AS ZERO. IF NOT, PLEASE USE THE SOLUTION CONTROLS TO RESET 
             THE CRITERION FOR ZERO FORCE.
          TIME INCREMENT MAY NOW INCREASE TO    1.500E-03

 ITERATION SUMMARY FOR THE INCREMENT:   1 TOTAL ITERATIONS, OF WHICH
   0 ARE SEVERE DISCONTINUITY ITERATIONS AND  1 ARE EQUILIBRIUM ITERATIONS.

 TIME INCREMENT COMPLETED  1.000E-03,  FRACTION OF STEP COMPLETED  2.000E-03
 STEP TIME COMPLETED       2.000E-03,  TOTAL TIME COMPLETED        2.000E-03


  INCREMENT     3 STARTS. ATTEMPT NUMBER  1, TIME INCREMENT  1.500E-03
 
	SYMMETRIC NEW DIRECT SPARSE SOLVER RUNNING ON
 	1 HOST x 1 MPI RANK PER HOST x 1 THREAD PER RANK
        NUMBER OF EQUATIONS:  24
        NUMBER OF RHS:        1
        NUMBER OF FLOPS:      4.900e+03
        SOLVER ELAPSED TIME:  0ms

               CONVERGENCE CHECKS FOR EQUILIBRIUM ITERATION     1


 AVERAGE FORCE                      9.549-318   TIME AVG. FORCE       1.000E-02
 LARGEST SCALED RESIDUAL FORCE     -9.881-324   AT NODE          2   DOF  2
   INSTANCE: BLOCK_INST                                                                      
  CORRESPONDING RESIDUAL FORCE     -9.881-324
 LARGEST INCREMENT OF DISP.         7.500E-04   AT NODE          2   DOF  1
   INSTANCE: BLOCK_INST                                                                      
 LARGEST CORRECTION TO DISP.       -2.168E-19   AT NODE          2   DOF  1
   INSTANCE: BLOCK_INST                                                                      
          THERE IS ZERO FORCE     EVERYWHERE
 

 ***WARNING: THERE IS ZERO FORCE EVERYWHERE IN THE MODEL BASED ON THE DEFAULT 
             CRITERION. PLEASE CHECK THE VALUE OF THE AVERAGE FORCE DURING THE 
             CURRENT ITERATION TO VERIFY THAT THE FORCE IS SMALL ENOUGH TO BE 
             TREATED AS ZERO. IF NOT, PLEASE USE THE SOLUTION CONTROLS TO RESET 
             THE CRITERION FOR ZERO FORCE.
          TIME INCREMENT MAY NOW INCREASE TO    2.250E-03

 ITERATION SUMMARY FOR THE INCREMENT:   1 TOTAL ITERATIONS, OF WHICH
   0 ARE SEVERE DISCONTINUITY ITERATIONS AND  1 ARE EQUILIBRIUM ITERATIONS.

 TIME INCREMENT COMPLETED  1.500E-03,  FRACTION OF STEP COMPLETED  3.500E-03
 STEP TIME COMPLETED       3.500E-03,  TOTAL TIME COMPLETED        3.500E-03


  INCREMENT     4 STARTS. ATTEMPT NUMBER  1, TIME INCREMENT  2.250E-03
 
	SYMMETRIC NEW DIRECT SPARSE SOLVER RUNNING ON
 	1 HOST x 1 MPI RANK PER HOST x 1 THREAD PER RANK
        NUMBER OF EQUATIONS:  24
        NUMBER OF RHS:        1
        NUMBER OF FLOPS:      4.900e+03
        SOLVER ELAPSED TIME:  1ms

               CONVERGENCE CHECKS FOR EQUILIBRIUM ITERATION     1


 AVERAGE FORCE                      2.069-317   TIME AVG. FORCE       1.000E-02
 LARGEST SCALED RESIDUAL FORCE       0.00       AT NODE          2   DOF  2
   INSTANCE: BLOCK_INST                                                                      
  CORRESPONDING RESIDUAL FORCE       0.00    
 LARGEST INCREMENT OF DISP.         1.125E-03   AT NODE          2   DOF  1
   INSTANCE: BLOCK_INST                                                                      
 LARGEST CORRECTION TO DISP.       -2.168E-19   AT NODE          2   DOF  1
   INSTANCE: BLOCK_INST                                                                      
          THERE IS ZERO FORCE     EVERYWHERE
 

 ***WARNING: THERE IS ZERO FORCE EVERYWHERE IN THE MODEL BASED ON THE DEFAULT 
             CRITERION. PLEASE CHECK THE VALUE OF THE AVERAGE FORCE DURING THE 
             CURRENT ITERATION TO VERIFY THAT THE FORCE IS SMALL ENOUGH TO BE 
             TREATED AS ZERO. IF NOT, PLEASE USE THE SOLUTION CONTROLS TO RESET 
             THE CRITERION FOR ZERO FORCE.
          TIME INCREMENT MAY NOW INCREASE TO    3.375E-03

 ITERATION SUMMARY FOR THE INCREMENT:   1 TOTAL ITERATIONS, OF WHICH
   0 ARE SEVERE DISCONTINUITY ITERATIONS AND  1 ARE EQUILIBRIUM ITERATIONS.

 TIME INCREMENT COMPLETED  2.250E-03,  FRACTION OF STEP COMPLETED  5.750E-03
 STEP TIME COMPLETED       5.750E-03,  TOTAL TIME COMPLETED        5.750E-03


  INCREMENT     5 STARTS. ATTEMPT NUMBER  1, TIME INCREMENT  3.375E-03
 
	SYMMETRIC NEW DIRECT SPARSE SOLVER RUNNING ON
 	1 HOST x 1 MPI RANK PER HOST x 1 THREAD PER RANK
        NUMBER OF EQUATIONS:  24
        NUMBER OF RHS:        1
        NUMBER OF FLOPS:      4.900e+03
        SOLVER ELAPSED TIME:  0ms

               CONVERGENCE CHECKS FOR EQUILIBRIUM ITERATION     1


 AVERAGE FORCE                      3.899-317   TIME AVG. FORCE       1.000E-02
 LARGEST SCALED RESIDUAL FORCE       0.00       AT NODE          2   DOF  2
   INSTANCE: BLOCK_INST                                                                      
  CORRESPONDING RESIDUAL FORCE       0.00    
 LARGEST INCREMENT OF DISP.         1.688E-03   AT NODE          2   DOF  1
   INSTANCE: BLOCK_INST                                                                      
 LARGEST CORRECTION TO DISP.        1.518E-18   AT NODE          2   DOF  1
   INSTANCE: BLOCK_INST                                                                      
          THERE IS ZERO FORCE     EVERYWHERE
 

 ***WARNING: THERE IS ZERO FORCE EVERYWHERE IN THE MODEL BASED ON THE DEFAULT 
             CRITERION. PLEASE CHECK THE VALUE OF THE AVERAGE FORCE DURING THE 
             CURRENT ITERATION TO VERIFY THAT THE FORCE IS SMALL ENOUGH TO BE 
             TREATED AS ZERO. IF NOT, PLEASE USE THE SOLUTION CONTROLS TO RESET 
             THE CRITERION FOR ZERO FORCE.
          TIME INCREMENT MAY NOW INCREASE TO    5.063E-03

 ITERATION SUMMARY FOR THE INCREMENT:   1 TOTAL ITERATIONS, OF WHICH
   0 ARE SEVERE DISCONTINUITY ITERATIONS AND  1 ARE EQUILIBRIUM ITERATIONS.

 TIME INCREMENT COMPLETED  3.375E-03,  FRACTION OF STEP COMPLETED  9.125E-03
 STEP TIME COMPLETED       9.125E-03,  TOTAL TIME COMPLETED        9.125E-03


  INCREMENT     6 STARTS. ATTEMPT NUMBER  1, TIME INCREMENT  5.063E-03
 
	SYMMETRIC NEW DIRECT SPARSE SOLVER RUNNING ON
 	1 HOST x 1 MPI RANK PER HOST x 1 THREAD PER RANK
        NUMBER OF EQUATIONS:  24
        NUMBER OF RHS:        1
        NUMBER OF FLOPS:      4.900e+03
        SOLVER ELAPSED TIME:  0ms

               CONVERGENCE CHECKS FOR EQUILIBRIUM ITERATION     1


 AVERAGE FORCE                      6.804-317   TIME AVG. FORCE       1.000E-02
 LARGEST SCALED RESIDUAL FORCE      9.881-324   AT NODE          2   DOF  2
   INSTANCE: BLOCK_INST                                                                      
  CORRESPONDING RESIDUAL FORCE      9.881-324
 LARGEST INCREMENT OF DISP.         2.531E-03   AT NODE          2   DOF  1
   INSTANCE: BLOCK_INST                                                                      
 LARGEST CORRECTION TO DISP.       -1.301E-18   AT NODE          2   DOF  1
   INSTANCE: BLOCK_INST                                                                      
          THERE IS ZERO FORCE     EVERYWHERE
 

 ***WARNING: THERE IS ZERO FORCE EVERYWHERE IN THE MODEL BASED ON THE DEFAULT 
             CRITERION. PLEASE CHECK THE VALUE OF THE AVERAGE FORCE DURING THE 
             CURRENT ITERATION TO VERIFY THAT THE FORCE IS SMALL ENOUGH TO BE 
             TREATED AS ZERO. IF NOT, PLEASE USE THE SOLUTION CONTROLS TO RESET 
             THE CRITERION FOR ZERO FORCE.
          TIME INCREMENT MAY NOW INCREASE TO    7.594E-03

 ITERATION SUMMARY FOR THE INCREMENT:   1 TOTAL ITERATIONS, OF WHICH
   0 ARE SEVERE DISCONTINUITY ITERATIONS AND  1 ARE EQUILIBRIUM ITERATIONS.

 TIME INCREMENT COMPLETED  5.063E-03,  FRACTION OF STEP COMPLETED  1.419E-02
 STEP TIME COMPLETED       1.419E-02,  TOTAL TIME COMPLETED        1.419E-02


  INCREMENT     7 STARTS. ATTEMPT NUMBER  1, TIME INCREMENT  7.594E-03
 
	SYMMETRIC NEW DIRECT SPARSE SOLVER RUNNING ON
 	1 HOST x 1 MPI RANK PER HOST x 1 THREAD PER RANK
        NUMBER OF EQUATIONS:  24
        NUMBER OF RHS:        1
        NUMBER OF FLOPS:      4.900e+03
        SOLVER ELAPSED TIME:  1ms

               CONVERGENCE CHECKS FOR EQUILIBRIUM ITERATION     1


 AVERAGE FORCE                      1.132-316   TIME AVG. FORCE       1.000E-02
 LARGEST SCALED RESIDUAL FORCE      9.881-324   AT NODE          2   DOF  2
   INSTANCE: BLOCK_INST                                                                      
  CORRESPONDING RESIDUAL FORCE      9.881-324
 LARGEST INCREMENT OF DISP.         3.797E-03   AT NODE          2   DOF  1
   INSTANCE: BLOCK_INST                                                                      
 LARGEST CORRECTION TO DISP.        8.674E-19   AT NODE          2   DOF  1
   INSTANCE: BLOCK_INST                                                                      
          THERE IS ZERO FORCE     EVERYWHERE
 

 ***WARNING: THERE IS ZERO FORCE EVERYWHERE IN THE MODEL BASED ON THE DEFAULT 
             CRITERION. PLEASE CHECK THE VALUE OF THE AVERAGE FORCE DURING THE 
             CURRENT ITERATION TO VERIFY THAT THE FORCE IS SMALL ENOUGH TO BE 
             TREATED AS ZERO. IF NOT, PLEASE USE THE SOLUTION CONTROLS TO RESET 
             THE CRITERION FOR ZERO FORCE.
          TIME INCREMENT MAY NOW INCREASE TO    1.139E-02

 ITERATION SUMMARY FOR THE INCREMENT:   1 TOTAL ITERATIONS, OF WHICH
   0 ARE SEVERE DISCONTINUITY ITERATIONS AND  1 ARE EQUILIBRIUM ITERATIONS.

 TIME INCREMENT COMPLETED  7.594E-03,  FRACTION OF STEP COMPLETED  2.178E-02
 STEP TIME COMPLETED       2.178E-02,  TOTAL TIME COMPLETED        2.178E-02


  INCREMENT     8 STARTS. ATTEMPT NUMBER  1, TIME INCREMENT  1.139E-02
 
	SYMMETRIC NEW DIRECT SPARSE SOLVER RUNNING ON
 	1 HOST x 1 MPI RANK PER HOST x 1 THREAD PER RANK
        NUMBER OF EQUATIONS:  24
        NUMBER OF RHS:        1
        NUMBER OF FLOPS:      4.900e+03
        SOLVER ELAPSED TIME:  0ms

               CONVERGENCE CHECKS FOR EQUILIBRIUM ITERATION     1


 AVERAGE FORCE                      1.825-316   TIME AVG. FORCE       1.000E-02
 LARGEST SCALED RESIDUAL FORCE      9.881-324   AT NODE          2   DOF  2
   INSTANCE: BLOCK_INST                                                                      
  CORRESPONDING RESIDUAL FORCE      9.881-324
 LARGEST INCREMENT OF DISP.         5.695E-03   AT NODE          2   DOF  1
   INSTANCE: BLOCK_INST                                                                      
 LARGEST CORRECTION TO DISP.        8.674E-19   AT NODE          2   DOF  1
   INSTANCE: BLOCK_INST                                                                      
          THERE IS ZERO FORCE     EVERYWHERE
 

 ***WARNING: THERE IS ZERO FORCE EVERYWHERE IN THE MODEL BASED ON THE DEFAULT 
             CRITERION. PLEASE CHECK THE VALUE OF THE AVERAGE FORCE DURING THE 
             CURRENT ITERATION TO VERIFY THAT THE FORCE IS SMALL ENOUGH TO BE 
             TREATED AS ZERO. IF NOT, PLEASE USE THE SOLUTION CONTROLS TO RESET 
             THE CRITERION FOR ZERO FORCE.
          TIME INCREMENT MAY NOW INCREASE TO    1.709E-02

 ITERATION SUMMARY FOR THE INCREMENT:   1 TOTAL ITERATIONS, OF WHICH
   0 ARE SEVERE DISCONTINUITY ITERATIONS AND  1 ARE EQUILIBRIUM ITERATIONS.

 TIME INCREMENT COMPLETED  1.139E-02,  FRACTION OF STEP COMPLETED  3.317E-02
 STEP TIME COMPLETED       3.317E-02,  TOTAL TIME COMPLETED        3.317E-02


  INCREMENT     9 STARTS. ATTEMPT NUMBER  1, TIME INCREMENT  1.709E-02
 
	SYMMETRIC NEW DIRECT SPARSE SOLVER RUNNING ON
 	1 HOST x 1 MPI RANK PER HOST x 1 THREAD PER RANK
        NUMBER OF EQUATIONS:  24
        NUMBER OF RHS:        1
        NUMBER OF FLOPS:      4.900e+03
        SOLVER ELAPSED TIME:  1ms

               CONVERGENCE CHECKS FOR EQUILIBRIUM ITERATION     1


 AVERAGE FORCE                      2.881-316   TIME AVG. FORCE       1.000E-02
 LARGEST SCALED RESIDUAL FORCE     -9.881-324   AT NODE          2   DOF  2
   INSTANCE: BLOCK_INST                                                                      
  CORRESPONDING RESIDUAL FORCE     -9.881-324
 LARGEST INCREMENT OF DISP.         8.543E-03   AT NODE          2   DOF  1
   INSTANCE: BLOCK_INST                                                                      
 LARGEST CORRECTION TO DISP.       -9.881-288   AT NODE          2   DOF  2
   INSTANCE: BLOCK_INST                                                                      
          THERE IS ZERO FORCE     EVERYWHERE
 

 ***WARNING: THERE IS ZERO FORCE EVERYWHERE IN THE MODEL BASED ON THE DEFAULT 
             CRITERION. PLEASE CHECK THE VALUE OF THE AVERAGE FORCE DURING THE 
             CURRENT ITERATION TO VERIFY THAT THE FORCE IS SMALL ENOUGH TO BE 
             TREATED AS ZERO. IF NOT, PLEASE USE THE SOLUTION CONTROLS TO RESET 
             THE CRITERION FOR ZERO FORCE.
          TIME INCREMENT MAY NOW INCREASE TO    2.563E-02

 ITERATION SUMMARY FOR THE INCREMENT:   1 TOTAL ITERATIONS, OF WHICH
   0 ARE SEVERE DISCONTINUITY ITERATIONS AND  1 ARE EQUILIBRIUM ITERATIONS.

 TIME INCREMENT COMPLETED  1.709E-02,  FRACTION OF STEP COMPLETED  5.026E-02
 STEP TIME COMPLETED       5.026E-02,  TOTAL TIME COMPLETED        5.026E-02


  INCREMENT    10 STARTS. ATTEMPT NUMBER  1, TIME INCREMENT  2.563E-02
 
	SYMMETRIC NEW DIRECT SPARSE SOLVER RUNNING ON
 	1 HOST x 1 MPI RANK PER HOST x 1 THREAD PER RANK
        NUMBER OF EQUATIONS:  24
        NUMBER OF RHS:        1
        NUMBER OF FLOPS:      4.900e+03
        SOLVER ELAPSED TIME:  1ms

               CONVERGENCE CHECKS FOR EQUILIBRIUM ITERATION     1


 AVERAGE FORCE                      4.481-316   TIME AVG. FORCE       1.000E-02
 LARGEST SCALED RESIDUAL FORCE       0.00       AT NODE          2   DOF  2
   INSTANCE: BLOCK_INST                                                                      
  CORRESPONDING RESIDUAL FORCE       0.00    
 LARGEST INCREMENT OF DISP.         1.281E-02   AT NODE          2   DOF  1
   INSTANCE: BLOCK_INST                                                                      
 LARGEST CORRECTION TO DISP.       -1.041E-17   AT NODE          2   DOF  1
   INSTANCE: BLOCK_INST                                                                      
          THERE IS ZERO FORCE     EVERYWHERE
 

 ***WARNING: THERE IS ZERO FORCE EVERYWHERE IN THE MODEL BASED ON THE DEFAULT 
             CRITERION. PLEASE CHECK THE VALUE OF THE AVERAGE FORCE DURING THE 
             CURRENT ITERATION TO VERIFY THAT THE FORCE IS SMALL ENOUGH TO BE 
             TREATED AS ZERO. IF NOT, PLEASE USE THE SOLUTION CONTROLS TO RESET 
             THE CRITERION FOR ZERO FORCE.
          TIME INCREMENT MAY NOW INCREASE TO    3.844E-02

 ITERATION SUMMARY FOR THE INCREMENT:   1 TOTAL ITERATIONS, OF WHICH
   0 ARE SEVERE DISCONTINUITY ITERATIONS AND  1 ARE EQUILIBRIUM ITERATIONS.

 TIME INCREMENT COMPLETED  2.563E-02,  FRACTION OF STEP COMPLETED  7.589E-02
 STEP TIME COMPLETED       7.589E-02,  TOTAL TIME COMPLETED        7.589E-02


  INCREMENT    11 STARTS. ATTEMPT NUMBER  1, TIME INCREMENT  3.844E-02
 
	SYMMETRIC NEW DIRECT SPARSE SOLVER RUNNING ON
 	1 HOST x 1 MPI RANK PER HOST x 1 THREAD PER RANK
        NUMBER OF EQUATIONS:  24
        NUMBER OF RHS:        1
        NUMBER OF FLOPS:      4.900e+03
        SOLVER ELAPSED TIME:  0ms

               CONVERGENCE CHECKS FOR EQUILIBRIUM ITERATION     1


 AVERAGE FORCE                      6.896-316   TIME AVG. FORCE       1.000E-02
 LARGEST SCALED RESIDUAL FORCE       0.00       AT NODE          2   DOF  2
   INSTANCE: BLOCK_INST                                                                      
  CORRESPONDING RESIDUAL FORCE       0.00    
 LARGEST INCREMENT OF DISP.         1.922E-02   AT NODE          2   DOF  1
   INSTANCE: BLOCK_INST                                                                      
 LARGEST CORRECTION TO DISP.        6.939E-18   AT NODE          2   DOF  1
   INSTANCE: BLOCK_INST                                                                      
          THERE IS ZERO FORCE     EVERYWHERE
 

 ***WARNING: THERE IS ZERO FORCE EVERYWHERE IN THE MODEL BASED ON THE DEFAULT 
             CRITERION. PLEASE CHECK THE VALUE OF THE AVERAGE FORCE DURING THE 
             CURRENT ITERATION TO VERIFY THAT THE FORCE IS SMALL ENOUGH TO BE 
             TREATED AS ZERO. IF NOT, PLEASE USE THE SOLUTION CONTROLS TO RESET 
             THE CRITERION FOR ZERO FORCE.
          TIME INCREMENT MAY NOW INCREASE TO    5.000E-02

 ITERATION SUMMARY FOR THE INCREMENT:   1 TOTAL ITERATIONS, OF WHICH
   0 ARE SEVERE DISCONTINUITY ITERATIONS AND  1 ARE EQUILIBRIUM ITERATIONS.

 TIME INCREMENT COMPLETED  3.844E-02,  FRACTION OF STEP COMPLETED  0.114    
 STEP TIME COMPLETED       0.114    ,  TOTAL TIME COMPLETED        0.114    


  INCREMENT    12 STARTS. ATTEMPT NUMBER  1, TIME INCREMENT  5.000E-02
 
	SYMMETRIC NEW DIRECT SPARSE SOLVER RUNNING ON
 	1 HOST x 1 MPI RANK PER HOST x 1 THREAD PER RANK
        NUMBER OF EQUATIONS:  24
        NUMBER OF RHS:        1
        NUMBER OF FLOPS:      4.900e+03
        SOLVER ELAPSED TIME:  1ms

               CONVERGENCE CHECKS FOR EQUILIBRIUM ITERATION     1


 AVERAGE FORCE                      1.054-315   TIME AVG. FORCE       1.000E-02
 LARGEST SCALED RESIDUAL FORCE       0.00       AT NODE          2   DOF  2
   INSTANCE: BLOCK_INST                                                                      
  CORRESPONDING RESIDUAL FORCE       0.00    
 LARGEST INCREMENT OF DISP.         2.500E-02   AT NODE          2   DOF  1
   INSTANCE: BLOCK_INST                                                                      
 LARGEST CORRECTION TO DISP.       -1.388E-17   AT NODE          2   DOF  1
   INSTANCE: BLOCK_INST                                                                      
          THERE IS ZERO FORCE     EVERYWHERE
 

 ***WARNING: THERE IS ZERO FORCE EVERYWHERE IN THE MODEL BASED ON THE DEFAULT 
             CRITERION. PLEASE CHECK THE VALUE OF THE AVERAGE FORCE DURING THE 
             CURRENT ITERATION TO VERIFY THAT THE FORCE IS SMALL ENOUGH TO BE 
             TREATED AS ZERO. IF NOT, PLEASE USE THE SOLUTION CONTROLS TO RESET 
             THE CRITERION FOR ZERO FORCE.

 ITERATION SUMMARY FOR THE INCREMENT:   1 TOTAL ITERATIONS, OF WHICH
   0 ARE SEVERE DISCONTINUITY ITERATIONS AND  1 ARE EQUILIBRIUM ITERATIONS.

 TIME INCREMENT COMPLETED  5.000E-02,  FRACTION OF STEP COMPLETED  0.164    
 STEP TIME COMPLETED       0.164    ,  TOTAL TIME COMPLETED        0.164    


  INCREMENT    13 STARTS. ATTEMPT NUMBER  1, TIME INCREMENT  5.000E-02
 
	SYMMETRIC NEW DIRECT SPARSE SOLVER RUNNING ON
 	1 HOST x 1 MPI RANK PER HOST x 1 THREAD PER RANK
        NUMBER OF EQUATIONS:  24
        NUMBER OF RHS:        1
        NUMBER OF FLOPS:      4.900e+03
        SOLVER ELAPSED TIME:  0ms

               CONVERGENCE CHECKS FOR EQUILIBRIUM ITERATION     1


 AVERAGE FORCE                      1.577-315   TIME AVG. FORCE       1.000E-02
 LARGEST SCALED RESIDUAL FORCE       0.00       AT NODE          2   DOF  2
   INSTANCE: BLOCK_INST                                                                      
  CORRESPONDING RESIDUAL FORCE       0.00    
 LARGEST INCREMENT OF DISP.         2.500E-02   AT NODE          2   DOF  1
   INSTANCE: BLOCK_INST                                                                      
 LARGEST CORRECTION TO DISP.        1.388E-17   AT NODE          2   DOF  1
   INSTANCE: BLOCK_INST                                                                      
          THERE IS ZERO FORCE     EVERYWHERE
 

 ***WARNING: THERE IS ZERO FORCE EVERYWHERE IN THE MODEL BASED ON THE DEFAULT 
             CRITERION. PLEASE CHECK THE VALUE OF THE AVERAGE FORCE DURING THE 
             CURRENT ITERATION TO VERIFY THAT THE FORCE IS SMALL ENOUGH TO BE 
             TREATED AS ZERO. IF NOT, PLEASE USE THE SOLUTION CONTROLS TO RESET 
             THE CRITERION FOR ZERO FORCE.

 ITERATION SUMMARY FOR THE INCREMENT:   1 TOTAL ITERATIONS, OF WHICH
   0 ARE SEVERE DISCONTINUITY ITERATIONS AND  1 ARE EQUILIBRIUM ITERATIONS.

 TIME INCREMENT COMPLETED  5.000E-02,  FRACTION OF STEP COMPLETED  0.214    
 STEP TIME COMPLETED       0.214    ,  TOTAL TIME COMPLETED        0.214    


  INCREMENT    14 STARTS. ATTEMPT NUMBER  1, TIME INCREMENT  5.000E-02
 
	SYMMETRIC NEW DIRECT SPARSE SOLVER RUNNING ON
 	1 HOST x 1 MPI RANK PER HOST x 1 THREAD PER RANK
        NUMBER OF EQUATIONS:  24
        NUMBER OF RHS:        1
        NUMBER OF FLOPS:      4.900e+03
        SOLVER ELAPSED TIME:  0ms

               CONVERGENCE CHECKS FOR EQUILIBRIUM ITERATION     1


 AVERAGE FORCE                      2.259-315   TIME AVG. FORCE       1.000E-02
 LARGEST SCALED RESIDUAL FORCE       0.00       AT NODE          2   DOF  2
   INSTANCE: BLOCK_INST                                                                      
  CORRESPONDING RESIDUAL FORCE       0.00    
 LARGEST INCREMENT OF DISP.         2.500E-02   AT NODE          2   DOF  1
   INSTANCE: BLOCK_INST                                                                      
 LARGEST CORRECTION TO DISP.       -1.388E-17   AT NODE          2   DOF  1
   INSTANCE: BLOCK_INST                                                                      
          THERE IS ZERO FORCE     EVERYWHERE
 

 ***WARNING: THERE IS ZERO FORCE EVERYWHERE IN THE MODEL BASED ON THE DEFAULT 
             CRITERION. PLEASE CHECK THE VALUE OF THE AVERAGE FORCE DURING THE 
             CURRENT ITERATION TO VERIFY THAT THE FORCE IS SMALL ENOUGH TO BE 
             TREATED AS ZERO. IF NOT, PLEASE USE THE SOLUTION CONTROLS TO RESET 
             THE CRITERION FOR ZERO FORCE.

 ITERATION SUMMARY FOR THE INCREMENT:   1 TOTAL ITERATIONS, OF WHICH
   0 ARE SEVERE DISCONTINUITY ITERATIONS AND  1 ARE EQUILIBRIUM ITERATIONS.

 TIME INCREMENT COMPLETED  5.000E-02,  FRACTION OF STEP COMPLETED  0.264    
 STEP TIME COMPLETED       0.264    ,  TOTAL TIME COMPLETED        0.264    


  INCREMENT    15 STARTS. ATTEMPT NUMBER  1, TIME INCREMENT  5.000E-02
 
	SYMMETRIC NEW DIRECT SPARSE SOLVER RUNNING ON
 	1 HOST x 1 MPI RANK PER HOST x 1 THREAD PER RANK
        NUMBER OF EQUATIONS:  24
        NUMBER OF RHS:        1
        NUMBER OF FLOPS:      4.900e+03
        SOLVER ELAPSED TIME:  0ms

               CONVERGENCE CHECKS FOR EQUILIBRIUM ITERATION     1


 AVERAGE FORCE                      3.100-315   TIME AVG. FORCE       1.000E-02
 LARGEST SCALED RESIDUAL FORCE      9.881-324   AT NODE          2   DOF  2
   INSTANCE: BLOCK_INST                                                                      
  CORRESPONDING RESIDUAL FORCE      9.881-324
 LARGEST INCREMENT OF DISP.         2.500E-02   AT NODE          2   DOF  1
   INSTANCE: BLOCK_INST                                                                      
 LARGEST CORRECTION TO DISP.        1.388E-17   AT NODE          2   DOF  1
   INSTANCE: BLOCK_INST                                                                      
          THERE IS ZERO FORCE     EVERYWHERE
 

 ***WARNING: THERE IS ZERO FORCE EVERYWHERE IN THE MODEL BASED ON THE DEFAULT 
             CRITERION. PLEASE CHECK THE VALUE OF THE AVERAGE FORCE DURING THE 
             CURRENT ITERATION TO VERIFY THAT THE FORCE IS SMALL ENOUGH TO BE 
             TREATED AS ZERO. IF NOT, PLEASE USE THE SOLUTION CONTROLS TO RESET 
             THE CRITERION FOR ZERO FORCE.

 ITERATION SUMMARY FOR THE INCREMENT:   1 TOTAL ITERATIONS, OF WHICH
   0 ARE SEVERE DISCONTINUITY ITERATIONS AND  1 ARE EQUILIBRIUM ITERATIONS.

 TIME INCREMENT COMPLETED  5.000E-02,  FRACTION OF STEP COMPLETED  0.314    
 STEP TIME COMPLETED       0.314    ,  TOTAL TIME COMPLETED        0.314    


  INCREMENT    16 STARTS. ATTEMPT NUMBER  1, TIME INCREMENT  5.000E-02
 
	SYMMETRIC NEW DIRECT SPARSE SOLVER RUNNING ON
 	1 HOST x 1 MPI RANK PER HOST x 1 THREAD PER RANK
        NUMBER OF EQUATIONS:  24
        NUMBER OF RHS:        1
        NUMBER OF FLOPS:      4.900e+03
        SOLVER ELAPSED TIME:  0ms

               CONVERGENCE CHECKS FOR EQUILIBRIUM ITERATION     1


 AVERAGE FORCE                      4.101-315   TIME AVG. FORCE       1.000E-02
 LARGEST SCALED RESIDUAL FORCE      9.881-324   AT NODE          2   DOF  2
   INSTANCE: BLOCK_INST                                                                      
  CORRESPONDING RESIDUAL FORCE      9.881-324
 LARGEST INCREMENT OF DISP.         2.500E-02   AT NODE          2   DOF  1
   INSTANCE: BLOCK_INST                                                                      
 LARGEST CORRECTION TO DISP.        2.776E-17   AT NODE          2   DOF  1
   INSTANCE: BLOCK_INST                                                                      
          THERE IS ZERO FORCE     EVERYWHERE
 

 ***WARNING: THERE IS ZERO FORCE EVERYWHERE IN THE MODEL BASED ON THE DEFAULT 
             CRITERION. PLEASE CHECK THE VALUE OF THE AVERAGE FORCE DURING THE 
             CURRENT ITERATION TO VERIFY THAT THE FORCE IS SMALL ENOUGH TO BE 
             TREATED AS ZERO. IF NOT, PLEASE USE THE SOLUTION CONTROLS TO RESET 
             THE CRITERION FOR ZERO FORCE.

 ITERATION SUMMARY FOR THE INCREMENT:   1 TOTAL ITERATIONS, OF WHICH
   0 ARE SEVERE DISCONTINUITY ITERATIONS AND  1 ARE EQUILIBRIUM ITERATIONS.

 TIME INCREMENT COMPLETED  5.000E-02,  FRACTION OF STEP COMPLETED  0.364    
 STEP TIME COMPLETED       0.364    ,  TOTAL TIME COMPLETED        0.364    


  INCREMENT    17 STARTS. ATTEMPT NUMBER  1, TIME INCREMENT  5.000E-02
 
	SYMMETRIC NEW DIRECT SPARSE SOLVER RUNNING ON
 	1 HOST x 1 MPI RANK PER HOST x 1 THREAD PER RANK
        NUMBER OF EQUATIONS:  24
        NUMBER OF RHS:        1
        NUMBER OF FLOPS:      4.900e+03
        SOLVER ELAPSED TIME:  0ms

               CONVERGENCE CHECKS FOR EQUILIBRIUM ITERATION     1


 AVERAGE FORCE                      5.260-315   TIME AVG. FORCE       1.000E-02
 LARGEST SCALED RESIDUAL FORCE       0.00       AT NODE          2   DOF  2
   INSTANCE: BLOCK_INST                                                                      
  CORRESPONDING RESIDUAL FORCE       0.00    
 LARGEST INCREMENT OF DISP.         2.500E-02   AT NODE          2   DOF  1
   INSTANCE: BLOCK_INST                                                                      
 LARGEST CORRECTION TO DISP.       -5.551E-17   AT NODE          2   DOF  1
   INSTANCE: BLOCK_INST                                                                      
          THERE IS ZERO FORCE     EVERYWHERE
 

 ***WARNING: THERE IS ZERO FORCE EVERYWHERE IN THE MODEL BASED ON THE DEFAULT 
             CRITERION. PLEASE CHECK THE VALUE OF THE AVERAGE FORCE DURING THE 
             CURRENT ITERATION TO VERIFY THAT THE FORCE IS SMALL ENOUGH TO BE 
             TREATED AS ZERO. IF NOT, PLEASE USE THE SOLUTION CONTROLS TO RESET 
             THE CRITERION FOR ZERO FORCE.

 ITERATION SUMMARY FOR THE INCREMENT:   1 TOTAL ITERATIONS, OF WHICH
   0 ARE SEVERE DISCONTINUITY ITERATIONS AND  1 ARE EQUILIBRIUM ITERATIONS.

 TIME INCREMENT COMPLETED  5.000E-02,  FRACTION OF STEP COMPLETED  0.414    
 STEP TIME COMPLETED       0.414    ,  TOTAL TIME COMPLETED        0.414    


  INCREMENT    18 STARTS. ATTEMPT NUMBER  1, TIME INCREMENT  5.000E-02
 
	SYMMETRIC NEW DIRECT SPARSE SOLVER RUNNING ON
 	1 HOST x 1 MPI RANK PER HOST x 1 THREAD PER RANK
        NUMBER OF EQUATIONS:  24
        NUMBER OF RHS:        1
        NUMBER OF FLOPS:      4.900e+03
        SOLVER ELAPSED TIME:  0ms

               CONVERGENCE CHECKS FOR EQUILIBRIUM ITERATION     1


 AVERAGE FORCE                      6.579-315   TIME AVG. FORCE       1.000E-02
 LARGEST SCALED RESIDUAL FORCE      9.881-324   AT NODE          2   DOF  2
   INSTANCE: BLOCK_INST                                                                      
  CORRESPONDING RESIDUAL FORCE      9.881-324
 LARGEST INCREMENT OF DISP.         2.500E-02   AT NODE          2   DOF  1
   INSTANCE: BLOCK_INST                                                                      
 LARGEST CORRECTION TO DISP.        9.881-288   AT NODE          2   DOF  2
   INSTANCE: BLOCK_INST                                                                      
          THERE IS ZERO FORCE     EVERYWHERE
 

 ***WARNING: THERE IS ZERO FORCE EVERYWHERE IN THE MODEL BASED ON THE DEFAULT 
             CRITERION. PLEASE CHECK THE VALUE OF THE AVERAGE FORCE DURING THE 
             CURRENT ITERATION TO VERIFY THAT THE FORCE IS SMALL ENOUGH TO BE 
             TREATED AS ZERO. IF NOT, PLEASE USE THE SOLUTION CONTROLS TO RESET 
             THE CRITERION FOR ZERO FORCE.

 ITERATION SUMMARY FOR THE INCREMENT:   1 TOTAL ITERATIONS, OF WHICH
   0 ARE SEVERE DISCONTINUITY ITERATIONS AND  1 ARE EQUILIBRIUM ITERATIONS.

 TIME INCREMENT COMPLETED  5.000E-02,  FRACTION OF STEP COMPLETED  0.464    
 STEP TIME COMPLETED       0.464    ,  TOTAL TIME COMPLETED        0.464    


  INCREMENT    19 STARTS. ATTEMPT NUMBER  1, TIME INCREMENT  5.000E-02
 
	SYMMETRIC NEW DIRECT SPARSE SOLVER RUNNING ON
 	1 HOST x 1 MPI RANK PER HOST x 1 THREAD PER RANK
        NUMBER OF EQUATIONS:  24
        NUMBER OF RHS:        1
        NUMBER OF FLOPS:      4.900e+03
        SOLVER ELAPSED TIME:  1ms

               CONVERGENCE CHECKS FOR EQUILIBRIUM ITERATION     1


 AVERAGE FORCE                      8.057-315   TIME AVG. FORCE       1.000E-02
 LARGEST SCALED RESIDUAL FORCE       0.00       AT NODE          2   DOF  2
   INSTANCE: BLOCK_INST                                                                      
  CORRESPONDING RESIDUAL FORCE       0.00    
 LARGEST INCREMENT OF DISP.         2.500E-02   AT NODE          2   DOF  1
   INSTANCE: BLOCK_INST                                                                      
 LARGEST CORRECTION TO DISP.        5.551E-17   AT NODE          2   DOF  1
   INSTANCE: BLOCK_INST                                                                      
          THERE IS ZERO FORCE     EVERYWHERE
 

 ***WARNING: THERE IS ZERO FORCE EVERYWHERE IN THE MODEL BASED ON THE DEFAULT 
             CRITERION. PLEASE CHECK THE VALUE OF THE AVERAGE FORCE DURING THE 
             CURRENT ITERATION TO VERIFY THAT THE FORCE IS SMALL ENOUGH TO BE 
             TREATED AS ZERO. IF NOT, PLEASE USE THE SOLUTION CONTROLS TO RESET 
             THE CRITERION FOR ZERO FORCE.

 ITERATION SUMMARY FOR THE INCREMENT:   1 TOTAL ITERATIONS, OF WHICH
   0 ARE SEVERE DISCONTINUITY ITERATIONS AND  1 ARE EQUILIBRIUM ITERATIONS.

 TIME INCREMENT COMPLETED  5.000E-02,  FRACTION OF STEP COMPLETED  0.514    
 STEP TIME COMPLETED       0.514    ,  TOTAL TIME COMPLETED        0.514    


  INCREMENT    20 STARTS. ATTEMPT NUMBER  1, TIME INCREMENT  5.000E-02
 
	SYMMETRIC NEW DIRECT SPARSE SOLVER RUNNING ON
 	1 HOST x 1 MPI RANK PER HOST x 1 THREAD PER RANK
        NUMBER OF EQUATIONS:  24
        NUMBER OF RHS:        1
        NUMBER OF FLOPS:      4.900e+03
        SOLVER ELAPSED TIME:  1ms

               CONVERGENCE CHECKS FOR EQUILIBRIUM ITERATION     1


 AVERAGE FORCE                      9.694-315   TIME AVG. FORCE       1.000E-02
 LARGEST SCALED RESIDUAL FORCE     -9.881-324   AT NODE          2   DOF  2
   INSTANCE: BLOCK_INST                                                                      
  CORRESPONDING RESIDUAL FORCE     -9.881-324
 LARGEST INCREMENT OF DISP.         2.500E-02   AT NODE          2   DOF  1
   INSTANCE: BLOCK_INST                                                                      
 LARGEST CORRECTION TO DISP.       -9.881-288   AT NODE          2   DOF  2
   INSTANCE: BLOCK_INST                                                                      
          THERE IS ZERO FORCE     EVERYWHERE
 

 ***WARNING: THERE IS ZERO FORCE EVERYWHERE IN THE MODEL BASED ON THE DEFAULT 
             CRITERION. PLEASE CHECK THE VALUE OF THE AVERAGE FORCE DURING THE 
             CURRENT ITERATION TO VERIFY THAT THE FORCE IS SMALL ENOUGH TO BE 
             TREATED AS ZERO. IF NOT, PLEASE USE THE SOLUTION CONTROLS TO RESET 
             THE CRITERION FOR ZERO FORCE.

 ITERATION SUMMARY FOR THE INCREMENT:   1 TOTAL ITERATIONS, OF WHICH
   0 ARE SEVERE DISCONTINUITY ITERATIONS AND  1 ARE EQUILIBRIUM ITERATIONS.

 TIME INCREMENT COMPLETED  5.000E-02,  FRACTION OF STEP COMPLETED  0.564    
 STEP TIME COMPLETED       0.564    ,  TOTAL TIME COMPLETED        0.564    


  INCREMENT    21 STARTS. ATTEMPT NUMBER  1, TIME INCREMENT  5.000E-02
 
	SYMMETRIC NEW DIRECT SPARSE SOLVER RUNNING ON
 	1 HOST x 1 MPI RANK PER HOST x 1 THREAD PER RANK
        NUMBER OF EQUATIONS:  24
        NUMBER OF RHS:        1
        NUMBER OF FLOPS:      4.900e+03
        SOLVER ELAPSED TIME:  1ms

               CONVERGENCE CHECKS FOR EQUILIBRIUM ITERATION     1


 AVERAGE FORCE                      1.149-314   TIME AVG. FORCE       1.000E-02
 LARGEST SCALED RESIDUAL FORCE     -9.881-324   AT NODE          2   DOF  2
   INSTANCE: BLOCK_INST                                                                      
  CORRESPONDING RESIDUAL FORCE     -9.881-324
 LARGEST INCREMENT OF DISP.         2.500E-02   AT NODE          2   DOF  1
   INSTANCE: BLOCK_INST                                                                      
 LARGEST CORRECTION TO DISP.       -9.881-288   AT NODE          2   DOF  2
   INSTANCE: BLOCK_INST                                                                      
          THERE IS ZERO FORCE     EVERYWHERE
 

 ***WARNING: THERE IS ZERO FORCE EVERYWHERE IN THE MODEL BASED ON THE DEFAULT 
             CRITERION. PLEASE CHECK THE VALUE OF THE AVERAGE FORCE DURING THE 
             CURRENT ITERATION TO VERIFY THAT THE FORCE IS SMALL ENOUGH TO BE 
             TREATED AS ZERO. IF NOT, PLEASE USE THE SOLUTION CONTROLS TO RESET 
             THE CRITERION FOR ZERO FORCE.

 ITERATION SUMMARY FOR THE INCREMENT:   1 TOTAL ITERATIONS, OF WHICH
   0 ARE SEVERE DISCONTINUITY ITERATIONS AND  1 ARE EQUILIBRIUM ITERATIONS.

 TIME INCREMENT COMPLETED  5.000E-02,  FRACTION OF STEP COMPLETED  0.614    
 STEP TIME COMPLETED       0.614    ,  TOTAL TIME COMPLETED        0.614    


  INCREMENT    22 STARTS. ATTEMPT NUMBER  1, TIME INCREMENT  5.000E-02
 
	SYMMETRIC NEW DIRECT SPARSE SOLVER RUNNING ON
 	1 HOST x 1 MPI RANK PER HOST x 1 THREAD PER RANK
        NUMBER OF EQUATIONS:  24
        NUMBER OF RHS:        1
        NUMBER OF FLOPS:      4.900e+03
        SOLVER ELAPSED TIME:  1ms

               CONVERGENCE CHECKS FOR EQUILIBRIUM ITERATION     1


 AVERAGE FORCE                      1.345-314   TIME AVG. FORCE       1.000E-02
 LARGEST SCALED RESIDUAL FORCE       0.00       AT NODE          2   DOF  2
   INSTANCE: BLOCK_INST                                                                      
  CORRESPONDING RESIDUAL FORCE       0.00    
 LARGEST INCREMENT OF DISP.         2.500E-02   AT NODE          2   DOF  1
   INSTANCE: BLOCK_INST                                                                      
 LARGEST CORRECTION TO DISP.         0.00       AT NODE          2   DOF  1
   INSTANCE: BLOCK_INST                                                                      
          THERE IS ZERO FORCE     EVERYWHERE
 

 ***WARNING: THERE IS ZERO FORCE EVERYWHERE IN THE MODEL BASED ON THE DEFAULT 
             CRITERION. PLEASE CHECK THE VALUE OF THE AVERAGE FORCE DURING THE 
             CURRENT ITERATION TO VERIFY THAT THE FORCE IS SMALL ENOUGH TO BE 
             TREATED AS ZERO. IF NOT, PLEASE USE THE SOLUTION CONTROLS TO RESET 
             THE CRITERION FOR ZERO FORCE.

 ITERATION SUMMARY FOR THE INCREMENT:   1 TOTAL ITERATIONS, OF WHICH
   0 ARE SEVERE DISCONTINUITY ITERATIONS AND  1 ARE EQUILIBRIUM ITERATIONS.

 TIME INCREMENT COMPLETED  5.000E-02,  FRACTION OF STEP COMPLETED  0.664    
 STEP TIME COMPLETED       0.664    ,  TOTAL TIME COMPLETED        0.664    


  INCREMENT    23 STARTS. ATTEMPT NUMBER  1, TIME INCREMENT  5.000E-02
 
	SYMMETRIC NEW DIRECT SPARSE SOLVER RUNNING ON
 	1 HOST x 1 MPI RANK PER HOST x 1 THREAD PER RANK
        NUMBER OF EQUATIONS:  24
        NUMBER OF RHS:        1
        NUMBER OF FLOPS:      4.900e+03
        SOLVER ELAPSED TIME:  0ms

               CONVERGENCE CHECKS FOR EQUILIBRIUM ITERATION     1


 AVERAGE FORCE                      1.556-314   TIME AVG. FORCE       1.000E-02
 LARGEST SCALED RESIDUAL FORCE     -9.881-324   AT NODE          2   DOF  2
   INSTANCE: BLOCK_INST                                                                      
  CORRESPONDING RESIDUAL FORCE     -9.881-324
 LARGEST INCREMENT OF DISP.         2.500E-02   AT NODE          2   DOF  1
   INSTANCE: BLOCK_INST                                                                      
 LARGEST CORRECTION TO DISP.       -9.881-288   AT NODE          2   DOF  2
   INSTANCE: BLOCK_INST                                                                      
          THERE IS ZERO FORCE     EVERYWHERE
 

 ***WARNING: THERE IS ZERO FORCE EVERYWHERE IN THE MODEL BASED ON THE DEFAULT 
             CRITERION. PLEASE CHECK THE VALUE OF THE AVERAGE FORCE DURING THE 
             CURRENT ITERATION TO VERIFY THAT THE FORCE IS SMALL ENOUGH TO BE 
             TREATED AS ZERO. IF NOT, PLEASE USE THE SOLUTION CONTROLS TO RESET 
             THE CRITERION FOR ZERO FORCE.

 ITERATION SUMMARY FOR THE INCREMENT:   1 TOTAL ITERATIONS, OF WHICH
   0 ARE SEVERE DISCONTINUITY ITERATIONS AND  1 ARE EQUILIBRIUM ITERATIONS.

 TIME INCREMENT COMPLETED  5.000E-02,  FRACTION OF STEP COMPLETED  0.714    
 STEP TIME COMPLETED       0.714    ,  TOTAL TIME COMPLETED        0.714    


  INCREMENT    24 STARTS. ATTEMPT NUMBER  1, TIME INCREMENT  5.000E-02
 
	SYMMETRIC NEW DIRECT SPARSE SOLVER RUNNING ON
 	1 HOST x 1 MPI RANK PER HOST x 1 THREAD PER RANK
        NUMBER OF EQUATIONS:  24
        NUMBER OF RHS:        1
        NUMBER OF FLOPS:      4.900e+03
        SOLVER ELAPSED TIME:  0ms

               CONVERGENCE CHECKS FOR EQUILIBRIUM ITERATION     1


 AVERAGE FORCE                      1.783-314   TIME AVG. FORCE       1.000E-02
 LARGEST SCALED RESIDUAL FORCE      9.881-324   AT NODE          2   DOF  2
   INSTANCE: BLOCK_INST                                                                      
  CORRESPONDING RESIDUAL FORCE      9.881-324
 LARGEST INCREMENT OF DISP.         2.500E-02   AT NODE          2   DOF  1
   INSTANCE: BLOCK_INST                                                                      
 LARGEST CORRECTION TO DISP.        5.551E-17   AT NODE          2   DOF  1
   INSTANCE: BLOCK_INST                                                                      
          THERE IS ZERO FORCE     EVERYWHERE
 

 ***WARNING: THERE IS ZERO FORCE EVERYWHERE IN THE MODEL BASED ON THE DEFAULT 
             CRITERION. PLEASE CHECK THE VALUE OF THE AVERAGE FORCE DURING THE 
             CURRENT ITERATION TO VERIFY THAT THE FORCE IS SMALL ENOUGH TO BE 
             TREATED AS ZERO. IF NOT, PLEASE USE THE SOLUTION CONTROLS TO RESET 
             THE CRITERION FOR ZERO FORCE.

 ITERATION SUMMARY FOR THE INCREMENT:   1 TOTAL ITERATIONS, OF WHICH
   0 ARE SEVERE DISCONTINUITY ITERATIONS AND  1 ARE EQUILIBRIUM ITERATIONS.

 TIME INCREMENT COMPLETED  5.000E-02,  FRACTION OF STEP COMPLETED  0.764    
 STEP TIME COMPLETED       0.764    ,  TOTAL TIME COMPLETED        0.764    


  INCREMENT    25 STARTS. ATTEMPT NUMBER  1, TIME INCREMENT  5.000E-02
 
	SYMMETRIC NEW DIRECT SPARSE SOLVER RUNNING ON
 	1 HOST x 1 MPI RANK PER HOST x 1 THREAD PER RANK
        NUMBER OF EQUATIONS:  24
        NUMBER OF RHS:        1
        NUMBER OF FLOPS:      4.900e+03
        SOLVER ELAPSED TIME:  0ms

               CONVERGENCE CHECKS FOR EQUILIBRIUM ITERATION     1


 AVERAGE FORCE                      2.027-314   TIME AVG. FORCE       1.000E-02
 LARGEST SCALED RESIDUAL FORCE       0.00       AT NODE          2   DOF  2
   INSTANCE: BLOCK_INST                                                                      
  CORRESPONDING RESIDUAL FORCE       0.00    
 LARGEST INCREMENT OF DISP.         2.500E-02   AT NODE          2   DOF  1
   INSTANCE: BLOCK_INST                                                                      
 LARGEST CORRECTION TO DISP.         0.00       AT NODE          2   DOF  1
   INSTANCE: BLOCK_INST                                                                      
          THERE IS ZERO FORCE     EVERYWHERE
 

 ***WARNING: THERE IS ZERO FORCE EVERYWHERE IN THE MODEL BASED ON THE DEFAULT 
             CRITERION. PLEASE CHECK THE VALUE OF THE AVERAGE FORCE DURING THE 
             CURRENT ITERATION TO VERIFY THAT THE FORCE IS SMALL ENOUGH TO BE 
             TREATED AS ZERO. IF NOT, PLEASE USE THE SOLUTION CONTROLS TO RESET 
             THE CRITERION FOR ZERO FORCE.

 ITERATION SUMMARY FOR THE INCREMENT:   1 TOTAL ITERATIONS, OF WHICH
   0 ARE SEVERE DISCONTINUITY ITERATIONS AND  1 ARE EQUILIBRIUM ITERATIONS.

 TIME INCREMENT COMPLETED  5.000E-02,  FRACTION OF STEP COMPLETED  0.814    
 STEP TIME COMPLETED       0.814    ,  TOTAL TIME COMPLETED        0.814    


  INCREMENT    26 STARTS. ATTEMPT NUMBER  1, TIME INCREMENT  5.000E-02
 
	SYMMETRIC NEW DIRECT SPARSE SOLVER RUNNING ON
 	1 HOST x 1 MPI RANK PER HOST x 1 THREAD PER RANK
        NUMBER OF EQUATIONS:  24
        NUMBER OF RHS:        1
        NUMBER OF FLOPS:      4.900e+03
        SOLVER ELAPSED TIME:  0ms

               CONVERGENCE CHECKS FOR EQUILIBRIUM ITERATION     1


 AVERAGE FORCE                      2.286-314   TIME AVG. FORCE       1.000E-02
 LARGEST SCALED RESIDUAL FORCE     -9.881-324   AT NODE          2   DOF  2
   INSTANCE: BLOCK_INST                                                                      
  CORRESPONDING RESIDUAL FORCE     -9.881-324
 LARGEST INCREMENT OF DISP.         2.500E-02   AT NODE          2   DOF  1
   INSTANCE: BLOCK_INST                                                                      
 LARGEST CORRECTION TO DISP.       -5.551E-17   AT NODE          2   DOF  1
   INSTANCE: BLOCK_INST                                                                      
          THERE IS ZERO FORCE     EVERYWHERE
 

 ***WARNING: THERE IS ZERO FORCE EVERYWHERE IN THE MODEL BASED ON THE DEFAULT 
             CRITERION. PLEASE CHECK THE VALUE OF THE AVERAGE FORCE DURING THE 
             CURRENT ITERATION TO VERIFY THAT THE FORCE IS SMALL ENOUGH TO BE 
             TREATED AS ZERO. IF NOT, PLEASE USE THE SOLUTION CONTROLS TO RESET 
             THE CRITERION FOR ZERO FORCE.

 ITERATION SUMMARY FOR THE INCREMENT:   1 TOTAL ITERATIONS, OF WHICH
   0 ARE SEVERE DISCONTINUITY ITERATIONS AND  1 ARE EQUILIBRIUM ITERATIONS.

 TIME INCREMENT COMPLETED  5.000E-02,  FRACTION OF STEP COMPLETED  0.864    
 STEP TIME COMPLETED       0.864    ,  TOTAL TIME COMPLETED        0.864    


  INCREMENT    27 STARTS. ATTEMPT NUMBER  1, TIME INCREMENT  5.000E-02
 
	SYMMETRIC NEW DIRECT SPARSE SOLVER RUNNING ON
 	1 HOST x 1 MPI RANK PER HOST x 1 THREAD PER RANK
        NUMBER OF EQUATIONS:  24
        NUMBER OF RHS:        1
        NUMBER OF FLOPS:      4.900e+03
        SOLVER ELAPSED TIME:  1ms

               CONVERGENCE CHECKS FOR EQUILIBRIUM ITERATION     1


 AVERAGE FORCE                      2.561-314   TIME AVG. FORCE       1.000E-02
 LARGEST SCALED RESIDUAL FORCE      9.881-324   AT NODE          2   DOF  2
   INSTANCE: BLOCK_INST                                                                      
  CORRESPONDING RESIDUAL FORCE      9.881-324
 LARGEST INCREMENT OF DISP.         2.500E-02   AT NODE          2   DOF  1
   INSTANCE: BLOCK_INST                                                                      
 LARGEST CORRECTION TO DISP.        9.881-288   AT NODE          2   DOF  2
   INSTANCE: BLOCK_INST                                                                      
          THERE IS ZERO FORCE     EVERYWHERE
 

 ***WARNING: THERE IS ZERO FORCE EVERYWHERE IN THE MODEL BASED ON THE DEFAULT 
             CRITERION. PLEASE CHECK THE VALUE OF THE AVERAGE FORCE DURING THE 
             CURRENT ITERATION TO VERIFY THAT THE FORCE IS SMALL ENOUGH TO BE 
             TREATED AS ZERO. IF NOT, PLEASE USE THE SOLUTION CONTROLS TO RESET 
             THE CRITERION FOR ZERO FORCE.

 ITERATION SUMMARY FOR THE INCREMENT:   1 TOTAL ITERATIONS, OF WHICH
   0 ARE SEVERE DISCONTINUITY ITERATIONS AND  1 ARE EQUILIBRIUM ITERATIONS.

 TIME INCREMENT COMPLETED  5.000E-02,  FRACTION OF STEP COMPLETED  0.914    
 STEP TIME COMPLETED       0.914    ,  TOTAL TIME COMPLETED        0.914    


  INCREMENT    28 STARTS. ATTEMPT NUMBER  1, TIME INCREMENT  5.000E-02
 
	SYMMETRIC NEW DIRECT SPARSE SOLVER RUNNING ON
 	1 HOST x 1 MPI RANK PER HOST x 1 THREAD PER RANK
        NUMBER OF EQUATIONS:  24
        NUMBER OF RHS:        1
        NUMBER OF FLOPS:      4.900e+03
        SOLVER ELAPSED TIME:  0ms

               CONVERGENCE CHECKS FOR EQUILIBRIUM ITERATION     1


 AVERAGE FORCE                      2.852-314   TIME AVG. FORCE       1.000E-02
 LARGEST SCALED RESIDUAL FORCE     -9.881-324   AT NODE          2   DOF  2
   INSTANCE: BLOCK_INST                                                                      
  CORRESPONDING RESIDUAL FORCE     -9.881-324
 LARGEST INCREMENT OF DISP.         2.500E-02   AT NODE          2   DOF  1
   INSTANCE: BLOCK_INST                                                                      
 LARGEST CORRECTION TO DISP.       -5.551E-17   AT NODE          2   DOF  1
   INSTANCE: BLOCK_INST                                                                      
          THERE IS ZERO FORCE     EVERYWHERE
 

 ***WARNING: THERE IS ZERO FORCE EVERYWHERE IN THE MODEL BASED ON THE DEFAULT 
             CRITERION. PLEASE CHECK THE VALUE OF THE AVERAGE FORCE DURING THE 
             CURRENT ITERATION TO VERIFY THAT THE FORCE IS SMALL ENOUGH TO BE 
             TREATED AS ZERO. IF NOT, PLEASE USE THE SOLUTION CONTROLS TO RESET 
             THE CRITERION FOR ZERO FORCE.

 ITERATION SUMMARY FOR THE INCREMENT:   1 TOTAL ITERATIONS, OF WHICH
   0 ARE SEVERE DISCONTINUITY ITERATIONS AND  1 ARE EQUILIBRIUM ITERATIONS.

 TIME INCREMENT COMPLETED  5.000E-02,  FRACTION OF STEP COMPLETED  0.964    
 STEP TIME COMPLETED       0.964    ,  TOTAL TIME COMPLETED        0.964    


  INCREMENT    29 STARTS. ATTEMPT NUMBER  1, TIME INCREMENT  3.567E-02
 
	SYMMETRIC NEW DIRECT SPARSE SOLVER RUNNING ON
 	1 HOST x 1 MPI RANK PER HOST x 1 THREAD PER RANK
        NUMBER OF EQUATIONS:  24
        NUMBER OF RHS:        1
        NUMBER OF FLOPS:      4.900e+03
        SOLVER ELAPSED TIME:  1ms

               CONVERGENCE CHECKS FOR EQUILIBRIUM ITERATION     1


 AVERAGE FORCE                      3.159-314   TIME AVG. FORCE       1.000E-02
 LARGEST SCALED RESIDUAL FORCE     -9.881-324   AT NODE          2   DOF  2
   INSTANCE: BLOCK_INST                                                                      
  CORRESPONDING RESIDUAL FORCE     -9.881-324
 LARGEST INCREMENT OF DISP.         1.783E-02   AT NODE          2   DOF  1
   INSTANCE: BLOCK_INST                                                                      
 LARGEST CORRECTION TO DISP.        2.429E-17   AT NODE          2   DOF  1
   INSTANCE: BLOCK_INST                                                                      
          THERE IS ZERO FORCE     EVERYWHERE
 

 ***WARNING: THERE IS ZERO FORCE EVERYWHERE IN THE MODEL BASED ON THE DEFAULT 
             CRITERION. PLEASE CHECK THE VALUE OF THE AVERAGE FORCE DURING THE 
             CURRENT ITERATION TO VERIFY THAT THE FORCE IS SMALL ENOUGH TO BE 
             TREATED AS ZERO. IF NOT, PLEASE USE THE SOLUTION CONTROLS TO RESET 
             THE CRITERION FOR ZERO FORCE.

 ITERATION SUMMARY FOR THE INCREMENT:   1 TOTAL ITERATIONS, OF WHICH
   0 ARE SEVERE DISCONTINUITY ITERATIONS AND  1 ARE EQUILIBRIUM ITERATIONS.

 TIME INCREMENT COMPLETED  3.567E-02,  FRACTION OF STEP COMPLETED   1.00    
 STEP TIME COMPLETED        1.00    ,  TOTAL TIME COMPLETED         1.00    


          THE ANALYSIS HAS BEEN COMPLETED



     ANALYSIS SUMMARY:
     TOTAL OF         29  INCREMENTS
                       0  CUTBACKS IN AUTOMATIC INCREMENTATION
                      29  ITERATIONS INCLUDING CONTACT ITERATIONS IF PRESENT
                      29  PASSES THROUGH THE EQUATION SOLVER OF WHICH 
                       1  INVOLVE MATRIX DECOMPOSITION, INCLUDING
                       0  DECOMPOSITION(S) OF THE MASS MATRIX
                       1  REORDERING OF EQUATIONS TO MINIMIZE WAVEFRONT
                       0  ADDITIONAL RESIDUAL EVALUATIONS FOR LINE SEARCHES
                       0  ADDITIONAL OPERATOR EVALUATIONS FOR LINE SEARCHES
                       0  WARNING MESSAGES DURING USER INPUT PROCESSING
                      43  WARNING MESSAGES DURING ANALYSIS
                      13  ANALYSIS WARNINGS ARE NUMERICAL PROBLEM MESSAGES
                       0  ANALYSIS WARNINGS ARE NEGATIVE EIGENVALUE MESSAGES
                       0  ERROR MESSAGES



     JOB TIME SUMMARY
       USER TIME (SEC)      =     0.20    
       SYSTEM TIME (SEC)    =     0.20    
       TOTAL CPU TIME (SEC) =     0.40    
       WALLCLOCK TIME (SEC) =            1
       MEMORY PEAK (GB)     =            0
