# CSPRO-BE

# Features #
* Django 3.1.7
* Uses PIP for python package management
* mysql for database with mysqlclient

# Pre requisites #

* Install Python 3.9.5 if not previously installed (for ubuntu 18.04).  
```
$ sudo apt-get update
$ sudo add-apt-repository ppa:jonathonf/python-3.9.5
$ sudo apt-get update
$ sudo apt-get install python3.9.5
```  

* Install MySql if not previously installed.  
```
sudo apt update
sudo apt install mysql-server
sudo mysql_secure_installation
```

* Install Python Package Index Tool pip3  
`sudo apt-get -y install python3-pip`

* Install virtual environment wrapper  
(further info found here: [https://linoxide.com/how-to-create-python-virtual-environment-on-ubuntu-20-04/](https://linoxide.com/how-to-create-python-virtual-environment-on-ubuntu-20-04/))
`$ apt-get install python3-venv`  

* Create directory for development, name it anything.
```
$ mkdir CSPRO
$ cd CSPRO
```

* When inside the directory create virtual environment, called env in example. Then activate the environment.  
```
$ virtual --python=python3.9.5 env
	virtualenv -p python3.9.5 env
	navigate into bin folder and run source activate
$ .env/bin/activate
```  
# Installation #

1. Enter CSPRO directory for development where project files stored.  
` (env) $ cd CSPRO`
2. Install requirements  
`pip install -r requirment.txt`

3. Set up MYSql
Switch over to the mysql account by typing:  
`$ mysql -u root -h localhost -p`   

You can now access a Mysql prompt immediately by typing:
ALTER ROLE 'adminmanager' WITH LOGIN;
  
```
$ ALTER USER 'userName'@'localhost' IDENTIFIED BY 'New-Password-Here';
$ CREATE DATABASE cspro;
$ GRANT ALL PRIVILEGES ON mydb.* TO 'myuser'@'%' WITH GRANT OPTION;
```  


4. RUN Admin site migrations and other django app migrations.  
	'python manage.py migrate'
	
5. Import Static Data.  
`sh dependencies.sh`

6. Run the server
`python manage.py runserver`

This should run the server and give an IP address that when entered into a web browser will bring up the development server. Address of the server is your IP address
most likely http://127.0.0.1:8000/.

7. Create superuser 
` python manage.py createsuperuser`
email: superadmin@yopmial.com
password: xxxxxxxxx
this super admin will create when dependencies.sh runs


8. Regsiter the Outh Application
`First uncomment the below line in main/admin.py`
` admin.site.unregister(Application)`

In your Django admin create a new oauth2_provider.models.Application. Set client type to "public" and grant type to "resource owner password based". The name can just be whatever makes sense to you (e.g., "iOS App", "JS Frontend"), and the application should be owned by your admin user.Use this client ID , Client Secret in your project settings/base.py

9. To view the API documentation. Go to
`(Postman Collection found here: [https://www.getpostman.com/collections/a2700829cc05a1fb9633](https://www.getpostman.com/collections/a2700829cc05a1fb9633)`  


#Project Overview

This project contains one database is default `default_db`.
if you change any models do `python manage.py makemigrations`
but for migrate use both of these commands 
`python manage.py migrate` for apply changes in database