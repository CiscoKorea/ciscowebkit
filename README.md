
# Cisco Webkit

## Manual Install

### 1. Install Mariadb

* Windows
	
    * [MariaDB Link](https://downloads.mariadb.org/interstitial/mariadb-10.1.14/winx64-packages/mariadb-10.1.14-winx64.msi/from/http%3A//ftp.utexas.edu/mariadb/)
    * [Gettext Link](https://mlocati.github.io/articles/gettext-iconv-windows.html)


* Redhat/CentOS (tested on CentOS 7.x):
	
	$ yum install mariadb-server mariadb-devel epel-release gcc python-devel git

* Ubuntu/Debian (tested on Ubuntu 14.04): 

	$ apt-get install python-pip mariadb-server libmysqlclient-dev python-dev

### 2. Install Python Package 

	$ pip install django mysqlclient tabulate websocket-client requests

### 3. Create Database

Setting Variables
* {ADMIN_NAME} : ID for Administrator
* {PASSWORD} : Password for Administrator

Connect mariadb server with client

	$ mysql -u root -p

Create database & auth

	mysql > CREATE DATABASE ciscowebkit;
	mysql > GRANT ALL PRIVILEGES ON ciscowebkit.* TO '{ADMIN_NAME}'@'localhost' IDENTIFIED BY '{PASSWORD}';"
	
{ADMIN_NAME} and {PASSWORD} is used for initial login ID & Password

### 4. Initial Setting

Using Environments
* {CISCOWEBKIT_ROOT} : Webkit Package Root

Edit {CISCOWEBKIT_ROOT}/ciscowebkit/settings.py


	DATABASES = {
		'default': {
			'ENGINE': 'django.db.backends.mysql',
			'NAME': 'ciscowebkit',
			'USER': '{ADMIN_NAME}',
			'PASSWORD': '{PASSWORD}',
		}
	}

	$ cd {CISCOWEBKIT_ROOT}
	$ python manage.py makemigrations
	$ python manage.py migrate
	$ python manage.py createsuperuser
	$ python manage.py runserver 0.0.0.0:80

* makemigrations : create python wrapper for database
* migrate : create database tables
* createsuperuser : create superuser with {CISCOWEBKIT_ROOT}/ciscowebkit/settings.py
* runserver : excute django server with <Accept Address>:<Listening Port>

Important! {ADMIN_NAME} & {PASSWORD} is same as Variables in Create Database Section

## Install on Docker Image

* Install Docker Package
* Execute build.sh

	cd ciscowebkit/docker $ build.sh

* Execute start.sh

	cd ciscowebkit/docker $ start.sh

## Install via Ansible

Install ansible latest version from github.com

	$ git clone https://github.com/ansible/ansible --recursive 
	$ cd ansible 
	$ sudo python setup.py install 

update hosts file [dev] & [prd] section with your vm's ip 
create sudo user account named cisco ( or what you want) 

	$ useradd -m cisco -s /bin/bash 
	$ usermode -aG sudo cisco for Ubuntu 
	$ usermode -aG wheel cisco for RHEL/CentOS


run ansible script 

	$ ansible-playbook webtoolkit.yml -i hosts -u cisco -K -k 

Enjoy !!


## Developer Guide

### Icon Repository
http://fontawesome.io/icons/
