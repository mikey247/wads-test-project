CREATE DATABASE gitissues;
CREATE USER brooke WITH PASSWORD 'brooke';
ALTER ROLE brooke SET default_transaction_isolation TO 'read committed';
ALTER ROLE brooke SET client_encoding TO 'utf8';
ALTER ROLE brooke SET timezone TO 'utc';
GRANT ALL PRIVILEGES ON DATABASE gitissues TO brooke;
