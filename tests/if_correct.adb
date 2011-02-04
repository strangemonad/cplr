-- if statements

procedure IF_CORRECT is
begin
	if TRUE then
		null;
	end if;

	-- simple if statement still requires ; at end of statement sequence
	if TRUE then null; end if;

	if FALSE then
		null;
	else
		null;
	end if;

	if FALSE then
		null;
	elsif FALSE then
		null;
	elsif TRUE then
		null;
	end if;

	if FALSE then
		null;
	elsif FALSE then
		null;
	else
		null;
	end if;
end IF_CORRECT;
