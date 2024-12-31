import hashlib
import os
from dotenv import load_dotenv
import psycopg2 as pgs
load_dotenv()

server_addr = os.getenv("DB_SERVER")
server_db_host, server_db_port = server_addr.split(":")
postgres_user = os.getenv("POSTGRES_USER")
postgres_password = os.getenv("POSTGRES_PASSWORD")
postgres_db = os.getenv("POSTGRES_DB")

exworlds_admin_login = os.getenv("EXWORLDS_ADMIN_USERNAME")
exworlds_admin_password = os.getenv("EXWORLDS_ADMIN_PASSWORD")

salt = os.getenv("PASSWORD_SALT")

#print(f"Mongo exworlds database user: {mongo_exowrlds_login}")
print(f"Exworlds admin user {exworlds_admin_login}")


conn = pgs.connect(dbname = "exworlds",
                   user = postgres_user,
                   password = postgres_password,
                   host = server_db_host,
                   port = server_db_port)
cur = conn.cursor()

cur.execute("""
DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS packs CASCADE;
DROP TABLE IF EXISTS tables CASCADE;
DROP TABLE IF EXISTS images CASCADE;
DROP TABLE IF EXISTS notes CASCADE;
DROP TABLE IF EXISTS settings CASCADE;
""")

cur.execute("""
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";


CREATE TABLE IF NOT EXISTS users (
  uid UUID NOT NULL DEFAULT uuid_generate_v4(),
  username TEXT,
  password_hash TEXT,
  banned TIMESTAMP DEFAULT NULL,
  rights TEXT[] DEFAULT '{}',
  lists JSONB DEFAULT '{"favorites": [], "likes": []}',
  waiting JSONB DEFAULT '{"registration": false, "aproval": false}',
  relationship JSONB DEFAULT '{"black-list": []}'
  );

CREATE TABLE IF NOT EXISTS packs (
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

CREATE TABLE IF NOT EXISTS tables (
  name TEXT,
  codename TEXT,
  upath TEXT PRIMARY KEY,
  common JSONB,
  data JSONB
  );

CREATE TABLE IF NOT EXISTS images (
  filename TEXT,
  codename TEXT,
  path TEXT DEFAULT '/',
  owner TEXT,
  data BYTEA
  );

CREATE TABLE IF NOT EXISTS settings (
  key VARCHAR(60) NOT NULL UNIQUE,
  data JSONB NOT NULL,
  last_update TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE OR REPLACE FUNCTION add_user(
  username TEXT, 
  password_hash TEXT, 
  aprove BOOL DEFAULT false, 
  registration BOOL DEFAULT false
) RETURNS VOID AS $$
  DECLARE
    default_rights JSONB;
  BEGIN
    SELECT data INTO default_rights
    FROM settings
    WHERE key = 'default-rights';
    
    IF default_rights IS NULL THEN
        default_rights := '{}';
    END IF;
    
    INSERT INTO users (username, password_hash, waiting, rights)
    VALUES (
      username, 
      password_hash, 
      jsonb_build_object(
        'registration', registration,
        'aproval', aprove
        ),
       (SELECT ARRAY(SELECT jsonb_array_elements_text(default_rights->'value')))
      );
  END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION sync_last_update()
  RETURNS TRIGGER AS $$
  BEGIN
    NEW.last_update = now();
    RETURN NEW;
  END;
$$ language plpgsql;


CREATE OR REPLACE TRIGGER settings_update
    BEFORE UPDATE
    ON
        settings
    FOR EACH ROW
EXECUTE PROCEDURE sync_last_update();


CREATE OR REPLACE VIEW banned_users AS
  SELECT * FROM users WHERE banned IS NOT NULL;

CREATE OR REPLACE VIEW users_waiting_aprove AS
  SELECT * FROM users WHERE (waiting->>'aproval')::bool = true;

CREATE OR REPLACE VIEW users_waiting_register AS
  SELECT * FROM users WHERE (waiting->>'registration')::bool = true;

INSERT INTO settings (key, data) VALUES ('server-name', '{"value": "Exworlds server"}');
INSERT INTO settings (key, data) VALUES ('default-rights', '{"value": ["any-create"]}');
""")

if not cur.execute("SELECT * FROM users WHERE username=%s", exworlds_admin_login):
    password_hash = hashlib.pbkdf2_hmac("sha512", str(exworlds_admin_password).encode(), str(salt).encode(), 2 ** 8).hex()
    cur.execute("INSERT INTO users (username, password_hash, rights) VALUES (%s, %s, %s)",
                (exworlds_admin_login, password_hash, ["server-admin"]))

conn.commit()
conn.close()