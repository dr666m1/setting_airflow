# 前提
gceをairflow用のサーバーとして設定する。
条件としては以下を想定。

- マシンタイプはf1-micro
- OSはUbuntu 18.04 LTS

# dockerの設定

```sh
# install
mkdir -p ~/.tmp
curl https://get.docker.com > ~/.tmp/install.sh
chmod +x ~/.tmp/install.sh
~/.tmp/install.sh

# dockerグループに追加
sudo usermod -aG docker $USER
```

# dockerの実行
```sh
docker container run -it -u `id -u`:0 -v $LOCAL_PATH:/opt/airflow apache/airflow:1.10.12-python3.8 initdb #初回のみ
docker container run -it -u `id -u`:0 -v $LOCAL_PATH:/opt/airflow apache/airflow:1.10.12-python3.8 scheduler
```
