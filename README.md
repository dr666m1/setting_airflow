# 前提
gceをairflow用のサーバーとして設定する。
条件としては以下を想定。

- マシンタイプはf1-micro
- OSはUbuntu 18.04 LTS

# 準備
以下を実行。
`~/.bashrc`やグループの反映には再ログインが必要。

```sh
# git clone
AIRFLOW_HOME="$HOME/airflow"
git clone https://github.com/dr666m1/setting_airflow.git $AIRFLOW_HOME
echo "export AIRFLOW_HOME=$AIRFLOW_HOME" >> ~/.bashrc

# dockerの準備
mkdir -p ~/.tmp
curl https://get.docker.com > ~/.tmp/install.sh
chmod +x ~/.tmp/install.sh
~/.tmp/install.sh
sudo usermod -aG docker $USER
```

# 実行
以下を実行。`-u`を適切に設定しないと次のような問題が生じる。

- コンテナ経由で作成したファイルをコンテナ外から削除できない
- `/etc/passwd`が変更されない（→ホームディレクトリ関係で不整合が生じる）。コードの該当部分は[ここ](https://github.com/apache/airflow/blob/db3fe0926bb75008311eed804052c90bfa912424/scripts/in_container/prod/entrypoint_prod.sh#L94)。

```sh
docker container run --rm -it -u `id -u`:0 -v $AIRFLOW_HOME:/opt/airflow apache/airflow:1.10.12-python3.8 initdb #初回のみ
docker container run --rm -it -u `id -u`:0 -v $AIRFLOW_HOME:/opt/airflow apache/airflow:1.10.12-python3.8 scheduler
```

# 捕捉
## airflow.cfg
デフォルトから以下を変更している。

- dags_are_paused_at_creation = False
- load_examples = False
- dag_discovery_safe_mode = False
- catchup_by_default = False
