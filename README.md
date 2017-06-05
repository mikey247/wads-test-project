# Django/Wagtail Setup Notes

## System Libraries

These are required libraries in addition to standard ones such as Apache2 and Python 3 (3.4)

For Apache2 Server, use mod_wsgi for Python 3 (seperate package to the Python 2.7 one)

    apt-get install libapache2-mod-wsgi-py3 
    apt-get install python-letsencrypt-apache
    apt-get install python-psycopg2
    apt-get install build-essential binutils-doc autoconf flex bison libjpeg-dev
    apt-get install libfreetype6-dev zlib1g-dev libzmq3-dev libgdbm-dev libncurses5-dev
    apt-get install automake libtool libffi-dev curl git tmux gettext
    apt-get install postgresql-9.6 postgresql-contrib-9.6 postgresql-doc-9.6 postgresql-server-dev-9.6
    apt-get install openjdk-8-jre
    apt-get install elasticsearch
    apt-get install redis-server
    apt-get install python3-yaml libyaml-dev

**Note: Java required for elasticsearch**

**Note: YAML required if planning to use YAML format for fixtures**

**Note: Specific version of elasticsearch may be required for it to work.**

    wget https://download.elastic.co/elasticsearch/elasticsearch/elasticsearch-1.7.2.deb
    dpkg -i elasticsearch-1.7.2.deb

Optional for dev mode and testing of Django/Wagtail default database setting:

    apt-get install sqlite3
    apt-get install sqlitebrowser

## Configure elasticsearch

Create service:

    update-rc.d elasticsearch defaults 95 10

Edit `/etc/elasticsearch/elasticsearch.yml`:

    network.bind_host: 127.0.0.1

Restart service:

    service elasticsearch restart

Test service:

    curl -X GET 'http://localhost:9200'

Should see response similar to:

```
#!JSON
	{
	"status" : 200,
	"name" : "Grandmaster",
	"cluster_name" : "elasticsearch",
	"version" : {
		"number" : "1.7.2",
		"build_hash" : "e43676b1385b8125d647f593f7202acbd816e8ec",
		"build_timestamp" : "2015-09-14T09:49:53Z",
		"build_snapshot" : false,
		"lucene_version" : "4.10.4"
	},
	"tagline" : "You Know, for Search"
	}

```

**Note: Connection refused is likely when wrong version is installed (see above).**
	
## Virtual Environment

Create a virtual environment to hold the required version of Python and necessary modules e.g.,

    cd /var/www/wagtail
    virtualenv -p /usr/bin/python3 wagtail-env
    source wagtail-env/bin/activate
	
## Install Django, Wagtail and Additional Modules

    cd /var/www/wagtail
    pip install wagtail

    wagtail start siteroot
    cd siteroot
	
Edit the `requirements.txt` file and add (as of 2017-06-05)
```
appdirs==1.4.3
beautifulsoup4==4.6.0
certifi==2017.4.17
chardet==3.0.3
Django==1.11.2
django-bootstrap-themes==3.3.6
django-classy-tags==0.8.0
django-debug-toolbar==1.8
django-extensions==1.7.9
django-modelcluster==3.1
django-redis==4.8.0
django-taggit==0.22.1
django-treebeard==4.1.1
djangorestframework==3.6.3
elasticsearch==2.4.0
html5lib==0.999999999
idna==2.5
olefile==0.44
packaging==16.8
Pillow==4.1.1
pip-review==0.5.3
psycopg2==2.7.1
Pygments==2.2.0
pyparsing==2.2.0
pytz==2017.2
PyYAML==3.12
redis==2.10.5
requests==2.17.3
shortcodes==2.4.0
six==1.10.0
sqlparse==0.2.3
Unidecode==0.4.20
urllib3==1.21.1
wagtail==1.10.1
wagtailmenus==2.2.2
wagtailtinymce==4.2.1.5
webencodings==0.5.1
Willow==0.4
```
	
    pip install -r requirements.txt

## SSL Certificate

Use certbot-auto....TBC

	
## Setup Apache2 config

Create `/etc/apache2/sites-available/wagtail-le-ssl.conf`

Use *WSGIDaemonProcess* to specify the python path to the site and the virtualenv

Note: SSL content generated by certbot-auto with Let's Encrypt CA

```
#!Apache Config

<IfModule mod_ssl.c>
<VirtualHost *:443>

    ServerName <your-host>

    Alias /robots.txt /var/www/wagtail/siteroot/static/robots.txt
    Alias /favicon.ico /var/www/wagtail/siteroot/static/favicon.ico

    Alias /media /var/www/wagtail/siteroot/media/
    Alias /static /var/www/wagtail/siteroot/static/

    <Directory /var/www/wagtail/siteroot/static>
        Require all granted
    </Directory>

    <Directory /var/www/wagtail/siteroot/media>
        Require all granted
    </Directory>

    <Directory /var/www/wagtail/siteroot/sitecore>
        <Files wsgi.py>
	    Require all granted
	</Files>
    </Directory>

    # Use python-home as preferred method; alternative fails on some Python/wsgi versions

    WSGIDaemonProcess wagtailapp python-home=/var/www/wagtail/wagtail-env/lib/python3.5/site-packages python-path=/var\
/www/wagtail/siteroot
    WSGIProcessGroup wagtailapp
    WSGIScriptAlias / /var/www/wagtail/siteroot/sitecore/wsgi.py process-group=wagtailapp

    LogLevel warn
    ErrorLog /var/log/apache2/wagtail-error_log
    CustomLog /var/log/apache2/wagtail-access_log common

    SSLCertificateFile /etc/letsencrypt/live/<your-host>/cert.pem
    SSLCertificateKeyFile /etc/letsencrypt/live/<your-host>/privkey.pem
    Include /etc/letsencrypt/options-ssl-apache.conf
    SSLCertificateChainFile /etc/letsencrypt/live/<your-host>/chain.pem

</VirtualHost>
</IfModule>
```

Default `/var/www/wagtail/siteroot/sitecore/wsgi.py` is good as is for development mode, but requires a minor edit for production mode:

    #os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sitecore.settings.dev")
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sitecore.settings.production")

## Configure postgresql for wagtail app

	su - postgres
	psql
	postgres=#
		CREATE DATABASE wagtail;
		CREATE USER wagtail WITH PASSWORD '***********';
		ALTER ROLE wagtail SET client_encoding TO 'utf8';
		ALTER ROLE wagtail SET default_transaction_isolation TO 'read committed';
		ALTER ROLE wagtail SET timezone TO 'UTC';
		GRANT ALL PRIVILEGES ON DATABASE wagtail TO wagtail;
		\q
	exit


## Configure Django/Wagtail

Generate a new SECRET_KEY at http://www.miniwebtool.com/django-secret-key-generator/

Edit `/var/www/wagtail/mysite/mysite/settings/base.py` and remove DATABASES, ALLOWED_HOSTS, LANGUAGE_CODE, WAGTAIL_SITE_NAME, BASE_URL

Create local.py and add:


```
#!python
# ---------------
# Django Settings
# ---------------

SECRET_KEY = '**************************************'

# Security
# https://docs.djangoproject.com/en/1.10/topics/security/#ssl-https

#    SECURE_SSL_REDIRECT = True
#    SESSION_COOKIE_SECURE = True
#    CSRF_COOKIE_SECURE = True
#    SECURE_HSTS_SECONDS = 3600 # 1 hour; change to 31536000 for 1 year when in production


# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'wagtail=',
        'USER': 'wagtail',
        'PASSWORD': '**********************',
        'HOST': 'localhost',
        'PORT': '',
    }
}

# Hosts
# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts

ALLOWED_HOSTS = [
    'your-FQDN-host',
    'localhost',
    '127.0.0.1',
]

INTERNAL_IPS = [
    '127.0.0.1',
]

# Language

LANGUAGE_CODE = 'en-gb'

# ----------------
# Wagtail Settings
# ----------------

WAGTAIL_SITE_NAME = "=Django/Wagtail Development Test Site"

# Base URL to use when referring to full URLs within the Wagtail admin backend -
# e.g. in notification emails. Don't include '/admin' or a trailing slash

BASE_URL = '<your-FQDN-host>'

# Cache

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'localhost:6379',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
    },
}

# (Elastic) Search

WAGTAILSEARCH_BACKENDS = {
    'default': {
        'BACKEND': 'wagtail.wagtailsearch.backends.elasticsearch',
        'INDEX': 'wagtail',
    },
}

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAdminUser',
    ],
    'PAGE_SIZE': 10
}



```

**Note: Do NOT INCLUDE local.py in any git repos!**
	
Initialise wagtail:

	cd /var/www/wagtail/siteroot
	./manage.py makemigrations
	
Requires `makemigrations` per app:

	./manage.py makemigrations siteconfig
	./manage.py makemigrations sitecore
	./manage.py makemigrations search

	./manage.py makemigrations home

	./manage.py makemigrations article

Database, search and superuser commands:

	./manage.py update_index
	./manage.py createsuperuser
		{overseer/**password**}
	./manage.py collectstatic

Perform initial migration:

	./manage.py migrate
	
Enable/Start Services
---------------------

	a2ensite wagtail-le-ssl
	apache2ctl restart
	
## Development Mode

If DEBUG is enabled run in dev mode on localhost ONLY. Debug information is output on the pages and may compromise security. Use an SSH tunnel to access via a remote machine and browser.

## Live site

Enable the production settings and **ensure DEBUG mode is DISABLED**, along with any toolbars.

Go to:
*	https://<your-host> for site
*	https://<your-host>/admin for Wagtail CMS Admin
*	https://<your-host>/django-admin for the default Django app admin
	
## Service cron jobs (TBC)

Need to consider:
*	le-ssl cert renewal...
*	elasticsearch update_index
*	session clearout

# References

* https://www.digitalocean.com/community/tutorials/how-to-install-and-configure-elasticsearch-on-ubuntu-14-04
* http://www.revsys.com/writings/quicktips/ssh-tunnel.html -