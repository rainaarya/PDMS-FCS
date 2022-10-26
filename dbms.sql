use website;
create table users(
    First_Name varchar(50) not null,
    Last_Name varchar(50) not null,
    Sex varchar(10) not null,
    Email varchar(50) not null unique,
    Password varchar(50) not null
)
