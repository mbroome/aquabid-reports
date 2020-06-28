USE abreports;

create table users (
   user varchar(30) not null,
   location varchar(50) not null,
   primary key(user)
);

create table auctions (
   id varchar(15) not null,
   section varchar(30) not null,
   link varchar(100) not null,
   description varchar(100) not null,
   pic bool not null default 0,
   seller varchar(30) not null,
   closes varchar(10),
   bids int,
   price float,
   reserve varchar(5),
   shipping varchar(10),
   details text,
   primary key(id, section)
);

