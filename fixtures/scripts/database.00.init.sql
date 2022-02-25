CREATE DATABASE <database_name>;
CREATE USER <username> WITH PASSWORD '<password>';
ALTER ROLE <username> SET default_transaction_isolation TO 'read committed';
ALTER ROLE <username> SET client_encoding TO 'utf8';
ALTER ROLE <username> SET timezone TO 'utc';
GRANT ALL PRIVILEGES ON DATABASE <database_name> TO <username>;
