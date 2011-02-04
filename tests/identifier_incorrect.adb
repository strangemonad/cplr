-- incorrect Identifiers

procedure IDENTIFIER_INCORRECT is
	_X: INTEGER; -- identifier cannot begin (or end) with an underscore
	X_: INTEGER;
	X__X: INTEGER; -- identifier cannot contain adjacent underscores
	NULL: INTEGER; -- identifier cannot be reserved word
begin
	null;
end IDENTIFIER_INCORRECT;
