drop materialized view snapshot_mv;
create materialized view snapshot_mv
build immediate refresh complete as
select * from std_table;
/