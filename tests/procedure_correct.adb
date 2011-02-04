package body PROCEDURE_CORRECT is
	I1, I2: INTEGER;

	procedure P1 is
	begin
		null;
	end P1;

	procedure P2(I: INTEGER) is
	begin
		null;
	end P2;

	procedure P3(I1, I2: INTEGER) is
	begin
		null;
	end P3;

	procedure P4(I1: INTEGER; I2: INTEGER) is
	begin
		null;
	end P4;

	procedure P5(I1: in INTEGER; I2: out INTEGER; I3: in out INTEGER) is
	begin
		null;
	end P5;

begin
	P1;
	P2(1);
	P3(1, 2);
	P4(1, 2);
	P5(1, I1, I2);
	-- fully specified name
	PROCEDURE_CORRECT.P1;
end PROCEDURE_CORRECT;
