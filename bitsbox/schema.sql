-- A cabinet will have a pre-existing "layout". The layout provides "items"
-- based on the CSS flex box model. The spec here is a JSON document containing
-- layout objects. A layout object is as follows:
--
-- {
--   type: <LayoutType>,
--   style: <string>, // extra CSS to apply to this layout
--   class: <string>, // extra classes (space separated)
-- }
--
-- CSS properities useful to layout are as follows:
--
-- flex-flow
-- align-items
-- align-content
-- justify-content
--
-- LayoutType is either "container" or "item". A "contenainer" has the following
-- fields:
--
-- {
--   children: [<Layout>] // child elements of the layout
-- }
--
-- An "item" is the leaf node of the tree and contains no additional fields.
--
-- Each item is uniquely specified by a "path" which if an array giving 0-based
-- indices into children array for each container.

drop table if exists layouts;
create table layouts (
    id integer primary key autoincrement,
    name text not null, -- human-friendly name for the layout
    spec json not null
);

drop table if exists layout_items;
create table layout_items (
    id integer primary key autoincrement,
    layout_id integer not null, -- layout this item belongs to
    spec_item_path json not null, -- path of corresponding item in layout's spec

    foreign key(layout_id) references layouts(id)
);

-- A cabinet has a name and a layout.
drop table if exists cabinets;
create table cabinets (
    id integer primary key autoincrement,
    name text not null,
    layout_id integer not null,

    foreign key(layout_id) references layouts(id)
);

-- Locations within cabinets
drop table if exists locations;
create table locations (
    id integer primary key autoincrement,
    cabinet_id integer not null,
    layout_item_id integer not null,

    foreign key(cabinet_id) references cabinets(id),
    foreign key(layout_item_id) references layout_items(id)
);

-- Drawers exist within cabinets at a given location. An "orphan" drawer is one
-- which is in no location. Each drawer has a label.
drop table if exists drawers;
create table drawers (
    id integer primary key autoincrement,
    label text not null,
    location_id integer,

    foreign key(location_id) references locations(id)
);

-- A collection exists (optionally) within a drawer. More than one collection
-- may be within a drawer.
drop table if exists collections;
create table collections (
    id integer primary key autoincrement,
    name text not null,
    description text not null,
    contents_count integer not null,
    drawer_id integer,

    foreign key(drawer_id) references drawers(id)
);

