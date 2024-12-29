CREATE EXTENSION "uuid-ossp";


CREATE TABLE users (
  uid UUID NOT NULL DEFAULT uuid_generate_v4 (),
  username TEXT,
  password_hash TEXT,
  banned BOOL DEFAULT false,
  rigths TEXT[] DEFAULT '{}',
  lists JSONB DEFAULT '{"favorites": [], "likes": []}',
  waiting JSONB DEFAULT '{"registration": false, "aproval": false}',
  relationship JSONB DEFAULT '{"black-list": []}'
  );

CREATE TABLE packs (
  name TEXT,
  codename TEXT,
  image TEXT,
  path TEXT PRIMARY KEY,
  hidden BOOL DEFAULT false,
  freezed BOOL DEFAULT false,
  last_update TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  likes INT DEFAULT 0,
  favorites INT DEFAULT 0,
  owner TEXT,
  readactors TEXT[] DEFAULT '{}'
  );

CREATE TABLE tables (
  name TEXT,
  codename TEXT,
  upath TEXT PRIMARY KEY,
  common JSONB,
  data JSONB,
  );

CREATE TABLE images (
  name TEXT,
  codename TEXT,
  owner TEXT,
  data BYTEA
  );

CREATE OR REPLACE FUNCTION add_user(
  username TEXT, 
  password_hash TEXT, 
  aprove BOOL DEFAULT false, 
  registration BOOL DEFAULT false
)

RETURNS VOID AS $$
  BEGIN
   INSERT INTO users (username, password_hash, waiting)
 VALUES (
   username, 
   password_hash, 
   jsonb_build_object(
     'registration', registration,
     'aproval', aprove
        )
      );
  END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE VIEW banned_users AS
  SELECT * FROM users WHERE banned = true;

CREATE OR REPLACE VIEW users_waiting_aprove AS
  SELECT * FROM users WHERE (waiting->>'aproval')::bool = true;

CREATE OR REPLACE VIEW users_waiting_register AS
  SELECT * FROM users WHERE (waiting->>'registration')::bool = true;


SELECT add_user('User-1', '');
SELECT add_user('User-2', '', aprove => true);
SELECT add_user('Test-user', '', registration => true);
SELECT add_user('admin', '');

UPDATE users SET banned = true WHERE username = 'User-1';
