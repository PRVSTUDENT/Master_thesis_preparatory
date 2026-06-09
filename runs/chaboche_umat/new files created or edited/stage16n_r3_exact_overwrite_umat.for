C ======================================================================
C STAGE16N_NEML_EQUIVALENT_CHABOCHE_UMAT.FOR
C
C Abaqus UMAT for Stage 16N.
C
C This is a NEML-equivalent Chaboche benchmark UMAT for the Stage 16
C plate-with-hole geometry. It follows the Stage 15 P2 material definition:
C   E = 200000 MPa, nu = 0.3, yield = 100 MPa
C   Voce isotropic hardening: Q = 50 MPa, b = 5
C   three nonlinear Chaboche backstresses:
C     C_i     = [80000, 14000, 3333] MPa
C     gamma_i = [900, 1500, 1]
C
C State variable layout:
C   STATEV(1)      accumulated plastic strain alpha
C   STATEV(2:7)    backstress 1, Abaqus order 11,22,33,12,13,23
C   STATEV(8:13)   backstress 2, Abaqus order 11,22,33,12,13,23
C   STATEV(14:19)  backstress 3, Abaqus order 11,22,33,12,13,23
C   STATEV(20:25)  plastic strain tensor, Abaqus order 11,22,33,12,13,23
C   STATEV(26)     isotropic hardening R
C   STATEV(27)     last plastic multiplier increment
C ======================================================================
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

      DOUBLE PRECISION E,NU,SIGY,QISO,BISO,MU,LAM,TINY
      DOUBLE PRECISION C1,C2,C3,G1,G2,G3,MEAN,QEQ,RISO,FVAL
      DOUBLE PRECISION HARD,DPALG,DP,DPMAX
      DOUBLE PRECISION STRIAL(6),ETA(6),NFLOW(6),EPOLD(6),EPNEW(6)
      DOUBLE PRECISION X1OLD(6),X2OLD(6),X3OLD(6)
      DOUBLE PRECISION X1NEW(6),X2NEW(6),X3NEW(6),XTOT(6)
      INTEGER I,J

      CALL STAGE16N_R3E_EXACT_OVERWRITE(STATEV,NSTATV,
     1 NOEL,NPT,JSTEP,KINC,TIME,PROPS,NPROPS)

      TINY = 1.D-12
      DPMAX = 5.D-4

      E     = PROPS(1)
      NU    = PROPS(2)
      SIGY  = PROPS(3)
      QISO  = PROPS(4)
      BISO  = PROPS(5)
      C1    = PROPS(6)
      G1    = PROPS(7)
      C2    = PROPS(8)
      G2    = PROPS(9)
      C3    = PROPS(10)
      G3    = PROPS(11)

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
        X1OLD(I)=0.D0
        X2OLD(I)=0.D0
        X3OLD(I)=0.D0
        X1NEW(I)=0.D0
        X2NEW(I)=0.D0
        X3NEW(I)=0.D0
        XTOT(I)=0.D0
        EPOLD(I)=0.D0
        EPNEW(I)=0.D0
        ETA(I)=0.D0
        NFLOW(I)=0.D0
      END DO

      IF (NSTATV.GE.19) THEN
        DO I=1,6
          X1OLD(I)=STATEV(I+1)
          X2OLD(I)=STATEV(I+7)
          X3OLD(I)=STATEV(I+13)
        END DO
      END IF
      IF (NSTATV.GE.25) THEN
        DO I=1,6
          EPOLD(I)=STATEV(I+19)
        END DO
      END IF

      DO I=1,NTENS
        STRIAL(I)=STRESS(I)
        DO J=1,NTENS
          STRIAL(I)=STRIAL(I)+DDSDDE(I,J)*DSTRAN(J)
        END DO
        STRESS(I)=STRIAL(I)
      END DO

      DO I=1,6
        XTOT(I)=X1OLD(I)+X2OLD(I)+X3OLD(I)
      END DO

      MEAN=(STRIAL(1)+STRIAL(2)+STRIAL(3))/3.D0
      ETA(1)=STRIAL(1)-MEAN-XTOT(1)
      ETA(2)=STRIAL(2)-MEAN-XTOT(2)
      ETA(3)=STRIAL(3)-MEAN-XTOT(3)
      ETA(4)=STRIAL(4)-XTOT(4)
      ETA(5)=STRIAL(5)-XTOT(5)
      ETA(6)=STRIAL(6)-XTOT(6)

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
        X1NEW(I)=X1OLD(I)
        X2NEW(I)=X2OLD(I)
        X3NEW(I)=X3OLD(I)
        EPNEW(I)=EPOLD(I)
      END DO

      IF (FVAL.GT.1.D-8 .AND. QEQ.GT.TINY) THEN
        HARD=3.D0*MU+(2.D0/3.D0)*(C1+C2+C3)
        HARD=HARD+QISO*BISO*DEXP(-BISO*STATEV(1))
        DPALG=FVAL/HARD
        DP=DMIN1(DPALG,DPMAX)
        IF (DP.LT.0.D0) DP=0.D0

        DO I=1,6
          STRESS(I)=STRIAL(I)-2.D0*MU*DP*NFLOW(I)
          X1NEW(I)=(X1OLD(I)+(2.D0/3.D0)*C1*DP*NFLOW(I))
     1            /(1.D0+G1*DP)
          X2NEW(I)=(X2OLD(I)+(2.D0/3.D0)*C2*DP*NFLOW(I))
     1            /(1.D0+G2*DP)
          X3NEW(I)=(X3OLD(I)+(2.D0/3.D0)*C3*DP*NFLOW(I))
     1            /(1.D0+G3*DP)
          EPNEW(I)=EPOLD(I)+DP*NFLOW(I)
        END DO
      END IF

      IF (NSTATV.GE.1) STATEV(1)=STATEV(1)+DP
      IF (NSTATV.GE.19) THEN
        DO I=1,6
          STATEV(I+1)=X1NEW(I)
          STATEV(I+7)=X2NEW(I)
          STATEV(I+13)=X3NEW(I)
        END DO
      END IF
      IF (NSTATV.GE.25) THEN
        DO I=1,6
          STATEV(I+19)=EPNEW(I)
        END DO
      END IF
      IF (NSTATV.GE.26) THEN
        STATEV(26)=QISO*(1.D0-DEXP(-BISO*STATEV(1)))
      END IF
      IF (NSTATV.GE.27) STATEV(27)=DP

      SSE=0.D0
      SPD=0.D0
      DO I=1,NTENS
        SSE=SSE+0.5D0*STRESS(I)*DSTRAN(I)
      END DO

      RETURN
      END

C ======================================================================
C Stage 16N-R3E restart-preserved exact material-memory overwrite.
C Reads direct-access binary state records generated by
C stage16n_extract_exact_state_for_reinjection.py.
C Only independent material memory is overwritten: STATEV(1:25).
C STATEV(26) and STATEV(27) are not read from the table.
C ======================================================================

      SUBROUTINE STAGE16N_READ_OVERWRITE_STATE(NOEL,NPT,VALS,FOUND)
      INCLUDE 'ABA_PARAM.INC'
      INTEGER NOEL,NPT,FOUND,RECNO,UNITNO,IOS,I
      DOUBLE PRECISION VALS(33)
      CHARACTER*512 STATEBIN

      FOUND=0
      DO I=1,33
        VALS(I)=0.D0
      END DO

      CALL GETENV('STAGE16N_OVERWRITE_STATE_BIN',STATEBIN)
      IF (STATEBIN.EQ.' ') STATEBIN='state.bin'

      RECNO=(NOEL-1)*8+NPT
      UNITNO=10000+NOEL*10+NPT
      OPEN(UNIT=UNITNO,FILE=STATEBIN,STATUS='OLD',
     1 ACCESS='DIRECT',FORM='UNFORMATTED',RECL=66,IOSTAT=IOS)
      IF (IOS.NE.0) THEN
        WRITE(6,*) 'STAGE16N_R3E ERROR: cannot open state binary'
        WRITE(6,*) STATEBIN
        CALL XIT
      END IF

      READ(UNITNO,REC=RECNO,IOSTAT=IOS) (VALS(I),I=1,33)
      CLOSE(UNITNO)
      IF (IOS.NE.0) THEN
        WRITE(6,*) 'STAGE16N_R3E ERROR: cannot read state record',
     1             NOEL,NPT,RECNO,IOS
        CALL XIT
      END IF

      FOUND=1
      RETURN
      END

      SUBROUTINE STAGE16N_R3E_EXACT_OVERWRITE(STATEV,NSTATV,
     1 NOEL,NPT,JSTEP,KINC,TIME,PROPS,NPROPS)
      INCLUDE 'ABA_PARAM.INC'
      DIMENSION STATEV(NSTATV),JSTEP(4),TIME(2),PROPS(NPROPS)
      INTEGER NSTATV,NOEL,NPT,KINC,NPROPS
      INTEGER TARGET_STEP,FOUND,I
      DOUBLE PRECISION VALS(33),CHECK_TIME,TOL
      CHARACTER*80 TARGET_TEXT,CHECK_TEXT

      TARGET_STEP=-1
      CHECK_TIME=-1.D0
      CALL GETENV('STAGE16N_OVERWRITE_TARGET_STEP',TARGET_TEXT)
      CALL GETENV('STAGE16N_OVERWRITE_CHECK_TIME',CHECK_TEXT)
      IF (TARGET_TEXT.NE.' ') READ(TARGET_TEXT,*,ERR=90) TARGET_STEP
      IF (CHECK_TEXT.NE.' ') READ(CHECK_TEXT,*,ERR=90) CHECK_TIME
90    CONTINUE

      TOL=1.D-6
      IF (TARGET_STEP.LT.0) RETURN
      IF (JSTEP(1).NE.TARGET_STEP) RETURN
      IF (KINC.NE.0) RETURN
      IF (DABS(TIME(1)).GT.TOL) RETURN
      IF (CHECK_TIME.GE.0.D0 .AND. DABS(TIME(2)-CHECK_TIME).GT.TOL)
     1 RETURN

      CALL STAGE16N_READ_OVERWRITE_STATE(NOEL,NPT,VALS,FOUND)
      IF (FOUND.EQ.0) THEN
        WRITE(6,*) 'STAGE16N_R3E missing overwrite state',NOEL,NPT
        CALL XIT
      END IF

      DO I=1,NSTATV
        IF (I.LE.25) STATEV(I)=VALS(I+6)
      END DO

      IF ((NOEL.LE.4 .AND. NPT.LE.2) .OR.
     1    (NOEL.EQ.278 .AND. NPT.EQ.1)) THEN
        WRITE(6,*) 'STAGE16N_R3E_OVERWRITE',
     1      ' NOEL=',NOEL,' NPT=',NPT,' KSTEP=',JSTEP(1),
     2      ' KINC=',KINC,' TIME1=',TIME(1),' TIME2=',TIME(2),
     3      ' STATEV1=',STATEV(1),' STATEV8=',STATEV(8),
     4      ' STATEV11=',STATEV(11)
      END IF

      RETURN
      END

      SUBROUTINE SIGINI(SIGMA,COORDS,NTENS,NCRDS,NOEL,NPT,
     1 LAYER,KSPT,LREBAR,NAMES)
      INCLUDE 'ABA_PARAM.INC'
      DIMENSION SIGMA(NTENS),COORDS(NCRDS)
      CHARACTER*80 NAMES(2)
      RETURN
      END

      SUBROUTINE SDVINI(STATEV,COORDS,NSTATV,NCRDS,NOEL,NPT,
     1 LAYER,KSPT)
      INCLUDE 'ABA_PARAM.INC'
      DIMENSION STATEV(NSTATV),COORDS(NCRDS)
      RETURN
      END

