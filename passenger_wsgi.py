# -*- coding: utf-8 -*-
import os, sys
sys.path.insert(0, '/var/www/www-root/data/www/orc-rrmc.ru/MedProject')
sys.path.insert(1, '/var/www/www-root/data/www/orc-rrmc.ru/.venv/lib/python3.11/site-packages')
os.environ['DJANGO_SETTINGS_MODULE'] = 'MedProject.settings'
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application() 