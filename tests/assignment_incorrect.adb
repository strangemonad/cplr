procedure ASSIGNMENT_INCORRECT is
	I: INTEGER;
begin
	-- expression on left
	I+2 := 3; --gnat says missing :=

	-- can't have multiple assignments in one statement
	I := I := 1; --gnat says missing ;
end ASSIGNMENT_INCORRECT;
