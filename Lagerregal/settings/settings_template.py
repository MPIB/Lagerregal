

#edit if development
if dev:

# Make this unique, and don't share it with anybody.
SECRET_KEY = "CHANGE ME"

#edit if production
if prod:

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'database.db',                      # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

#SET A SECRET KEY AND DON'T SHARE IT WITH ANYONE
# SECRET_KEY = ""

LABEL_TEMPLATES = {
    "FOO" : {
        "device" : (
            #"/opt/Lagerregal/staticserve/labels/device.label",
            "labels/device.label",
            ["name", "inventorynumber", "serialnumber", "id"])
    }
}
