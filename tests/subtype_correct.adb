procedure SUBTYPE_CORRECT is
	subtype ST1 is INTEGER range 1..10;
	subtype ST2 is INTEGER;
	I: INTEGER range 1..10;
	type MATRIX is array (INTEGER range <>, INTEGER range <>) of INTEGER;
	subtype MATRIX_3 is MATRIX(1..3, 1..3);
	M: MATRIX(1..3, 1..3);
begin
	null;
end;
