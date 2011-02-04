procedure BLOCK_INCORRECT is
begin
	-- empty block
	declare
	begin
	end;

	-- missing begin
	declare
		I:INTEGER;
	end;
end BLOCK_INCORRECT;
