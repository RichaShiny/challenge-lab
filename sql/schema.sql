PRAGMA foreign_keys = ON;
CREATE TABLE assignments (
 user_id TEXT PRIMARY KEY, variant TEXT NOT NULL CHECK(variant IN ('control','challenge')),
 assigned_at INTEGER NOT NULL, channel TEXT NOT NULL, device TEXT NOT NULL
);
CREATE TABLE events (
 event_id TEXT PRIMARY KEY, user_id TEXT NOT NULL REFERENCES assignments(user_id),
 event_name TEXT NOT NULL CHECK(event_name IN ('session','challenge_complete','purchase','reward','error')),
 occurred_at INTEGER NOT NULL, contribution_cents INTEGER NOT NULL DEFAULT 0
);
CREATE INDEX events_user_time ON events(user_id, occurred_at);
