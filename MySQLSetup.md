# Introduction #

Setting up MySQL is a straight forward process but can be challenging or intimidating for those who are not database administrators.  This page will step you through setting up a MySQL server for use with the QA Autotest database.  Detailed instructions are provided for both Ubuntu and CentOS installations.  They should be fairly consistent across distributions but they were most recently tested with Ubuntu 10.04 and CentOS 5.5.

The instructions below will accomplish the following:
  * Install the MySQL server and client packages necessary for a successful deployment of the QA Autotest database.
  * The MySQL server will be configured for remote access over the network.
  * The MySQL server will have a known root password.
  * Install the requisite PHP packages necessary to display the web browser based GUI.

# Ubuntu #

  * Install MySQL and supporting packages:
```
sudo apt-get install mysql-server mysql-client python-mysqldb libapache2-mod-php5 php5-cli php5-common php5-cgi php5-mysql
```

  * The web server needs to be restarted to properly load the libapache2-mod-php5 module:
```
sudo /etc/init.d/apache2 restart
```

  * Set up MySQL root password.  If it wasn't set during the MySQL server installation, set up the root password on the MySQL Server:
```
# mysql -u root
mysql> use mysql;
mysql> UPDATE user SET Password=PASSWORD('new-password') WHERE user='root';
mysql> FLUSH PRIVILEGES;
mysql> quit
```

  * Enable remote access to the server:
```
vi /etc/mysql/my.cnf
```
> Find this line:

> `bind-address            = 127.0.0.1`

> Change the IP address from 127.0.0.1 to the public IP address of the host.

  * Restart mysql to make the changes take effect:
```
sudo service mysql restart
```

  * You are now ready to [install the database](http://code.google.com/p/qaautotest/wiki/InstallDatabase).


# CentOS #

  * Install MySQL and supporting packages:
```
yum install mysql.x86_64 mysql-server.x86_64 MySQL-python.x86_64 httpd.x86_64 mysql php.x86_64 php-mysql.x86_64
```

  * Start the MySQL database:
```
service mysqld start
```

  * Start the web server:
```
service httpd start
```

  * Make sure MySQL starts automatically when the node boots:
```
chkconfig --level 35 mysqld on
```

  * Make sure the web server starts automatically when the node boots:
```
chkconfig --level 35 httpd on
```

  * Set up MySQL root password.  If it wasn't set during the MySQL server installation, set up the root password on the MySQL Server:
```
# mysql -u root
mysql> use mysql;
mysql> UPDATE user SET Password=PASSWORD('new-password') WHERE user='root';
mysql> FLUSH PRIVILEGES;
mysql> quit
```

  * You are now ready to [install the database](http://code.google.com/p/qaautotest/wiki/InstallDatabase).