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

See `settings.py.tmpl` for all available configuration
settings; the contents of the file are replicated below. All of the settings
commented out are optional; the comments indicate if any defaults are used.

```python
{!../settings.py.tmpl!}
```
