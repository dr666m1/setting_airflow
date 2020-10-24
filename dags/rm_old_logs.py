import sys
from datetime import timedelta
# The DAG object; we'll need this to instantiate a DAG
from airflow import DAG
# Operators; we need this to operate!
from airflow.operators.python_operator import PythonOperator
from airflow.operators.bash_operator import BashOperator
from airflow.utils.dates import days_ago
# These args will get passed on to each operator
# You can override them on a per-task basis during operator initialization
import os
from datetime import timedelta

common_args = {
    'owner': os.environ.get("USER", "unknown"),
    'depends_on_past': False,
    'start_date': days_ago(1),
    'retries': 5,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'rm_old_logs',
    default_args=common_args,
    description='rm_old_logs',
    schedule_interval="55 12 *  *  *",
)

task1 = BashOperator(
    task_id='rm_old_logs',
    bash_command='''
        echo $AIRFLOW_HOME
        echo aaa
    '''
    dag=dag,
)

task1 #>> task2
