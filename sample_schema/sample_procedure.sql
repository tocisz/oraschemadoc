create or replace
procedure simple_procedure as
begin
  null;
end simple_procedure;
/

create or replace
procedure procedure1
( param1 in varchar2
, param2 in number
) as
begin
  null;
end procedure1;
/

create or replace
function function1
( param3 out varchar2
, param2 in varchar2
, param1 in varchar2
) return number as
begin
  return null;
end function1;
/