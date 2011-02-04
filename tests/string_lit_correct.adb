-- correct STRING literals

procedure STRING_LIT_CORRECT is
	S1: constant STRING := "a""a"; -- double quote in STRING literal
	S2: constant STRING := "a a"; -- space in STRING literal
begin
	null;
end STRING_LIT_CORRECT;
