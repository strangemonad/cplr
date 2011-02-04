-- incorrect INTEGER and FLOAT literals

procedure NUM_LIT_INCORRECT is
	X: INTEGER;
	Y: FLOAT;
begin
	X := 1__0; -- two consecutive underscores in a numeral
	X := 1_; -- numeral ending in underscore
	X := _1; -- numeral beginning with underscore

	Y := 1.; -- decimal point without trailing numeral
	Y := .1; -- decimal point without leading numeral
	Y := 1.0 e 10; -- space between constituents of exponent
end NUM_LIT_INCORRECT;
