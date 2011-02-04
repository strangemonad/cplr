procedure LOOP_INCORRECT is
begin
	-- can't be empty
	loop
	end loop;

	-- labelled loops must repeat label at end
	OUTER: loop
		null;
	end loop;
end LOOP_INCORRECT;
