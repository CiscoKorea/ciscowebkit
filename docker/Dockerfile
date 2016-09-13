FROM centos:7

MAINTAINER Cisco DevOps <hyjang@cisco.com>

RUN yum install gcc git mariadb mariadb-devel epel-release -y
RUN yum install python-devel python-pip -y
RUN pip install django requests mysqlclient tabulate websocket-client

RUN git clone https://github.com/CiscoKorea/ciscowebkit.git /opt/ciscowebkit
RUN python /opt/ciscowebkit/manage.py makemigrations
RUN python /opt/ciscowebkit/manage.py migrate
RUN echo "from django.contrib.auth.models import User; User.objects.create_superuser('cisco', 'admin@example.com', 'cisco123')" | python manage.py shell

# Start Services
ENTRYPOINT ["python /opt/ciscowebkit/manage.py runserver 0.0.0.0:80"]