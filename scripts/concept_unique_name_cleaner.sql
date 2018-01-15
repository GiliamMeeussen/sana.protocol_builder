UPDATE api_concept SET name=(name || id), display_name=(display_name || id)
WHERE name IN (
    SELECT duplicates.name from (
        SELECT name, count(*)
        FROM api_concept
        GROUP BY name
        HAVING count(*) > 1
    ) as duplicates
);
