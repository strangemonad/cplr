-- record

procedure RECORD_CORRECT is
	-- empty record
	type R1 is
	record
		null;
	end record;
	-- simple record
	type R2 is
	record
		I: INTEGER;
	end record;
	--
begin
	null;
end RECORD_CORRECT;
