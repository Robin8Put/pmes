# Installation and running of the Profile Management EcoSystems

## Mongo DB, IPFS and QTUM daemon installation

Install the Mongo DB Community Edition by the following [tutorial](https://docs.mongodb.com/manual/tutorial/install-mongodb-on-ubuntu/).

For installing the [IPFS](https://ipfs.io/docs/getting-started/) use the following commands:

```bash
sudo apt-get update
sudo apt-get install golang-go -y
wget https://dist.ipfs.io/go-ipfs/v0.4.10/go-ipfs_v0.4.10_linux-386.tar.gz
tar xvfz go-ipfs_v0.4.10_linux-386.tar.gz
sudo mv go-ipfs/ipfs /usr/local/bin/ipfs
```

**Install the [QTUM](https://github.com/qtumproject/qtum/wiki/How-to-Stake-QTUM-using-a-Linux-Virtual-Private-Server-(VPS))**

Download and add the Qtum signing key to your Linux operation system:

```bah
sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys BF5B197D
```

Add a repository to your APT sources. **NOTE**: Please remember to change "xenial" Ubuntu version codename for your personal Ubuntu version codename.

```bash
sudo su
echo "deb http://repo.qtum.info/apt/ubuntu/ xenial main" >> /etc/apt/sources.list
```

Refresh APT sources and install the Qtum:

```bash
sudo apt update && sudo apt install qtum
```

Here is the example of `qtum.conf` from a `~/qtum/` folder:

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

Install a python3.6-dev:

```bash
sudo apt-get install python3.6-dev
```

## Clone sources from the GitHub and create a virtual environment

```bash
git clone https://github.com/Robin8Put/pmes.git
```

Create the virtual environment and install needed libraries from a `requirements.txt`:

```bash
cd pmes
virtualenv --python=python3.6 venv
source venv/bin/activate
pip3 install -r requirements.txt
```

Add [bip32keys](bip32keys/bip32keys), [qtum_utils](bip32keys/qtum_utils) and [tornado_components](tornado_components) directories to the `venv/lib/python3.6/site-packages`. (Will be in the pip shortly)

# Running servers

Run a Mongo DB server:

```bash
sudo service mongod start
```

Initialize an IPFS daemon:

```bash
ipfs daemon
```

Execute a QTUM daemon:

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

The PMES works with eight modules: AMS, storage, balance, PDMS, qtum_bridge, email, coin and parser.

Therefore, for running PMES you should run the following servers:

1. run **AMS and PDMS** servers:

```bash
source venv/bin/activate
python3 main.py
```

2. run the **storage** server for the AMS module:

```bash
source venv/bin/activate
python3 ams/storage/main.py
```

3. run the **balance** server:

```bash
source venv/bin/activate
python3 balance/main.py
```

4. run the **qtum_bridge** server:

```bash
source venv/bin/activate
python3 pdms/qtum_bridge/main.py
```

5. run the **email** server:

```bash
source venv/bin/activate
python3 mail/email_new.py start
python3 mail/index.py
```

6. run the **coin** server:

```bash
source venv/bin/activate
python3 coin/one_coin.py start
```

7. run the **parser** server:

```bash
source venv/bin/activate
python3 parser/Client_storge.py
```
