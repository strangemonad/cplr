-- array types

procedure ARRAY_CORRECT is
	A1: array (INTEGER range 1..6) of INTEGER;
	type INTEGER_VECTOR_6 is array (INTEGER range 1..6) of INTEGER; -- contrained
	type INTEGER_MATRIX_6_6 is array (INTEGER range 1..6, 1..6) of INTEGER; -- contrained two dimensions
	type INTEGER_MATRIX is array (INTEGER range <>, INTEGER range <>) of INTEGER; -- unconstrained
	type AT1 is array (CHARACTER) of INTEGER; -- enumeration bounds
begin
	null;
end;
