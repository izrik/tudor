
alter table user rename to user2;

# run ./tudor.py --create-db

insert into user (email, hashed_password, is_admin) select email, hashed_password, is_admin from user2;
drop table user2;

######

# manually add an authorized user to all tasks

set @user_id = (select id from user where _____ limit 1);
insert into task_user_link (task_id, user_id) select id as task_id, @user_id from task;

