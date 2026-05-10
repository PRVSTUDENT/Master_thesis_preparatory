      SUBROUTINE UMAT(STRESS,STATEV,DDSDDE,SSE,SPD,SCD,
     1 RPL,DDSDDT,DRPLDE,DRPLDT,STRAN,DSTRAN,TIME,DTIME,
     2 TEMP,DTEMP,PREDEF,DPRED,CMNAME,NDI,NSHR,NTENS,NSTATV,
     3 PROPS,NPROPS,COORDS,DROT,PNEWDT,CELENT,DFGRD0,DFGRD1,
     4 NOEL,NPT,LAYER,KSPT,JSTEP,KINC)

      INCLUDE 'ABA_PARAM.INC'

      CHARACTER*80 CMNAME
      DIMENSION STRESS(NTENS),STATEV(NSTATV)
      DIMENSION DDSDDE(NTENS,NTENS),DDSDDT(NTENS)
      DIMENSION DRPLDE(NTENS),STRAN(NTENS),DSTRAN(NTENS)
      DIMENSION TIME(2),PREDEF(1),DPRED(1),PROPS(NPROPS)
      DIMENSION COORDS(3),DROT(3,3),DFGRD0(3,3)
      DIMENSION DFGRD1(3,3),JSTEP(4)

      DOUBLE PRECISION E,NU,SIGY,QISO,BISO,CKIN,GKIN,KVIS,MVIS
      DOUBLE PRECISION MU,LAM,MEAN,QEQ,RISO,FVAL,HARD
      DOUBLE PRECISION DPALG,DPRATE,DP,DPMAX,TINY
      DOUBLE PRECISION STRIAL(6),XOLD(6),XNEW(6)
      DOUBLE PRECISION EPOLD(6),EPNEW(6),ETA(6),NFLOW(6)
      INTEGER I,J

      TINY = 1.D-12
      DPMAX = 1.D-3

      E     = PROPS(1)
      NU    = PROPS(2)
      SIGY  = PROPS(3)
      QISO  = PROPS(4)
      BISO  = PROPS(5)
      CKIN  = PROPS(6)
      GKIN  = PROPS(7)
      KVIS  = PROPS(8)
      MVIS  = PROPS(9)

      MU  = E/(2.D0*(1.D0+NU))
      LAM = E*NU/((1.D0+NU)*(1.D0-2.D0*NU))

      DO I=1,NTENS
        DO J=1,NTENS
          DDSDDE(I,J)=0.D0
        END DO
      END DO

      DDSDDE(1,1)=LAM+2.D0*MU
      DDSDDE(2,2)=LAM+2.D0*MU
      DDSDDE(3,3)=LAM+2.D0*MU
      DDSDDE(1,2)=LAM
      DDSDDE(1,3)=LAM
      DDSDDE(2,1)=LAM
      DDSDDE(2,3)=LAM
      DDSDDE(3,1)=LAM
      DDSDDE(3,2)=LAM
      IF (NTENS.GE.4) DDSDDE(4,4)=MU
      IF (NTENS.GE.5) DDSDDE(5,5)=MU
      IF (NTENS.GE.6) DDSDDE(6,6)=MU

      DO I=1,6
        XOLD(I)=0.D0
        XNEW(I)=0.D0
        EPOLD(I)=0.D0
        EPNEW(I)=0.D0
        ETA(I)=0.D0
        NFLOW(I)=0.D0
      END DO

      IF (NSTATV.GE.7) THEN
        DO I=1,6
          XOLD(I)=STATEV(I+1)
        END DO
      END IF
      IF (NSTATV.GE.13) THEN
        DO I=1,6
          EPOLD(I)=STATEV(I+7)
        END DO
      END IF

      DO I=1,NTENS
        STRIAL(I)=STRESS(I)
        DO J=1,NTENS
          STRIAL(I)=STRIAL(I)+DDSDDE(I,J)*DSTRAN(J)
        END DO
      END DO

      DO I=1,NTENS
        STRESS(I)=STRIAL(I)
      END DO

      MEAN=(STRIAL(1)+STRIAL(2)+STRIAL(3))/3.D0
      ETA(1)=STRIAL(1)-MEAN-XOLD(1)
      ETA(2)=STRIAL(2)-MEAN-XOLD(2)
      ETA(3)=STRIAL(3)-MEAN-XOLD(3)
      ETA(4)=STRIAL(4)-XOLD(4)
      ETA(5)=STRIAL(5)-XOLD(5)
      ETA(6)=STRIAL(6)-XOLD(6)

      QEQ=ETA(1)*ETA(1)+ETA(2)*ETA(2)+ETA(3)*ETA(3)
      QEQ=QEQ+2.D0*(ETA(4)*ETA(4)+ETA(5)*ETA(5)
     1        +ETA(6)*ETA(6))
      QEQ=DSQRT(1.5D0*QEQ)

      IF (QEQ.GT.TINY) THEN
        DO I=1,6
          NFLOW(I)=1.5D0*ETA(I)/QEQ
        END DO
      END IF

      RISO=0.D0
      IF (STATEV(1).GT.0.D0) THEN
        RISO=QISO*(1.D0-DEXP(-BISO*STATEV(1)))
      END IF

      FVAL=QEQ-SIGY-RISO
      DP=0.D0

      DO I=1,6
        XNEW(I)=XOLD(I)
        EPNEW(I)=EPOLD(I)
      END DO

      IF (FVAL.GT.1.D-8 .AND. QEQ.GT.TINY) THEN
        HARD=3.D0*MU+(2.D0/3.D0)*CKIN
        HARD=HARD+QISO*BISO*DEXP(-BISO*STATEV(1))
        DPALG=FVAL/HARD
        IF (KVIS.GT.TINY) THEN
          DPRATE=DTIME*(FVAL/KVIS)**MVIS
        ELSE
          DPRATE=DPALG
        END IF
        DP=DMIN1(DPALG,DPRATE,DPMAX)
        IF (DP.LT.0.D0) DP=0.D0

        DO I=1,6
          STRESS(I)=STRIAL(I)-2.D0*MU*DP*NFLOW(I)
          XNEW(I)=(XOLD(I)+(2.D0/3.D0)*CKIN*DP*NFLOW(I))
     1            /(1.D0+GKIN*DP)
          EPNEW(I)=EPOLD(I)+DP*NFLOW(I)
        END DO
      END IF

      IF (NSTATV.GE.1) STATEV(1)=STATEV(1)+DP
      IF (NSTATV.GE.7) THEN
        DO I=1,6
          STATEV(I+1)=XNEW(I)
        END DO
      END IF
      IF (NSTATV.GE.13) THEN
        DO I=1,6
          STATEV(I+7)=EPNEW(I)
        END DO
      END IF
      IF (NSTATV.GE.14) THEN
        STATEV(14)=QISO*(1.D0-DEXP(-BISO*STATEV(1)))
      END IF
      IF (NSTATV.GE.15) STATEV(15)=DP

      SSE=0.D0
      SPD=0.D0
      DO I=1,NTENS
        SSE=SSE+0.5D0*STRESS(I)*DSTRAN(I)
      END DO

      RETURN
      END

C ======================================================================
C SDVINI: Initialize state-dependent variables from extracted cycle-19
C         data for exact-state injection testing.
C ======================================================================

      SUBROUTINE SDVINI(STATEV,COORDS,NSTATV,NCRDS,ORNT,LAYER,KSPT)

      INCLUDE 'ABA_PARAM.INC'

      DIMENSION STATEV(NSTATV),COORDS(NCRDS),ORNT(3,3)

C     Exact cycle-19 averaged state extracted from ODB (May 9, 2026)
C     Source: chaboche_vp_v1_cyclic_eps005_20cycles.odb
C     Frame time: 18.990257 (error: 9.7 ms from target 19.0)

      STATEV(1)  = 0.13485494256019592D0  ! STATEV1: accumulated viscoplastic strain
      STATEV(2)  = -85.89347076416016D0   ! STATEV2: backstress X1
      STATEV(3)  = 42.94673538208008D0    ! STATEV3: backstress X2
      STATEV(4)  = 42.94673538208008D0    ! STATEV4: backstress X3
      STATEV(5)  = -2.0947599256398208D-15  ! STATEV5: isotropic hardening (negligible)
      STATEV(6)  = 2.2161001084864085D-16   ! STATEV6: (negligible)
      STATEV(7)  = -2.4222445285629373D-15  ! STATEV7: (negligible)
      STATEV(8)  = -0.0017928289016708732D0 ! STATEV8: viscoplastic strain Ep1
      STATEV(9)  = 0.0008964144508354366D0  ! STATEV9: viscoplastic strain Ep2
      STATEV(10) = 0.0008964144508354366D0  ! STATEV10: viscoplastic strain Ep3
      STATEV(11) = -3.3179593353900074D-19  ! STATEV11: (negligible)
      STATEV(12) = -2.99851439388397D-19    ! STATEV12: (negligible)
      STATEV(13) = -1.0530329811066763D-19  ! STATEV13: (negligible)
      STATEV(14) = 1.3440132141113281D0     ! STATEV14: isotropic hardening RISO
      STATEV(15) = 0.0D0                    ! STATEV15: incremental plastic strain (reset to 0)

      RETURN
      END
