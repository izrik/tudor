
alter table user rename to user2;

# run ./tudor.py --create-db

insert into user (email, hashed_password, is_admin) select email, hashed_password, is_admin from user2;
drop table user2;
