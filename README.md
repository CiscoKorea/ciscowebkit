
# Cisco Webkit

## Manual Install

### 1. Install Mariadb

#### Windows

[MariaDB Link](https://downloads.mariadb.org/interstitial/mariadb-10.1.14/winx64-packages/mariadb-10.1.14-winx64.msi/from/http%3A//ftp.utexas.edu/mariadb/)

#### Redhat/CentOS
	
	$ yum install mariadb-server

#### Ubuntu/Debian: 

	$ apt-get install python-pip mariadb-server libmysqlclient-dev python-dev

### 2. Install Python Package 

	$ pip install django
	$ pip install mysqlclient
	$ pip install pymysql
	$ pip install tabulate
	$ pip install websocket-client 

### 3. Create Database
{ADMIN_NAME}
{PASSWORD}

	mysql > CREATE DATABASE ciscowebkit;
	mysql > GRANT ALL PRIVILEGES ON ciscowebkit.* TO '{ADMIN_NAME}'@'localhost' IDENTIFIED BY '{PASSWORD}';"

### 4. Initial Setting
{CISCOWEBKIT_ROOT}

Edit {CISCOWEBKIT_ROOT}/ciscowebkit/settings.py
<code>
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'ciscowebkit',
        'USER': '{ADMIN_NAME}',
        'PASSWORD': '{PASSWORD}',
    }
}
</code>

	$ cd {CISCOWEBKIT_ROOT}
	$ python manage.py makemigrations
	$ python manage.py migrate
	$ python manage.py createsuperuser
	$ python manage.py runserver 0.0.0.0:80

## Install via Ansible

Install ansible latest version from github.com
```
$> git clone https://github.com/ansible/ansible --recursive 
$> cd ansible 
$> sudo python setup.py install 
```

update hosts file [dev] & [prd] section with your vm's ip 
create sudo user account named cisco ( or what you want) 
```
$> useradd -m cisco -s /bin/bash 
$> usermode -aG sudo cisco for Ubuntu 
$> usermode -aG wheel cisco for RHEL/CentOS
```

run ansible script 
```
$> ansible-playbook webtoolkit.yml -i hosts -u cisco -K -k 
```

Enjoy !!


## Developer Guide

### Icon Repository
http://fontawesome.io/icons/