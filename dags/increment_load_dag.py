from airflow import DAG
from airflow.operators.postgres_operator import PostgresOperator
from airflow.operators.python_operator import ShortCircuitOperator
from operators.soda_to_s3_operator import SodaToS3Operator
from operators.s3_to_postgres_operator import S3ToPostgresOperator
from airflow.utils.dates import days_ago
from datetime import timedelta

soda_headers = {
    'keyId':'############',
    'keySecret':'#################',
    'Accept':'application/json'
}

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': days_ago(2),
    'email': ['airflow@example.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(seconds=30)
}

def get_size(**context):
	val = context['ti'].xcom_pull(key='obj_len')
	return True if val > 0 else False

with DAG('sf-emission-tracker-incremental_load',
	default_args=default_args,
	description='Executes incremental load from SODA API & S3-hosted csv''s into Production DW.',
	max_active_runs=1,
	schedule_interval=None) as dag:
 
	op1 = SodaToS3Operator(
		task_id='get_emission_data',
		http_conn_id='API_emission',
		headers=soda_headers,
		days_ago=31,
		s3_conn_id='S3_emission',
		s3_bucket='sf-emissionmeter',
		s3_directory='soda_jsons',
		size_check=True,
		max_bytes=500000000,
		dag=dag
	)
	
	op2 = ShortCircuitOperator(
		task_id='check_get_results',
		python_callable=get_size,
		provide_context=True,
		dag=dag
	)
	
	op3 = PostgresOperator(
		task_id='truncate_target_tables',
		postgres_conn_id='RDS_emission',
		sql='sql/trunc_target_tables.sql',
		dag=dag
	)
	
	op4 = S3ToPostgresOperator(
		task_id='load_emission_data',
		s3_conn_id='S3_emission',
		s3_bucket='sf-emissionmeter',
		s3_prefix='soda_jsons/soda_emission_import',
		source_data_type='json',
		postgres_conn_id='RDS_emission',
		schema='raw',
		table='soda_emission',
		get_latest=True,
		dag=dag
	)
	
	op5 = S3ToPostgresOperator(
		task_id='load_energy_data',
		s3_conn_id='S3_energy',
		s3_bucket='sf-energymeter',
		s3_prefix='soda_jsons/soda_energy_import',
		source_data_type='csv',
		header=True,
		postgres_conn_id='RDS_emission',
		schema='raw',
		table='soda_energy',
		get_latest=True,
		dag=dag
	)
	
	op7 = PostgresOperator(
		task_id='execute_incremental_load',
		postgres_conn_id='RDS_emission',
		sql='sql/incremental_load.sql',
		dag=dag
	)
	
	op1 >> op2 >> op3 >> (op4, op5) >> op7