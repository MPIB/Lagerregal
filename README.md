Lagerregal
==========

Lagerregal is a somewhat flexible inventory system. Mostly designed to work best
for my workplace, but should easily customizable to your needs.

[![Build Status](https://travis-ci.org/vIiRuS/Lagerregal.png?branch=master)](https://travis-ci.org/vIiRuS/Lagerregal)


Quickstart
==========

Install necessary requirements (either globally or with virtualenv)

```
$ sudo pip2 install -U -r dependencies.txt
```

Generate settings.py

```
$ cp Lagerregal/settings_template.py Lagerregal/settings.py
```

Run:

```
$ python2 manage.py syncdb
$ python2 manage.py runserver
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
