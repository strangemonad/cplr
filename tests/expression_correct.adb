procedure EXPRESSION_CORRECT is
	I1: INTEGER;
	B1: BOOLEAN;
	S1: constant STRING := "ABC" & "DEF";
begin
	I1 := +1;
	I1 := -1;
	I1 := 1 + 1;
	I1 := 2 - 1;
	I1 := 2 * 2;
	I1 := 4 / 2;
	I1 := 5 rem 2;
	I1 := 5 mod 3;
	I1 := 2 ** 3;
	I1 := -2**3; -- means -(2**3)

	B1 := 2 = 2;
	B1 := 2 /= 2;
	B1 := 2 < 2;
	B1 := 2 > 2;
	B1 := 2 <= 2;
	B1 := 2 >= 2;

	B1 := not TRUE;
	B1 := TRUE and FALSE;
	B1 := TRUE or FALSE;
	B1 := TRUE xor TRUE;

	-- BOOLEAN operators lower precedence than relational operators
	B1 := 1<2 and 2<4;

	-- BOOLEAN operators mustn't be mixed
	B1 := TRUE and TRUE and FALSE;
	B1 := (TRUE and TRUE) or FALSE;
	-- but not is higher than the others
	B1 := not TRUE and FALSE;

	-- short circuit BOOLEAN operators
	B1 := TRUE and then FALSE;
	B1 := FALSE or else TRUE;

	-- nested expression (parentheses)
	I1 := ((1+2) * (3+4)) ** (4/2);

	-- there should be more expression tests
end EXPRESSION_CORRECT;
