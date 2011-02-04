procedure LOOP_CORRECT is
	N: INTEGER;
begin
	-- simplest loop
	loop
		null;
	end loop;

	while TRUE loop
		null;
	end loop;

	-- for loop can iterate over subtype indication
	for I in INTEGER range 1..10 loop
		null;
	end loop;

	-- range
	for I in 1..10 loop
		null;
	end loop;

	-- or subtype name
	for I in INTEGER loop
		null;
	end loop;

	-- for can be reversed
	for I in reverse 1..10 loop
		null;
	end loop;

	-- exit
	loop
		null;
		exit;
	end loop;

	-- exit with label
	OUTER:loop
		INNER:loop
			exit OUTER;
		end loop INNER;
	end loop OUTER;

	loop
		exit when N = 0;
	end loop;

	OUTER2:loop
		INNER2:loop
			exit OUTER2 when N = 0;
		end loop INNER2;
	end loop OUTER2;
end LOOP_CORRECT;
