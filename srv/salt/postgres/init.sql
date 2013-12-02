DROP TABLE IF EXISTS users;
CREATE TABLE users (
  id SERIAL,
  username VARCHAR(100),
  password VARCHAR(255),
  email VARCHAR(255),
  joined TIMESTAMP
);

DROP TABLE IF EXISTS sites;
CREATE TABLE sites (
  name VARCHAR(255),
  pages INT,
  views INT,
  created TIMESTAMP
);

DROP TABLE IF EXISTS pages;
CREATE TABLE pages (
  id VARCHAR(255), -- <site name>/<path>
  edits INT,
  views INT,
  author INT,
  created TIMESTAMP,
  modified TIMESTAMP
);