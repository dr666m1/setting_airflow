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
SETTING_DIR="~/.setting_airflow"
git clone https://github.com/dr666m1/setting_airflow.git $SETTING_DIR

# airflowの設定
AIRFLOW_HOME="~/airflow"
echo "export AIRFLOW_HOME=$AIRFLOW_HOME" >> ~/.bashrc
ln -s $SETTING_DIR/airflow.cfg $AIRFLOW_HOME/airflow.cfg

# dockerの準備
mkdir -p ~/.tmp
curl https://get.docker.com > ~/.tmp/install.sh
chmod +x ~/.tmp/install.sh
~/.tmp/install.sh
sudo usermod -aG docker $USER
```

# 実行

```sh
docker container run -it -u `id -u`:0 -v $AIRFLOW_HOME:/opt/airflow apache/airflow:1.10.12-python3.8 initdb #初回のみ
docker container run -it -u `id -u`:0 -v $AIRFLOW_HOME:/opt/airflow apache/airflow:1.10.12-python3.8 scheduler
```


