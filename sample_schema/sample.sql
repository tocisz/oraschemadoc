/*
 * $Header$
 *
 * Create new user/schema
 */

DEFINE username=&1
DEFINE password=&2

--set term off
set trim on
set linesize 255
set serveroutput on

exec dbms_output.put_line('Running as SYSTEM user');

begin
    execute immediate 'drop user &username cascade';
exception when others then
    dbms_output.put_line('User doesn''t exist - new creation');
end;
/

create user &username
    identified by &password
    default tablespace users
    temporary tablespace temp;
grant create session to &username;
grant resource to &username;
grant unlimited tablespace to &username;
grant CREATE MATERIALIZED VIEW to &username;
grant CREATE VIEW to &username;
ALTER USER &username DEFAULT ROLE ALL;

exec dbms_output.put_line('Connecting and running as new use &username');
connect &username/&password

@sample_tables.sql
@sample_mview.sql
@sample_java.sql
@sample_procedure.sql
@sample_view.sql

set serveroutput off

quit
