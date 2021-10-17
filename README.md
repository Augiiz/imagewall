# imagewall
Social website where you can share images, watch shared images, comment and rate.

# Requirements
Python 3.8+

# Installation

Open main directory

Run ~InstallRequiredPackages.py

Run ~GenerateSecretKey.py

copy the key generated, go to imagewall/settings.py insert the key in SECRET_KEY field between the quotation marks.

In the same settings.py file go to the very bottom in the field EMAIL_HOST_USER add your desired gmail adress and in the EMAIL_HOST_PASSWORD add your gmail password, this will be used to send user emails when in need to remind their password.

Run ~MakeMigrations.py

Run ~CreateSuperUser.py

Fill super user information in the cmd window.

Run ~Runserver.py

Go to 127.0.0.1:8000
