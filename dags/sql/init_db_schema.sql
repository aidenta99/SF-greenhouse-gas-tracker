DROP SCHEMA IF EXISTS raw CASCADE;
DROP SCHEMA IF EXISTS staging CASCADE;
DROP SCHEMA IF EXISTS mart CASCADE;

CREATE SCHEMA raw;
CREATE SCHEMA staging;
CREATE SCHEMA mart;

-- Raw
CREATE UNLOGGED TABLE raw.soda_emission (
	raw_id text,
	created_at timestamp,
	updated_at timestamp,
	department_name text,
    department_code numeric,
    measured_at date,
    ghg_emission numeric,
    consumption numeric,
    consumption_unit text
);

CREATE UNLOGGED TABLE raw.soda_energy (
	raw_id text,
	created_at timestamp,
	updated_at timestamp,
	sfpuc_code text,
    building_address text,
    facility numeric,
    notes numeric,
    department_name text,
    department_code text,
    building_category text,
    year_built integer,
    year_renovated integer,
    building_floor_area numeric,
    energy_use_intensity numeric,
    carbon_intensity numeric
);

-- Staging
CREATE TABLE staging.dim_department (
	department_code serial PRIMARY KEY,
	department_name text,
    building_address text,
    facility numeric,
    notes numeric,
    department_name text,
    department_code text,
    building_category text,
    year_built integer,
    year_renovated integer,
    building_floor_area numeric
);

CREATE UNIQUE INDEX department_name_uniq_idx ON staging.dim_deparment (department_name);

CREATE TABLE staging.dim_location (
	location_key serial PRIMARY KEY,
	city text,
	state text,
	zip_code text
);

CREATE TABLE staging.fact_emission (
	emission_key text PRIMARY KEY,
    measured_at date,
    department_code numeric,
    ghg_emission numeric,
    consumption numeric,
    consumption_unit text
);

-- mart
CREATE TABLE mart.dim_department (
	department_code serial PRIMARY KEY,
	department_name text,
    building_address text,
    facility numeric,
    notes numeric,
    building_category text,
    year_built integer,
    year_renovated integer,
    building_floor_area numeric
);

CREATE TABLE mart.fact_emission (
	emission_key text PRIMARY KEY,
    measured_at date,
    department_code numeric,
    ghg_emission numeric,
    consumption numeric,
    consumption_unit text
);

