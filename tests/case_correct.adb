-- case statement

procedure CASE_CORRECT is
begin
	case TRUE is
	when TRUE => null;
	when others => null;
	end case;

	case 1 is
	when -1|-2|-3|-15..-10 => null;
	when INTEGER range -1000..-200 => null; -- not certain if this is legal
	when POSITIVE => null;
	when others => null;
	end case;
end CASE_CORRECT;
