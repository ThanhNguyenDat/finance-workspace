CREATE USER replicator WITH REPLICATION ENCRYPTED PASSWORD 'replicator_password';

SELECT pg_create_physical_replication_slot('replication_slot_backup');
SELECT pg_create_physical_replication_slot('replication_slot_1');
SELECT pg_create_physical_replication_slot('replication_slot_2');
SELECT pg_create_physical_replication_slot('replication_slot_3');
SELECT pg_create_physical_replication_slot('replication_slot_4');
