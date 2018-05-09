# LibAnno

> A PostgreSQL-backed Web Annotation server.

The server complies with the
[Web Annotation Protocol](https://www.w3.org/TR/annotation-protocol/), with a
few extras thrown in.


## Setup

### Development

A virtual machine setup is provided for easily getting a development server up
and running.

Download and install
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

### Production

The requirements for production servers are:

- Ubuntu 18.04 LTS
- Python 2.7 or >= 3.4
- PostgreSQL >= 10
