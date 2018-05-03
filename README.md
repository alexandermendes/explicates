# pywa

A PostgreSQL-backed Web Annotation server.

## Setup

### Development

A virtual machine setup is provided for easily getting a development server up
and running. Download and install
[Vagrant](https://www.vagrantup.com/) >= 4.2.10 and
[VirtualBox](https://www.virtualbox.org/) >= 1.2.1,
then run:

```bash
# setup the virtual machine
vagrant up

# enter the virtual machine
vagrant ssh

# run
python run.py
```

By default the server will now be available at http://127.0.0.1:3000.
