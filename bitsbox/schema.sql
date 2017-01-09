drop table if exists boxes;
create table boxes (
    id integer primary key autoincrement,
    title text not null,
    description text not null,
    contents_count integer not null
);
