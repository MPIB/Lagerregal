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
+ Optional query and listing for puppet facts or opsi details of a device
+ Permission system for users and public device lists
+ Themable with bootswatch

Manual Quickstart
=================

The following command will install all dependencies, setup a demo database, and
start a testserver for development:

```
make run
```

After that you can point your browser to
[http://localhost:8000](http://localhost:8000) and login with "admin:admin".

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
