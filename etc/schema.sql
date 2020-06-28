USE abreports;

create table sellers (
   user varchar(30) not null,
   location varchar(50) not null,
   country varchar(50),
   primary key(user)
);

create table auctions (
   id int not null,
   category varchar(30) not null,
   section varchar(50) not null,
   link varchar(100) not null,
   description varchar(100) not null,
   pic bool not null default 0,
   seller varchar(30) not null,
   closes varchar(10),
   bids int,
   price float,
   reserve varchar(5),
   shipping varchar(10),
   closed bool not null default 0,
   winner varchar(30),
   details text,
   primary key(id, category)
);

