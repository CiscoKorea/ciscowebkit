
# Cisco Webkit


## Install ( Manual)

### Install Mariadb

windows: https://downloads.mariadb.org/interstitial/mariadb-10.1.14/winx64-packages/mariadb-10.1.14-winx64.msi/from/http%3A//ftp.utexas.edu/mariadb/

Redhat/CentOS: 
```
$> yum install mariadb-server
```
Ubuntu/Debian: 
```
$> apt-get install python-pip mariadb-server libmysqlclient-dev python-dev
```

#### Create Database
```
mysql > CREATE DATABASE ciscowebkit;
mysql > GRANT ALL PRIVILEGES ON ciscowebkit.* TO 'cisco'@'localhost' IDENTIFIED BY 'cisco123';"
```

#### Install Python Package 
```
$> pip install django
$> pip install mysqlclient
$> pip install pymysql
$> pip install tabulate
$> pip install websocket-client 
$> cd CISCOWEBKIT_ROOT
$> python manage.py makemigrations
$> python manage.py migrate
$> python manage.py createsuperuser
$> python manage.py runserver 0.0.0.0:8080
```
## Icon Repository
http://fontawesome.io/icons/


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
