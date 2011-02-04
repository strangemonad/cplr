package PROCEDURE_CORRECT is
	procedure P1;
	procedure P2(I: INTEGER);
	procedure P3(I1, I2: INTEGER);
	procedure P4(I1: INTEGER; I2: INTEGER);
	procedure P5(I1: in INTEGER; I2: out INTEGER; I3: in out INTEGER);
end PROCEDURE_CORRECT;
