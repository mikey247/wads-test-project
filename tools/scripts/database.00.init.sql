CREATE DATABASE <database_name>;
CREATE <username> WITH PASSWORD '<password>';
ALTER ROLE <username> SET default_transaction_isolation TO 'read committed';
ALTER ROLE <username> SET client_encoding TO 'utf8';