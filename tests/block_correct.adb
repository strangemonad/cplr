procedure BLOCK_CORRECT is
begin
	declare
		I: INTEGER;
	begin
		null;
	end;

	-- named block
	BLOCK: declare
		I: INTEGER;
	begin
		null;
	end BLOCK;

	-- nested blocks
	declare
		I:INTEGER;
	begin
		declare
			I: INTEGER;
		begin
			null;
		end;
	end;

	-- declare is optional
	begin
		null;
	end;

	-- declare can be empty
	declare
	begin
		null;
	end;
end BLOCK_CORRECT;
