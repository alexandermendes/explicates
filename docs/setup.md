The following page explains how to get an Explicates server up and running.

## Installation

A virtual machine setup is provided for local development.

Download and install
[Vagrant](https://www.vagrantup.com/) >= 4.2.10 and
[VirtualBox](https://www.virtualbox.org/) >= 1.2.1,
then run:

```bash
# setup vm
vagrant up

# enter vm
vagrant ssh

# run
python run.py
```

## Configuration

The contents of the settings template file, `settings.py.tmpl`, are replicated
below. To edit any of the settings make a copy of the template:

```
cp settings.py.tmpl settings.py
```

The comments below indicate where any default values are used.

```python
{!../settings.py.tmpl!}
```

## Deployment

Explicates requires a server with PostgreSQL 10 (or higher) installed. The
recommended OS is Ubuntu 18.04. The guide following assumes you are starting
with a fresh Ubuntu 18.04 server.

Update and upgrade the package index:

```bash
sudo apt-get update
sudo apt-get upgrade
```

### Install Python and git

Install Python:

```bash
sudo apt install python
```

Install Python dependencies:

```bash
sudo apt install python-virtualenv python-dev python-setuptools python-pip
```

Install git:

```bash
sudo apt-get install git-core
```

### Download and build Explicates

Clone Explicates:

```bash
mkdir /var/www
git clone https://github.com/alexandermendes/explicates /var/www/explicates
```

Create a virtual environment:

```bash
cd /var/www/explicates
virtualenv env
```

Activate the virtual environment:

```bash
source env/bin/activate
```

Install Explicates:

```bash
pip install -r requirements.txt
```

Copy the settings template:

```bash
cp settings.py.tmpl settings.py
```

!!! warning "Important"

    You should edit the settings file to uncomment `ENV` and `SERVER_NAME`,
    where the server name is the location of your production server.

Copy the alembic configuration:

```bash
cp alembic.ini.tmpl alembic.ini
```

### Setup the database

Install database dependencies:

```bash
sudo apt-get install postgresql postgresql-server-dev-all python-psycopg2 libpq-dev
```

Add a database user:

```bash
sudo -u postgres createuser -d -P explicates
```

Enter the password `tester` when prompted.

!!! info "Password choice"

    If you choose a different password you should also edit the database path
    in `settings.py` and `alembic.ini`.

Create the database:

```bash
sudo -u postgres createdb explicates -O explicates
```

Populate the database:

```bash
python /var/www/explicates/bin/db_create.py
```

### Setup NGINX

Install NGINX:

```bash
sudo apt-get install nginx
```

Remove the default server configuration:

```bash
sudo rm -r /etc/nginx/sites-available/default
sudo rm -r /etc/nginx/sites-enabled/default
```

Edit a new server configuration file:

```
vim /etc/nginx/sites-available/explicates
```

Copy in the following and save the file:

```bash
server {
  listen 80 default_server;
  listen [::]:80 default_server;

  # Change this to match your domain
  server_name annotations.example.com;

  client_body_buffer_size 10K;
  client_header_buffer_size 1k;
  client_max_body_size 10m;
  large_client_header_buffers 2 1k;

  gzip             on;
  gzip_comp_level  2;
  gzip_types       text/plain application/json application/ld+json;
  gzip_min_length  1000;
  gzip_proxied     expired no-cache no-store private auth;

  location / {
    expires -1;
    include uwsgi_params;
    uwsgi_pass unix:/tmp/explicates.sock;
  }
}
```

Enable the Explicates configuration:

```bash
ln -s /etc/nginx/sites-available/explicates /etc/nginx/sites-enabled/explicates
```

Restart the NGINX server:

```bash
sudo service nginx restart
```

## Setting up uWSGI

Install uWSGI:

```bash
pip install -U uwsgi
```

Edit a new server configuration file:

```bash
vim /var/www/explicates/explicates.ini
```

Copy in the following and save the file:

```bash
[uwsgi]
socket = /tmp/explicates.sock
chmod-socket = 666
chdir = /var/www/explicates
pythonpath = ..
virtualenv = /var/www/explicates/env
module = run:app
cpu-affinity = 1
processes = 2
threads = 2
buffer-size = 65535
```

## Setup Up Supervisor

Supervisor is used to run Explicates in the background and restart it when the
server boots up.

Install supervisor:

```
sudo apt-get install supervisor
```

Edit a new Supervisor program configuration:

```bash
vim /etc/supervisor/conf.d/explicates.conf
```

Copy in the following and save the file:

```conf
[program:explicates]
command=/var/www/explicates/env/bin/uwsgi /var/www/explicates/explicates.ini
directory=/var/www/explicates
autostart=true
autorestart=true
log_stdout=true
log_stderr=true
logfile=/var/log/explicates.log
logfile_maxbytes=10MB
logfile_backups=2
```

Restart supervisor:

```bash
sudo service supervisor stop
sudo service supervisor start
```

Your Annotation server should now be running at
[http://your.domain.com](http://your.domain.com).

## Security

There are lots of potential steps that you could take to secure your servers.
Running through all of the options here is outside the scope of this guide,
but here are some quick wins for the LibCrowds and Explicates servers
(details might need to be modified a bit for the PYBOSSA server).

### Firewall

UFW, or Uncomplicated Firewall, is an easy way to manage a frontend firewall.

Install it:

```bash
sudo apt-get install ufw
```

Deny incoming and allow outgoing by default:

```bash
sudo ufw default deny incoming
sudo ufw default allow outgoing
```

Allow connections:

```bash
sudo ufw allow ssh
sudo ufw allow 22/tcp
```

Check the rules:

```bash
ufw status
```

You should see the following output:

```bash
To                         Action      From
--                         ------      ----
22                         ALLOW       Anywhere
80                         ALLOW       Anywhere
443                        ALLOW       Anywhere
22 (v6)                    ALLOW       Anywhere (v6)
80 (v6)                    ALLOW       Anywhere (v6)
443 (v6)                   ALLOW       Anywhere (v6)
```

If the rules do indeed appear as above, enable the firewall:

```bash
sudo ufw enable
```

## Secure Sockets Layer (SSL)

[Let's Encrypt](https://letsencrypt.org) provide free SSL certificates. Use
the [Certbot](https://certbot.eff.org/) client to set them up for your
operating system.

After following the Certbot guide, above, you can setup a scheduled task
to automatically renew the certificates.

Edit a new daily task:

```bash
vim /etc/cron.daily/certrenew
```

Copy in the following and save the file:

```
certbot renew
```

Make the file executable:

```bash
chmod +x /etc/cron.daily/certrenew
```

Your certificate should now be checked for renewal daily.



