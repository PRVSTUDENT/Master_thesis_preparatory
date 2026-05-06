C     =====================================================================
C     Chaboche Unified Viscoplastic User Material (UMAT) 
C     Implementation for Abaqus/Standard
C     
C     Model: Chaboche viscoplastic constitutive model with kinematic 
C            hardening and isotropic hardening
C     
C     Reference: Yue & Zhou 2023, 316 Stainless Steel
C     
C     State Variables (STATEV) - CORRECTED LAYOUT:
C     STATEV(1):     Accumulated viscoplastic strain (p)
C     STATEV(2-7):   Backstress tensor (X11, X22, X33, X12, X13, X23)
C     STATEV(8-13):  Viscoplastic strain tensor (Evp11, Evp22, ...)
C     STATEV(14):    Current isotropic hardening (R)
C     STATEV(15):    Last viscoplastic multiplier increment (dp)
C     
C     Material Properties (PROPS):
C     PROPS(1):      Young's modulus (E) [GPa] -> convert to MPa
C     PROPS(2):      Poisson's ratio (nu)
C     PROPS(3):      Initial yield stress (sigma_y) [MPa]
C     PROPS(4):      Isotropic hardening parameter (Q) [MPa]
C     PROPS(5):      Isotropic hardening exponent (b)
C     PROPS(6):      Kinematic hardening modulus (C) [MPa]
C     PROPS(7):      Kinematic hardening decay (gamma)
C     PROPS(8):      Viscosity parameter (K) [MPa·s]
C     PROPS(9):      Viscosity exponent (m)
C     =====================================================================

      SUBROUTINE UMAT(STRESS,STATEV,DDSDDE,SSE,SPD,SCD,
     1 RPL,DRPL,DRPLDT,STRAN,DSTRAN,TIME,DTIME,TEMP,DTEMP,
     2 PREDEF,DPRED,CMNAME,NDI,NSHR,NTENS,NSTATEV,PROPS,NPROPS,
     3 COORDS,DROT,PNEWDT,CELENT,DFGRD0,DFGRD1,NOEL,NPT,LAYER,
     4 KSPT,JSTEP,KINC)
      
      IMPLICIT NONE
      
      INTEGER :: NDI, NSHR, NTENS, NSTATEV, NPROPS, NOEL, NPT
      INTEGER :: LAYER, KSPT, KINC, JSTEP
      REAL*8 :: STRESS(NTENS), STATEV(NSTATEV), DDSDDE(NTENS,NTENS)
      REAL*8 :: STRAN(NTENS), DSTRAN(NTENS), TIME(2), DTIME
      REAL*8 :: TEMP, DTEMP, PREDEF(*), DPRED(*)
      REAL*8 :: PROPS(NPROPS), COORDS(3), PNEWDT, CELENT
      REAL*8 :: DROT(3,3), DFGRD0(3,3), DFGRD1(3,3)
      REAL*8 :: SSE, SPD, SCD, RPL, DRPL, DRPLDT
      CHARACTER*80 :: CMNAME
      
C     Local variables
      INTEGER :: I, J, K, IITER, MAXITER
      REAL*8 :: E, NU, SIGMA_Y, Q, B, C_KIN, GAMMA_KIN, K_VIS, M_VIS
      REAL*8 :: TWOMU, BULK, LAMBDA
      REAL*8 :: DEE(6,6)
      REAL*8 :: P_OLD, X_OLD(6), EPS_VP_OLD(6)
      REAL*8 :: R_OLD, DP_OLD
      REAL*8 :: DEPS(6), STRESS_TRIAL(6), DEVIATOR(6)
      REAL*8 :: X(6), P, EPS_VP(6)
      REAL*8 :: R, DP, J2, Q_FLOW, YIELD_FUNC, DLAMBDA
      REAL*8 :: N_FLOW(6), IDENT(6)
      REAL*8 :: DSTREP(6), DX(6), DEP_VP(6), DENOM
      REAL*8 :: CONV_TOL, ERROR, PHI, PHI_DOT
      REAL*8 :: MEAN_STRESS, FACT, HARD_RATE
      
C     Parameters
      DATA IDENT/1.0D0, 1.0D0, 1.0D0, 0.0D0, 0.0D0, 0.0D0/
      DATA CONV_TOL/1.0D-8/
      DATA MAXITER/100/
      DATA FACT/1.5D0/
      
C     ===================================================================
C     Extract material properties and convert units
C     ===================================================================
      
      E = PROPS(1)                      ! Material properties in MPa
      NU = PROPS(2)
      SIGMA_Y = PROPS(3)                ! MPa
      Q = PROPS(4)                      ! MPa
      B = PROPS(5)
      C_KIN = PROPS(6)                  ! MPa
      GAMMA_KIN = PROPS(7)
      K_VIS = PROPS(8)
      M_VIS = PROPS(9)
      
C     Elastic constants
      TWOMU = E / (1.0D0 + NU)
      BULK = E / (3.0D0 * (1.0D0 - 2.0D0 * NU))
      LAMBDA = BULK - TWOMU / 3.0D0
      
C     ===================================================================
C     Initialize elastic compliance matrix
C     ===================================================================
      
      CALL INITELASTIC(TWOMU, BULK, LAMBDA, DEE)
      
C     ===================================================================
C     Extract previous state variables (correct layout)
C     ===================================================================
      
      P_OLD = STATEV(1)                 ! Accumulated viscoplastic strain
      
      DO I = 1, 6
        X_OLD(I) = STATEV(1 + I)        ! Backstress (indices 2-7)
        EPS_VP_OLD(I) = STATEV(7 + I)   ! Vp strain tensor (indices 8-13)
      END DO
      
      R_OLD = STATEV(14)                ! Isotropic hardening
      DP_OLD = STATEV(15)               ! Last multiplier increment
      
C     ===================================================================
C     Initialize current state variables from old values
C     ===================================================================
      
      P = P_OLD
      DLAMBDA = 0.0D0
      DO I = 1, 6
        X(I) = X_OLD(I)
        EPS_VP(I) = EPS_VP_OLD(I)
      END DO
      
C     ===================================================================
C     Compute elastic trial stress
C     ===================================================================
      
      DEPS(1:NTENS) = DSTRAN(1:NTENS)
      CALL MATVEC(DEE, DEPS, DSTREP, NTENS)
      
      DO I = 1, NTENS
        STRESS_TRIAL(I) = STRESS(I) + DSTREP(I)  ! STRESS is input at start of increment
      END DO
      
C     ===================================================================
C     Compute J2 norm and yield function
C     ===================================================================
      
      CALL COMPUTEJ2(STRESS_TRIAL, X_OLD, J2, N_FLOW, DEVIATOR)
      
      R = Q * (1.0D0 - EXP(-B * P_OLD))  ! Current isotropic hardening
      YIELD_FUNC = J2 - (SIGMA_Y + R)
      
C     ===================================================================
C     Check yield condition: if f ≤ 0, elastic step
C     ===================================================================
      
      IF(YIELD_FUNC .LE. 0.0D0) THEN
C       Elastic step
        
        DO I = 1, NTENS
          STRESS(I) = STRESS_TRIAL(I)
        END DO
        
        CALL COPYELASTIC(DEE, DDSDDE, NTENS)
        
      ELSE
C       Elastoviscoplastic step: solve rate-dependent evolution
C       Flow rule: dε_vp/dt = <Φ(f)>^m  with Φ(f) = (J2 - σ_y - R) / K
        
        CALL INTEGRATEVISCOPLASTIC(STRESS_TRIAL, X_OLD, P_OLD, 
     1      E, NU, SIGMA_Y, Q, B, C_KIN, GAMMA_KIN, K_VIS, M_VIS,
     2      DTIME, STRESS, X, P, DLAMBDA, NTENS, 
     3      DDSDDE, DEE, CONV_TOL, MAXITER, J2, N_FLOW)
        
        CALL COMPUTEJ2(STRESS, X, J2, N_FLOW, DEVIATOR)
        DO I = 1, NTENS
          EPS_VP(I) = EPS_VP_OLD(I) + DLAMBDA * N_FLOW(I)
        END DO
        
      END IF
      
C     ===================================================================
C     Update state variables (correct layout)
C     ===================================================================
      
      STATEV(1) = P                     ! Accumulated viscoplastic strain
      
      DO I = 1, 6
        STATEV(1 + I) = X(I)            ! Backstress (indices 2-7)
        STATEV(7 + I) = EPS_VP(I)       ! Vp strain tensor (indices 8-13)
      END DO
      
      R = Q * (1.0D0 - EXP(-B * P))     ! Updated isotropic hardening
      STATEV(14) = R
      STATEV(15) = DLAMBDA              ! Store multiplier increment
      
C     ===================================================================
C     Compute strain energy density (simplified)
C     ===================================================================
      
      SSE = 0.0D0
      SPD = 0.0D0
      DO I = 1, NTENS
        SSE = SSE + 0.5D0 * STRESS(I) * DSTRAN(I)
      END DO
      
      RETURN
      END
C     =====================================================================
      
C     =====================================================================
C     Compute J2 norm of deviatoric stress
C     =====================================================================
      SUBROUTINE COMPUTEJ2(STRESS, X, J2, N_FLOW, DEVIATOR)
      
      IMPLICIT NONE
      INTEGER :: I, J
      REAL*8 :: STRESS(6), X(6), J2, N_FLOW(6), DEVIATOR(6)
      REAL*8 :: MEAN_STRESS, DEV(6), DIFF(6)
      
      MEAN_STRESS = (STRESS(1) + STRESS(2) + STRESS(3)) / 3.0D0
      
      DEV(1) = STRESS(1) - MEAN_STRESS
      DEV(2) = STRESS(2) - MEAN_STRESS
      DEV(3) = STRESS(3) - MEAN_STRESS
      DEV(4) = STRESS(4)
      DEV(5) = STRESS(5)
      DEV(6) = STRESS(6)
      
      DO I = 1, 6
        DIFF(I) = DEV(I) - X(I)
      END DO
      
C     J2 = sqrt(3/2 * diff:diff)
      J2 = 0.0D0
      DO I = 1, 3
        J2 = J2 + DIFF(I)*DIFF(I)
      END DO
      J2 = J2 + 2.0D0*(DIFF(4)*DIFF(4) + DIFF(5)*DIFF(5)
     1              + DIFF(6)*DIFF(6))
      
      IF(J2 .LT. 1.0D-15) J2 = 1.0D-15
      J2 = SQRT(1.5D0 * J2)
      
C     Flow direction
      IF(J2 .GT. 1.0D-15) THEN
        DO I = 1, 6
          N_FLOW(I) = 1.5D0 * DIFF(I) / J2
          DEVIATOR(I) = DEV(I)
        END DO
      END IF
      
      RETURN
      END
C     =====================================================================
      
C     =====================================================================
C     Isotropic hardening
C     =====================================================================
      SUBROUTINE ISOTROPICHARDENING(P, Q, B, SIGMA_Y, R)
      
      IMPLICIT NONE
      REAL*8 :: P, Q, B, SIGMA_Y, R
      
      IF(P .GT. 0.0D0) THEN
        R = Q * (1.0D0 - EXP(-B * P))
      ELSE
        R = 0.0D0
      END IF
      
      RETURN
      END
C     =====================================================================
      
C     =====================================================================
C     Integration routine - Viscoplastic implicit Euler
C     =====================================================================
      SUBROUTINE INTEGRATEVISCOPLASTIC(STRESS_T, X_OLD, P_OLD,
     1    E, NU, SIGMA_Y, Q, B, C_KIN, GAMMA_KIN, K_VIS, M_VIS,
     2    DTIME, STRESS, X, P, DLAMBDA, NTENS,
     3    DDSDDE, DEE, CONV_TOL, MAXITER, J2_TRIAL, N_FLOW_TRIAL)
      
      IMPLICIT NONE
      INTEGER :: NTENS, MAXITER, IITER, I, J
      REAL*8 :: STRESS_T(NTENS), X_OLD(NTENS), STRESS(NTENS), X(NTENS)
      REAL*8 :: P_OLD, P, DLAMBDA
      REAL*8 :: E, NU, SIGMA_Y, Q, B, C_KIN, GAMMA_KIN, K_VIS, M_VIS
      REAL*8 :: DTIME, CONV_TOL, ERROR, J2_TRIAL, N_FLOW_TRIAL(NTENS)
      REAL*8 :: DEE(NTENS,NTENS), DDSDDE(NTENS,NTENS)
      REAL*8 :: J2, Q_FLOW, YIELD_FUNC, R, DPSI_DLN, DENOM
      REAL*8 :: N_FLOW(6), DEVIATOR(6), STRESS_TEMP(6), X_TEMP(6)
      REAL*8 :: TWOMU, BULK
      REAL*8 :: PHI, PHI_DOT, FACT
      
      TWOMU = E / (1.0D0 + NU)
      BULK = E / (3.0D0 * (1.0D0 - 2.0D0 * NU))
      FACT = 1.5D0 / (TWOMU + C_KIN)
      
C     Initialize
      DO I = 1, NTENS
        STRESS(I) = STRESS_T(I)
        X(I) = X_OLD(I)
      END DO
      P = P_OLD
      DLAMBDA = 0.0D0
      
C     Implicit iteration for rate-dependent multiplier
      DO IITER = 1, MAXITER
        
        CALL COMPUTEJ2(STRESS, X, J2, N_FLOW, DEVIATOR)
        R = Q * (1.0D0 - EXP(-B * P))
        
        Q_FLOW = J2 - (SIGMA_Y + R)     ! Yield function
        
C       Rate-dependent flow: Φ = <Q_flow / K>^m
C       For viscoplasticity: dε_vp = Φ^m * ∂f/∂σ * dt
        
        IF(Q_FLOW .LT. 0.0D0) THEN
          PHI = 0.0D0
        ELSE
          PHI = (Q_FLOW / K_VIS) ** M_VIS
        END IF
        
        PHI_DOT = PHI / DTIME
        
C       Residual: should converge to zero
        ERROR = ABS(PHI_DOT)
        
        IF(ERROR .LT. CONV_TOL) EXIT
        
C       Update stresses and internal variables
C       ε_n+1 = ε_n - Δλ * ∂f/∂σ = ε_n - Φ^m * dt * n
        
        DLAMBDA = PHI * DTIME
        
        DO I = 1, NTENS
          STRESS(I) = STRESS_T(I) - TWOMU * DLAMBDA * N_FLOW(I)
C         Backstress evolution: dX = C * dε_vp - γ * X * dp
          X(I) = X_OLD(I) + (C_KIN * DLAMBDA * N_FLOW(I))
     1                    - (GAMMA_KIN * DLAMBDA * X_OLD(I))
        END DO
        
        P = P_OLD + DLAMBDA
        
      END DO
      
C     Compute consistent tangent stiffness
      CALL COMPCONSISTENTTANGENT(TWOMU, BULK, DLAMBDA, N_FLOW,
     1      C_KIN, GAMMA_KIN, Q, B, P, NTENS, DEE, DDSDDE)
      
      RETURN
      END
C     =====================================================================
      
C     =====================================================================
C     Initialize elastic compliance
C     =====================================================================
      SUBROUTINE INITELASTIC(TWOMU, BULK, LAMBDA, DEE)
      
      IMPLICIT NONE
      REAL*8 :: TWOMU, BULK, LAMBDA, DEE(6,6)
      INTEGER :: I, J
      
      DO I = 1, 6
        DO J = 1, 6
          DEE(I,J) = 0.0D0
        END DO
      END DO
      
      DEE(1,1) = LAMBDA + TWOMU
      DEE(2,2) = LAMBDA + TWOMU
      DEE(3,3) = LAMBDA + TWOMU
      DEE(1,2) = LAMBDA
      DEE(1,3) = LAMBDA
      DEE(2,3) = LAMBDA
      DEE(2,1) = LAMBDA
      DEE(3,1) = LAMBDA
      DEE(3,2) = LAMBDA
      DEE(4,4) = TWOMU / 2.0D0
      DEE(5,5) = TWOMU / 2.0D0
      DEE(6,6) = TWOMU / 2.0D0
      
      RETURN
      END
C     =====================================================================
      
C     =====================================================================
C     Matrix-vector multiplication
C     =====================================================================
      SUBROUTINE MATVEC(A, V, RES, N)
      
      IMPLICIT NONE
      INTEGER :: N, I, J
      REAL*8 :: A(N,N), V(N), RES(N)
      
      DO I = 1, N
        RES(I) = 0.0D0
        DO J = 1, N
          RES(I) = RES(I) + A(I,J) * V(J)
        END DO
      END DO
      
      RETURN
      END
C     =====================================================================
      
C     =====================================================================
C     Copy elastic stiffness to DDSDDE
C     =====================================================================
      SUBROUTINE COPYELASTIC(DEE, DDSDDE, NTENS)
      
      IMPLICIT NONE
      INTEGER :: NTENS, I, J
      REAL*8 :: DEE(NTENS,NTENS), DDSDDE(NTENS,NTENS)
      
      DO I = 1, NTENS
        DO J = 1, NTENS
          DDSDDE(I,J) = DEE(I,J)
        END DO
      END DO
      
      RETURN
      END
C     =====================================================================
      
C     =====================================================================
C     Compute consistent tangent stiffness
C     =====================================================================
      SUBROUTINE COMPCONSISTENTTANGENT(TWOMU, BULK, DLAMBDA, N_FLOW,
     1      C_KIN, GAMMA_KIN, Q, B, P, NTENS, DEE, DDSDDE)
      
      IMPLICIT NONE
      INTEGER :: NTENS, I, J
      REAL*8 :: TWOMU, BULK, DLAMBDA, N_FLOW(NTENS)
      REAL*8 :: C_KIN, GAMMA_KIN, Q, B, P
      REAL*8 :: DEE(NTENS,NTENS), DDSDDE(NTENS,NTENS)
      REAL*8 :: HARD_DENOM, HARD_RATE
      
      DO I = 1, NTENS
        DO J = 1, NTENS
          DDSDDE(I,J) = DEE(I,J)
        END DO
      END DO
      
C     Hardening derivative: dR/dp = Q*b*exp(-b*p)
      HARD_RATE = Q * B * EXP(-B * P)
      HARD_DENOM = TWOMU + C_KIN + HARD_RATE
      
      IF(HARD_DENOM .GT. 1.0D-15) THEN
        DO I = 1, NTENS
          DO J = 1, NTENS
            DDSDDE(I,J) = DDSDDE(I,J) 
     1                  - (TWOMU / HARD_DENOM) * N_FLOW(I) * N_FLOW(J)
          END DO
        END DO
      END IF
      
      RETURN
      END

