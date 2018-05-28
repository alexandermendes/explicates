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
