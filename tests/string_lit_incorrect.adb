-- incorrect STIRNG literals

procedure STRING_LIT_INCORRECT is
	S1: constant STRING := "a	a"; -- non-graphic character (tab) in STRING literal
	S2: constant STRING := "a
a"; -- newline in STRING literal
	-- unclosed STRING literal (further errors should be detected!)
	S3: constant STRING := "
begin
	null -- this error (missign ;) should be detected
end STRING_LIT_INCORRECT;
