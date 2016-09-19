#!/bin/bash

git clone https://github.com/CiscoKorea/ciscowebkit.git /opt/ciscowebkit
cd /opt/ciscowebkit && python manage.py makemigrations --settings docker.settings
cd /opt/ciscowebkit && python manage.py migrate --settings docker.settings
cd /opt/ciscowebkit && echo "from django.contrib.auth.models import User; User.objects.create_superuser('cisco', 'admin@example.com', 'cisco123')" | python manage.py shell --settings docker.settings
cd /opt/ciscowebkit && python manage.py runserver --settings docker.settings 0.0.0.0:80
