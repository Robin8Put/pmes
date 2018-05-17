# Profile Management EcoSystem installation

## Mongo DB, IPFS and QTUM daemon installation

Install Mongo DB Community Edition by next [tutorial](https://docs.mongodb.com/manual/tutorial/install-mongodb-on-ubuntu/).

For installing [IPFS](https://ipfs.io/docs/getting-started/) use next commands:

```bash
sudo apt-get update
sudo apt-get install golang-go -y
wget https://dist.ipfs.io/go-ipfs/v0.4.10/go-ipfs_v0.4.10_linux-386.tar.gz
tar xvfz go-ipfs_v0.4.10_linux-386.tar.gz
sudo mv go-ipfs/ipfs /usr/local/bin/ipfs
```

**Install [QTUM](https://github.com/qtumproject/qtum/wiki/How-to-Stake-QTUM-using-a-Linux-Virtual-Private-Server-(VPS))**

Download and add the Qtum signing key to your linux install:

```bah
sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys BF5B197D
```

Adding repository to your APT sources. **NOTE**: Please remember to change "xenial" for your Ubuntu version codename

```bash
sudo su
echo "deb http://repo.qtum.info/apt/ubuntu/ xenial main" >> /etc/apt/sources.list
```

Refresh APT sources and install Qtum:

```bash
sudo apt update && sudo apt install qtum
```

Here is the example of `qtum.conf` from `~/qtum/` folder:

```bash
server=1
testnet=1
rpcbind=127.0.0.1
rpcport=8333
rpcuser=qtumuser
rpcpassword=qtum2018
rpcclienttimeout=130
rpcallowip=127.0.0.0/24
logevents=1
```

## Cloning sources and creating of virtual environment

```bash
git clone https://github.com/Robin8Put/pmes.git
```

Create virtualenv and install needed libraries from the `requirements.txt`:

```bash
cd pmes
virtualenv --python=python3.6 venv
source venv/bin/activate
pip3 install -r requirements.txt
```

Add [bip32keys](bip32keys), [qtum_utils](bip32keys/qtum_utils) and [tornado_components](tornado_components) directories to the `venv/lib/python3.6/site-packages`. (Will be in the pip shortly)

# Running servers

Run Mongo DB:

```bash
sudo service mongod start
```

Initializing IPFS daemon:

```bash
ipfs daemon
```

To execute the QTUM daemon:

```bash
# prefered way to run qtum daemon
qtumd -testnet

# not prefered way to run qtum daemon
qtumd -daemon

# check that qtum daemon works
qtum-cli help
qtum-cli listunspent
ps -ax | grep qtumd
```

PMES works with four modules: AMS, balance, pdms and qtum_bridge.

Therefore, for running application you should run 5 servers:

1. **ams** server:

```bash
source venv/bin/activate
python3 ams/main.py
```

2. **storage** server for AMS:

```bash
source venv/bin/activate
python3 ams/storage/main.py
```

3. **balance** server:

```bash
source venv/bin/activate
python3 balance/main.py
```

4. **bridge** server:

```bash
source venv/bin/activate
python3 pdms/bridge/main.py
```

5. **pdms** server:

```bash
source venv/bin/activate
python3 pdms/main.py
```
