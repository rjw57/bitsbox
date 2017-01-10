drop table if exists cabinets;
create table cabinets (
    id integer primary key autoincrement,
    name text not null,
    layout json not null
);

drop table if exists drawers;
create table drawers (
    id integer primary key autoincrement,
    label text not null,
    cabinet_id integer not null,
    location text not null,

    foreign key(cabinet_id) references cabinets(id)
);

drop table if exists collections;
create table collections (
    id integer primary key autoincrement,
    name text not null,
    description text not null,
    contents_count integer not null,
    drawer_id integer not null,

    foreign key(drawer_id) references drawers(id)
);

