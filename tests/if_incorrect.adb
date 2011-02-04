-- if statements

procedure IF_INCORRECT is
begin
	-- missign statement sequence
	if TRUE then
	end if;

	-- missign ; after statement sequence
	if TRUE then null end if;

	-- elsif after else
	if TRUE then
		null;
	else
		null;
	elsif FALSE then
		null;
	end if;
end IF_INCORRECT;
