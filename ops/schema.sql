-- Local synthetic evidence with indexed time/status queries. Created by Jason Stys.
-- BEGIN CODE MAP (generated; python scripts/code_map.py)
-- table: attempts — line 13
-- column: id — line 14
-- column: at_ms — line 15
-- column: duration_us — line 16
-- column: status — line 17
-- column: trace_id — line 18
-- column: span_id — line 19
-- column: payload — line 22
-- table: reports — line 22
-- END CODE MAP
CREATE TABLE attempts (
    id INTEGER PRIMARY KEY,
    at_ms INTEGER NOT NULL,
    duration_us INTEGER NOT NULL CHECK (duration_us >= 0),
    status INTEGER NOT NULL CHECK (status BETWEEN 0 AND 599),
    trace_id TEXT NOT NULL,
    span_id TEXT NOT NULL
);
CREATE INDEX attempt_time_status ON attempts (at_ms, status);
CREATE TABLE reports (id INTEGER PRIMARY KEY, payload TEXT NOT NULL);
