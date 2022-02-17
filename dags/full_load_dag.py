from airflow import DAG
from airflow.operators.postgres_operator import PostgresOperator
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

with DAG('sf_data_full_load',
		default_args=default_args,
		description='Executes full load from SODA API to Production DW.',
		max_active_runs=1,
		schedule_interval=None) as dag:

    op1 = SodaToS3Operator(
		task_id='get_SF_emission_data',
		http_conn_id='API_emission',
		headers=soda_headers,
		s3_conn_id='S3_emission',
		s3_bucket='sf-emission',
		s3_directory='soda_jsons',
		size_check=True,
		max_bytes=500000000,
		dag=dag
	)
	
    op2 = PostgresOperator(
		task_id='initialize_target_db',
		postgres_conn_id='RDS_emission',
		sql='sql/init_db_schema.sql',
		dag=dag
	)
	
    op3 = S3ToPostgresOperator(
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
    
    op4 = S3ToPostgresOperator(
		task_id='load_energy_data',
		s3_conn_id='S3_energy',
		s3_bucket='sf-energymeter',
		s3_prefix='soda_jsons/soda_energy_import',
		source_data_type='json',
		postgres_conn_id='RDS_energy',
		schema='raw',
		table='soda_energy',
		get_latest=True,
		dag=dag
	)

    op5 = PostgresOperator(
		task_id='execute_full_load',
		postgres_conn_id='RDS_emission',
		sql='sql/full_load.sql',
		dag=dag
	)
	
    op1 >> op2 >> (op3, op4) >> op5