# esgf-auth
OpenID/OAuth2 authentication demo for ESGF

Simple Django web aplication with ESGF backend for social-core (former python-social-auth). The ESGF backend should also work with Flask, Pyramid, and other web frameworks supported by social-core.

# Install esgf-auth

Create Python 2.7 virtual environment

```
$ python --version 
Python 2.7.10
$ virtualenv venv
$ . venv/bin/activate
```

Download and install esgf-auth with dependencies (Django, social-auth-app-django, social-auth-core, etc.)

```
(venv)$ git clone git@github.com:lukaszlacinski/esgf-auth
(venv)$ cd esgf-auth
(venv)$ pip install -r requirements.txt
```

Create the database

```
(venv)$ ./manage.py migrate
```

Set SOCIAL_AUTH_ESGF_KEY and SOCIAL_AUTH_ESGF_SECRET in esgf-auth/settings.py to a client id and secret received from an admin of an ESGF OAuth2 server. When you register your OAuth2 client, your redirect URI is `https://<your_hostname>[/<prefix>]/complete/esgf/`.


# Apache/mod_wsgi

For example, on Ubuntu, add the following lines to /etc/apache2/sites-available/default-ssl,conf in `<VirtualHost _default_:443>`

```
    WSGIDaemonProcess esgf_auth python-path=<your_base_dir>/esgf-auth:<your_base_dir>/venv/lib/python2.7/site-packages
    WSGIScriptAlias /<prefix> <your_base_dir>/esgf-auth/esgf_auth/wsgi.py process-group=esgf_auth
    <Directory <your_base_dir>/esgf-auth/esgf_auth>
        <Files wsgi.py>
            # Apache >= 2.4
            #Require all granted
            # Apache <= 2.2
            Order allow,deny
            Allow from all
        </Files>
    </Directory>
```

where `<prefix>` is a optional path that you may need if you have another web app running at the '/' path. After restarting Apache, open `https://<your_hostname>/<prefix>` in a web browser. You will likely need to change ownership of the 'esgf-auth' directory to www-data (on Ubuntu), so Apache can access the SQLite3 database file.
