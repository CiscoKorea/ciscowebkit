#!/bin/bash

git clone https://github.com/CiscoKorea/ciscowebkit.git /opt/ciscowebkit
python /opt/ciscowebkit/manage.py makemigrations
python /opt/ciscowebkit/manage.py migrate
echo "from django.contrib.auth.models import User; User.objects.create_superuser('cisco', 'admin@example.com', 'cisco123')" | python /opt/ciscowebkit/manage.py shell
python /opt/ciscowebkit/manage.py runserver 0.0.0.0:80
