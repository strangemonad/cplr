package body FUNCTION_CORRECT is
	function F1 return INTEGER is
	begin
		return 1;
	end F1;
	function F2(I1, I2: INTEGER; I3: in INTEGER) return INTEGER is
	begin
		return I1 + I2 + I3;
	end F2;
	function "+"(I1: INTEGER; C1: CHARACTER) return STRING is
	begin
		return "fubar";
	end "+";

begin
	declare
		I: INTEGER;
		S: STRING(1..5);
	begin
		I := F1;
		I := FUNCTION_CORRECT.F1;
		I := F2(F1, 2, I);
		S := 1 + 'c';
	end;
end FUNCTION_CORRECT;
