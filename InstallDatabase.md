# Introduction #

This page describes how to install the test database on your machine.

## Requirements ##
  * Linux host (tested with Ubuntu 10.04 and CentOS 5.5 x64)
  * Local installation of MySQL server and client libraries (**Ubuntu:** 5.1.41-3; **CentOS:** 5.0.77-4.el5\_5.3)
  * Python 2.4 or later (**Ubuntu:** 2.6.5; **CentOS:** 2.4.3)
  * MySQL client library for Python (**Ubuntu:** 1.2.2; **CentOS:** 1.2.1-1 [http://sourceforge.net/projects/mysql-python/](http://sourceforge.net/projects/mysql-python/); **Windows:** 1.2.3c1 [http://www.codegood.com/](http://www.codegood.com/))
  * PHP 5 (**Ubuntu:** 5.3.2-1; **CentOS:** 5.1.6-27.el5)
  * Web server running locally (**Ubuntu:** Apache/2.2.14; **CentOS:** httpd/2.2.3-43.el5.centos.3)

## Preparing the MySQL Server ##
If this is a new installation of MySQL or if it is the first time the database is being used, follow the instructions described in [MySQL setup](http://code.google.com/p/qaautotest/wiki/MySQLSetup) for details on preparing the database.  If you are an experienced MySQL administrator, you should make sure you have prepared your database as follows:
  * You must know the root password for the database.
  * The database must be accessible over the network.  This will allow remote machines to access the test database through a web browser.
  * You must have all of the packages installed described in the "requirements" section above.
  * During the installation, a new user will be created to administer the Autotest database.  Identify a user and password you'd like to use for this purpose.

## Installation ##
  * Check out the source code.
  * Read through the [MySQL setup](http://code.google.com/p/qaautotest/wiki/MySQLSetup) section to ensure your MySQL server is prepared to host the test database.
  * From the autotest directory, run `install.py` as root.
  * Default values are provided.  Type enter to accept the defaults or enter your own custom value.
```
$ sudo ./install.py
Enter the MySQL host name [localhost]: 
Enter the port address for the MySQL server [3306]: 
Enter the name for the database [autotest]: 
Enter the root user name for the MySQL database [root]: 
Enter the password for the root user: 
Enter the name of your web root [/var/www/html]: 
Create a normal user for the database [tester]: 
Create a password for the normal user: 
Enter a comma separated list of admin IPs [127.0.0.1]: 
Setting up database privileges for the test user "tester".
Installation successful!
Connect to the GUI at http://localhost/autotest
For troubleshooting tips, go to http://code.google.com/p/qaautotest/wiki/Troubleshooting
```

## Troubleshooting ##
See the [Troubleshooting](http://code.google.com/p/qaautotest/wiki/Troubleshooting) page in the wiki.

## Uninstalling ##
  * Remove the installed files:
```
rm -Rf <web_root>/autotest
```

  * Remove any local database users:
```
# mysql -h <host> -u <user> -p
mysql> use mysql;
mysql> select * from user;
mysql> drop user "<user_name>"@"%";
mysql> drop user "<user_name>"@"localhost";
mysql> quit
```

  * Remove the test case database:
```
# mysql -h <host> -u <user> -p
mysql> drop database autotest;
mysql> quit
```