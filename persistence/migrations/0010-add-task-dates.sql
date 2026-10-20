ALTER TABLE
    task
ADD COLUMN date_created timestamp without time zone,
ADD COLUMN date_last_updated timestamp without time zone;

UPDATE
    task
SET
    date_created = LOCALTIMESTAMP,
    date_last_updated = LOCALTIMESTAMP;

ALTER TABLE
    task
ALTER COLUMN date_created SET NOT NULL,
ALTER COLUMN date_last_updated SET NOT NULL;
