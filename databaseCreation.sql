create table main.users
(
    user_id       INTEGER not null
        unique,
    money_balance INTEGER default 0,
    usage_times   INTEGER default 0
);

