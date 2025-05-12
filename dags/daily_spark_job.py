from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

defaut_args = {
    'owner': 'airflow',
    'start_date': datetime(2023, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

dag = DAG(
    'daily_spark_job',
    default_args=defaut_args,
    schedule_interval='@daily',
    catchup=False
)

run_spark = BashOperator(
    task_id='run_spark_job',
    bash_command='spark-submit /opt/airflow/dags/spark_batch_processor.py',
    dag=dag
)

run_spark