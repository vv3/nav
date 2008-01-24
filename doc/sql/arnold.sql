CREATE TABLE blocked_reason (
blocked_reasonid SERIAL PRIMARY KEY,
name VARCHAR,
comment VARCHAR
);

CREATE TABLE identity (
identityid SERIAL PRIMARY KEY,
mac VARCHAR NOT NULL, -- MAC-address of computer
blocked_status VARCHAR CHECK (blocked_status='enabled' OR blocked_status='disabled'),
blocked_reasonid INT REFERENCES blocked_reason ON UPDATE CASCADE ON DELETE SET NULL, -- reason of block
swportid INT NOT NULL, -- FK to swport-table. We find sysname,ip,module and port from this
ip INET, -- current ip of computer
dns VARCHAR, -- current dns-name of computer
netbios VARCHAR, -- current netbios-name of computer
starttime TIMESTAMP NOT NULL, -- time of first event on this computer-swport combo
lastchanged TIMESTAMP NOT NULL, -- time of last current event on this computer-swport combo
autoenable TIMESTAMP, -- time for autoenable
autoenablestep INT, -- number of days to wait for autoenable
mail VARCHAR, -- the mail address the warning was sent to
orgid VARCHAR,
determined CHAR(1), -- set to y if this is mac/port combo is blocked with the -d option.
UNIQUE (mac,swportid)
);

CREATE TABLE event (
eventid SERIAL PRIMARY KEY,
identityid INT REFERENCES identity ON UPDATE CASCADE ON DELETE CASCADE,
event_comment VARCHAR,
blocked_status VARCHAR CHECK (blocked_status='enabled' OR blocked_status='disabled'),
blocked_reasonid INT REFERENCES blocked_reason ON UPDATE CASCADE ON DELETE SET NULL, -- reason of block
eventtime TIMESTAMP NOT NULL,
autoenablestep INT,
username VARCHAR NOT NULL
);

-- A block, of lack of better name, is a run where we do automatic blocking 
-- of computers based on input ip-list.
CREATE TABLE block (
blockid SERIAL PRIMARY KEY,
blocktitle VARCHAR NOT NULL, -- title of block
blockdesc VARCHAR, -- description of block
mailfile VARCHAR, -- path to mailfile to use to send mail when blocking
reasonid INT REFERENCES blocked_reason ON UPDATE CASCADE ON DELETE CASCADE,
determined CHAR(1), -- if set: keep old ports blocked when pursuing
incremental CHAR(1), -- if set: increase number of days to block incrementally
blocktime INT NOT NULL, -- days from block to autoenable
active CHAR(1) CHECK (active='y' OR active='n'), -- if set to n will not do blocking of this kind
lastedited TIMESTAMP NOT NULL, -- timestamp of last time this block was edited
lastedituser VARCHAR NOT NULL, -- username of user who last edited this block
inputfile VARCHAR, -- path to file where list of ip-adresses is, if applicable
activeonvlans VARCHAR -- a string with comma-separated vlan-numbers
);

