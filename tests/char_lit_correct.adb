-- correct CHARACTER literals

with TEXT_IO;
procedure CHAR_LIT_CORRECT is
	use TEXT_IO;

	C: CHARACTER;
begin
	C := '''; -- ' literal
	C := ' '; -- space is a graphic character
	-- Case of CHARACTER literals must be preserved
	if 'a' = 'A' then
		PUT("FAILED: CHARACTER literal case not preserved");
		NEW_LINE;
	end if; 
	-- tick preceeding aggregate beginning with CHARACTER literal
	-- (easy for a scanner to think '(' is a CHARACTER literal)
	C := CHARACTER'('a');
end CHAR_LIT_CORRECT;
