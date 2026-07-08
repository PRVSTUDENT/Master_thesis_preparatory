C Stage 16N exact state reinjection hooks.
C
C The preparation script copies these hooks into a case-specific UMAT file.
C The hooks read a direct-access binary state file through the environment
C variable STAGE16N_STATE_BIN.  Each record contains:
C S1,S2,S3,S4,S5,S6,SDV1,...,SDV27
C
C Record number convention:
C   RECNO = (NOEL - 1) * 8 + NPT
C because the Stage 16N C3D8 mesh uses 8 integration points per element.

      SUBROUTINE STAGE16N_READ_STATE(NOEL,NPT,VALS,FOUND)
      INCLUDE 'ABA_PARAM.INC'
      INTEGER NOEL,NPT,FOUND,RECNO,UNITNO,IOS,I
      DOUBLE PRECISION VALS(33)
      CHARACTER*512 STATEBIN

      FOUND=0
      DO I=1,33
        VALS(I)=0.D0
      END DO

      CALL GETENV('STAGE16N_STATE_BIN',STATEBIN)
      IF (STATEBIN.EQ.' ') STATEBIN='state.bin'

      RECNO=(NOEL-1)*8+NPT
      UNITNO=10000+NOEL*10+NPT
      OPEN(UNIT=UNITNO,FILE=STATEBIN,STATUS='OLD',
     1 ACCESS='DIRECT',FORM='UNFORMATTED',RECL=66,IOSTAT=IOS)
      IF (IOS.NE.0) THEN
        WRITE(6,*) 'STAGE16N ERROR: cannot open state binary'
        WRITE(6,*) STATEBIN
        CALL XIT
      END IF

      READ(UNITNO,REC=RECNO,IOSTAT=IOS) (VALS(I),I=1,33)
      CLOSE(UNITNO)
      IF (IOS.NE.0) THEN
        WRITE(6,*) 'STAGE16N ERROR: cannot read state record',
     1             NOEL,NPT,RECNO,IOS
        CALL XIT
      END IF

      FOUND=1
      RETURN
      END

      SUBROUTINE SIGINI(SIGMA,COORDS,NTENS,NCRDS,NOEL,NPT,
     1 LAYER,KSPT,LREBAR,NAMES)
      INCLUDE 'ABA_PARAM.INC'
      DIMENSION SIGMA(NTENS),COORDS(NCRDS)
      CHARACTER*80 NAMES(2)
      INTEGER FOUND,I
      DOUBLE PRECISION VALS(33)

      CALL STAGE16N_READ_STATE(NOEL,NPT,VALS,FOUND)
      IF (FOUND.EQ.0) THEN
        WRITE(6,*) 'STAGE16N SIGINI missing NOEL,NPT:', NOEL,NPT
        CALL XIT
      END IF
      DO I=1,NTENS
        IF (I.LE.6) SIGMA(I)=VALS(I)
      END DO
      RETURN
      END

      SUBROUTINE SDVINI(STATEV,COORDS,NSTATV,NCRDS,NOEL,NPT,
     1 LAYER,KSPT)
      INCLUDE 'ABA_PARAM.INC'
      DIMENSION STATEV(NSTATV),COORDS(NCRDS)
      INTEGER FOUND,I
      DOUBLE PRECISION VALS(33)

      CALL STAGE16N_READ_STATE(NOEL,NPT,VALS,FOUND)
      IF (FOUND.EQ.0) THEN
        WRITE(6,*) 'STAGE16N SDVINI missing NOEL,NPT:', NOEL,NPT
        CALL XIT
      END IF
      DO I=1,NSTATV
        IF (I.LE.27) STATEV(I)=VALS(I+6)
      END DO
      RETURN
      END
