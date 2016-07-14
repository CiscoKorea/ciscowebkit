
# Cisco Webkit


## Install

### Install Mariadb

windows: https://downloads.mariadb.org/interstitial/mariadb-10.1.14/winx64-packages/mariadb-10.1.14-winx64.msi/from/http%3A//ftp.utexas.edu/mariadb/

RH: yum install mariadb-server
DEB: apt-get install python-pip mariadb-server libmysqlclient-dev python-dev

#### Create Database
mysql > CREATE DATABASE ciscowebkit;
mysql > GRANT ALL PRIVILEGES ON ciscowebkit.* TO 'cisco'@'localhost' IDENTIFIED BY 'cisco123';"

#### Install Python Package
$> pip install django

$> pip install mysqlclient

$> cd CISCOWEBKIT_ROOT

$> python manage.py makemigrations

$> python manage.py migrate

$> python manage.py createsuperuser

$> python manage.py runserver 8080

## Icon Repository
http://fontawesome.io/icons/
