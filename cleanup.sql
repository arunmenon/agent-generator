-- Delete tasks associated with crews that have no crew_name
DELETE FROM task
WHERE crew_id IN (
    SELECT crew_id FROM crew_metadata
    WHERE crew_name IS NULL OR crew_name = ''
);

-- Delete agents associated with crews that have no crew_name
DELETE FROM agent
WHERE crew_id IN (
    SELECT crew_id FROM crew_metadata
    WHERE crew_name IS NULL OR crew_name = ''
);

-- Finally, delete the crews themselves
DELETE FROM crew_metadata
WHERE crew_name IS NULL OR crew_name = '';

