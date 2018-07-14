CREATE SCHEMA fox_cub;


CREATE TABLE fox_cub.sport_type (
    id int NOT NULL PRIMARY KEY,
    name varchar(128),
);


CREATE TABLE fox_cub.tournament (
    id int NOT NULL PRIMARY KEY,
    name varchar(128),
);


CREATE TABLE fox_cub.stage (
    id int NOT NULL PRIMARY KEY,
    tournament_id integer not null references fox_cub.tournament(id),
    date daterange,
    name varchar(128)
);


CREATE TABLE fox_cub.team (
    id int NOT NULL PRIMARY KEY,
    sport_id integer not null references fox_cub.sport_type(id)
    name varchar(128)
);


CREATE TABLE fox_cub.game (
    /* Related to team sport */
    id int NOT NULL PRIMARY KEY,
    date timestamp,
    home_side integer not null references fox_cub.team(id),
    away_side integer not null references fox_cub.team(id)
);


CREATE TABLE fox_cub.player (
    /* Individual performance */
    id int NOT NULL PRIMARY KEY,
    sport_id integer not null references fox_cub.sport_type(id),
    full_name varchar(256)
);


CREATE TABLE fox_cub.user (
    id int NOT NULL PRIMARY KEY,
    username varchar(256) NOT NULL,
    password varchar(256) NOT NULL,
    salt varchar(256) NOT NULL,
)
