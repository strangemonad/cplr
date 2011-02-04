package PROCEDURE_INCORRECT is
	procedure P1(); -- can't have emply param list
	procedure P2(INTEGER); -- param name must be specified
	procedure P3(I1: out in INTEGER); -- in out, not out in

end PROCEDURE_INCORRECT;
