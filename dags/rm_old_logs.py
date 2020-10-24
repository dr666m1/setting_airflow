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
    schedule_interval="00 00 01  *  *",
)

task1 = BashOperator(
    task_id='dag_processor_manager',
    bash_command="""
        cp $AIRFLOW_HOME/logs/dag_processor_manager/dag_processor_manager{,_old}.log
        echo -n > $AIRFLOW_HOME/logs/dag_processor_manager/dag_processor_manager.log
    """,
    dag=dag,
)

task2 = BashOperator(
    task_id='else',
    bash_command="""
        find $AIRFLOW_HOME/logs -mtime +30 -print | grep -E '^.*/[0-9]{4}-[0-9]{2}-[0-9]{2}[^/]*$'
        find $AIRFLOW_HOME/logs -mtime +30 -print | xargs rm -rf
    """,
    dag=dag,
)

task1 #>> task2
