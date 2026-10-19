ALTER TABLE comment ADD COLUMN author_id integer REFERENCES "user" (id);
