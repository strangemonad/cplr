-- incorrect CHARACTE literals

procedure CHAR_LIT_CORRECT is
	C: CHARACTER;
begin
	C := '	'; -- non-graphic character (tab)
end CHAR_LIT_CORRECT;
