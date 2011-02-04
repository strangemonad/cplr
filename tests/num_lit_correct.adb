-- correct INTEGER and FLOAT literals

procedure NUM_LIT_CORRECT is
	X: INTEGER;
	Y: FLOAT;
begin
	Y := 1.0e1_0; -- underscore in exponent
	Y := 1.0e+1; -- positive exponent
end NUM_LIT_CORRECT;
