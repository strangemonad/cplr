package body PROCEDURE_INCORRECT is
	procedure P1() is -- can't have emply param list
	begin
		null;
	end P1;

	procedure P2(INTEGER) is -- param name must be specified
	begin
		null;
	end P2;

	procedure P3(I1: out in INTEGER) is -- in out, not out in
	begin
		null;
	end P3;

begin
	P1(); -- can't have empty param list
	
end PROCEDURE_INCORRECT;
