-- Populate department dimension

INSERT INTO staging.dim_location (city, state, zip_code)
SELECT 
	se.city,
	se.state,
	se.zip_code
FROM (
	SELECT DISTINCT
		COALESCE(city, 'Unknown') as city,
		COALESCE(state, 'Unknown') as state,
		COALESCE(zip, 'Unknown') as zip_code
	FROM raw.soda_evictions
	) se
LEFT JOIN staging.dim_location dl 
	ON se.city = dl.city
	AND se.state = dl.state
	AND se.zip_code = dl.zip_code
WHERE 
	dl.location_key IS NULL;