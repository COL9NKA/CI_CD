FROM postgres:latest

RUN echo "CREATE USER replicator WITH REPLICATION ENCRYPTED PASSWORD 'replicator_password';" > /docker-entrypoint-initdb.d/init.sql \
    && echo "SELECT pg_create_physical_replication_slot('replication_slot');" >> /docker-entrypoint-initdb.d/init.sql
