procedure EXPRESSION_INCORRECT is
	I1: INTEGER;
	B1: BOOLEAN;
begin
	I1 := 1**2**2; -- **, not and, abs are not asscociative
	I1 := abs abs (-2); -- gnat says missing operand for these
	B1 := not not TRUE;
	I1 := 2**-2; -- - is of lower precedence than **
	I1 := abs -2; -- - is of lower precedence that abs
	I1 := 2** abs 2; -- ** and abs cannot be mixed with parenthises
	I1 := 2 * -2; -- - of lower precedence than *, /, mod, and rem
	I1 := 2 / -2;
	I1 := 7 mod -3;
	I1 := 7 rem -3;

	-- logical operators mustn't be mixed
	B1 := TRUE and FALSE or TRUE;
	B1 := TRUE and FALSE and then TRUE;

end EXPRESSION_INCORRECT;
