FROM postgres:latest

RUN echo "CREATE TABLE IF NOT EXISTS Emails (ID SERIAL PRIMARY KEY, Email VARCHAR(32) NOT NULL);" > /docker-entrypoint-initdb.d/init.sql \
    && echo "INSERT INTO Emails (Email) VALUES ('test@mail.ru'), ('test1@mail.ru');" >> /docker-entrypoint-initdb.d/init.sql \
    && echo "CREATE TABLE IF NOT EXISTS Phone_numbers (ID SERIAL PRIMARY KEY, Phone_number VARCHAR(32) NOT NULL);" >> /docker-entrypoint-initdb.d/init.sql \
    && echo "INSERT INTO Phone_numbers (Phone_number) VALUES ('88005553535'), ('+78005553535');" >> /docker-entrypoint-initdb.d/init.sql \
    && echo "CREATE USER replicator WITH REPLICATION ENCRYPTED PASSWORD 'replicator_password';" >> /docker-entrypoint-initdb.d/init.sql \
    && echo "SELECT pg_create_physical_replication_slot('replication_slot');" >> /docker-entrypoint-initdb.d/init.sql
RUN chmod -R 777 /var/log/postgresql
RUN mkdir /oracle
RUN mkdir /oracle/pg_data/
RUN mkdir /oracle/pg_data/archive
RUN chmod -R 777 /oracle/pg_data/archive
