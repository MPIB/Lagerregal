Lagerregal
==========

Lagerregal is a somewhat flexible inventory system. Mostly designed to work
best for my workplace, but it should be easily customizable to your needs.

[![Build Status](https://travis-ci.org/MPIB/Lagerregal.png?branch=master)](https://travis-ci.org/MPIB/Lagerregal)

Screenshots
===========

![Alt text](/screenshots/device_detail.png?raw=true "Device Details")

Features
========

+ Inventory system for devices based on Django and Bootstrap
+ "Business" concepts for buildings, sections, departments, users
+ LDAP integration and synchronization scripts
+ Tracks edits of a device
+ Lend devices to users
+ Multi-Language support
+ Generates and prints Dymo labels from templates for inventory stickers
+ Manage static IP addresses for legacy network environments
+ Semi-Automatic e-mail delivery (on lending, trashing etc)
+ Optional query and listing for puppet facts of a device
+ Permission system for users and public device lists
+ Themable with bootswatch

Demo and Docker
===============

To quickly spin up a Lagerregal with minimal sample data, run:

```
docker run --rm -it -p 8000:8000  mpib/lagerregal:demo
```

point your browser to [http://localhost:8000](http://localhost:8000) and login with "admin:admin".

Note that both Dockerfiles included in the repo are intended for demo and
development purposes and are not suited for production.

Manual Quickstart
=================

Install necessary requirements (either globally or with virtualenv)

```
$ pip install -U -r dependencies.txt
```

Generate settings.py

For quickstart and development:

```
$ cp Lagerregal/template_development.py Lagerregal/settings.py
```

For production (edit first):
```
$ cp Lagerregal/template_production.py Lagerregal/settings.py
```

Run:

```
$ python manage.py migrate
$ python manage.py runserver
```

Optional (not optional for production):

```
$ python generate_secret_key.py
```

Generate sample data:
```
$ python manage.py populate
```

Label Printing
===============

1. Create necessary label templates with the official software and put them in static/.

2. Set `ALLOWED_INCLUDE_ROOTS = ('/path/to/static/dir',) ` in settings.py to the absolute location of that static folder.

3. Set the `LABEL_TEMPLATES`, Example:

```
LABEL_TEMPLATES = {
    "sample_department": {
        "device": [
            "/path/to/Lagerregal/static/labels/device.label",
            ["data","keys","to", "use","in","label"] ]
        "room": [
            "/path/to/Lagerregal/static/labels/room.label",
            ["data","keys","to", "use","in","label"] ]
    }
}
```
