import os
#os.system('cmd /k "python manage.py migrate --fake-initial"')
os.system('cmd /k "python manage.py makemigrations & python manage.py migrate"')