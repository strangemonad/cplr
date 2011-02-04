-- correct identifiers

with TEXT_IO; use TEXT_IO;
procedure IDENTIFIER_CORRECT is
	X: INTEGER;
	X_X: INTEGER; -- identifier can contain isolated underscores
	IF5: INTEGER; -- identifier can (properly) contain reserved word and digits
begin
	X := 5;
	-- identifier and reserved word case should not be preserved
	IF x /= 5 THEN
		PUT("FAILED: identifier case is not meant to be preserved");
		NEW_LINE;
	END IF;
end IDENTIFIER_CORRECT;
