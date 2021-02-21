## 前提
gceをairflow用のサーバーとして設定する。
条件としては以下を想定。

- マシンタイプはf1-micro
- OSはUbuntu 18.04 LTS
- user名はairflow

## 準備
### GCEから
以下を実行。
再起動すればdocker containerが起動しているはず。

```sh
# git clone
AIRFLOW_HOME="$HOME/airflow"
git clone https://github.com/dr666m1/setting_airflow.git $AIRFLOW_HOME
echo "export AIRFLOW_HOME=$AIRFLOW_HOME" >> ~/.bashrc
echo "export AIRFLOW_IMAGE=apache/airflow:1.10.12-python3.8" >> ~/.bashrc

# dockerの準備
mkdir -p ~/.tmp
curl https://get.docker.com > ~/.tmp/install.sh
chmod +x ~/.tmp/install.sh
~/.tmp/install.sh
sudo usermod -aG docker $USER

# systemdの設定
sudo cp ./docker-airflow.service /lib/systemd/system/
sudo systemctl enable docker-airflow

# airflowの初期化（docker image pullも兼ねる）
source ~/.bashrc
docker container run --rm -it -u `id -u`:0 -v $AIRFLOW_HOME:/opt/airflow $AIRFLOW_IMAGE initdb
```

### ローカル・GCPコンソールから
経験上なぜかたまにサーバーの再起動が必要になるため、いっそ定期的に再起動されるよう設定する。
参考は[この記事](https://cloud.google.com/scheduler/docs/start-and-stop-compute-engine-instances-on-a-schedule?hl=ja)。
まずはGCEが一連の処理の対象になるようラベル`env=dev`を追加し、その後以下を実行。

```sh
mkdir -p ~/.tmp
cd ~/.tmp

# create pub/sub topic
gcloud pubsub topics create start-instance-event
gcloud pubsub topics create stop-instance-event

# download & deploy functions
curl -OL https://raw.githubusercontent.com/GoogleCloudPlatform/nodejs-docs-samples/master/functions/scheduleinstance/index.js
curl -OL https://raw.githubusercontent.com/GoogleCloudPlatform/nodejs-docs-samples/master/functions/scheduleinstance/package.json

gcloud functions deploy startInstancePubSub \
    --trigger-topic start-instance-event \
    --runtime nodejs10 \
    --allow-unauthenticated

gcloud functions deploy stopInstancePubSub \
    --trigger-topic stop-instance-event \
    --runtime nodejs10 \
    --allow-unauthenticated

# setting Cloud Scheduler
gcloud beta scheduler jobs create pubsub startup-dev-instances \
    --schedule '0 4 * * *' \
    --topic start-instance-event \
    --message-body '{"zone":"us-west1-a", "label":"env=dev"}' \
    --time-zone 'Asia/Tokyo'

gcloud beta scheduler jobs create pubsub shutdown-dev-instances \
    --schedule '0 3 * * *' \
    --topic stop-instance-event \
    --message-body '{"zone":"us-west1-a", "label":"env=dev"}' \
    --time-zone 'Asia/Tokyo'
```

## 補足
### airflow.cfg
デフォルトから以下を変更している。

- dags_are_paused_at_creation = False
- load_examples = False
- dag_discovery_safe_mode = False
- catchup_by_default = False

### dags/rm_old_logs.py
30日以上前のログを削除するdagを含んでいる。
ログが肥大化して、サーバーが停止するのを防ぐ目的。

### airflowコマンドの実行
末尾の`scheduler`を`list-dags`など任意のコマンドに変更すれば実行できる。

```sh
docker container run -d -u `id -u`:0 -v $AIRFLOW_HOME:/opt/airflow $AIRFLOW_IMAGE scheduler
```
ちなみに`-u`を適切に設定しないと次のような問題が生じる。

- コンテナ経由で作成したファイルをコンテナ外から削除できない
- `/etc/passwd`が変更されない（ホームディレクトリ関係で不整合が生じる）。コードの該当部分は[ここ](https://github.com/apache/airflow/blob/db3fe0926bb75008311eed804052c90bfa912424/scripts/in_container/prod/entrypoint_prod.sh#L94)。

### CloudMonitoringAgent
必要なら導入する。
[CloudMonitoringAgent](https://cloud.google.com/monitoring/agent/installation)

