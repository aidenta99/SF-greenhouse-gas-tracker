
-- Populate department dimension

INSERT INTO staging.dim_location (location_key, city, state, zip_code)
SELECT -1, 'Unknown', 'Unknown', 'Unknown';

INSERT INTO staging.dim_location (city, state, zip_code)
SELECT DISTINCT
	COALESCE(city, 'Unknown') as city,
	COALESCE(state, 'Unknown') as state,
	COALESCE(zip, 'Unknown') as zip_code
FROM raw.soda_evictions
WHERE 
 city IS NOT NULL OR state IS NOT NULL OR zip IS NOT NULL;

-- Populate source dimension