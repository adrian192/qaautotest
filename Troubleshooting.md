# Introduction #

This troubleshooting page should help resolve the most common initial installation and usage issues.  It will be updated as time goes by and as new issues are uncovered.


### When connecting to the GUI for the first time, I am prompted to download a file or I see just a list of files ###
**Problem:** The index.php script isn't being correctly processed by your web server.

**Solution:**
  * Try installing the following packages: **Ubuntu:** `libapache2-mod-php5 php5-cli php5-common php5-cgi`.  **CentOS:** php.x86\_64
  * Verify that index.php is identified as being a valid index file in your apache/httpd configuration file.
  * After making these changes, you must restart your web server, e.g. `service httpd restart` or `/etc/init.d/apache2 restart`
  * If you still get a download prompt after doing the above, and if you are usign Google's Chrome web browser, clear your browser's cache and reload the page.

### The web page doesn't load ###
If, when you connect to `http://<ip_address>/autotest`, you get an error indicating that the page cannot load, there are three likely explanations:
  * The web server isn't started.  Check the status of your web server with a command such as `service httpd status` or `/etc/init.d/apache2 status`.
  * There is a firewall on the machine that is preventing the web page from loading.  The simple test for this is to try stopping the firewall service, e.g. `service iptables stop`.  If this works, you should set a rule allowing HTTP access through the firewall or disable the firewall altogether.
  * The installation target directory wasn't the web root.  The default web root in the installation script is `/var/www/html`.  This is the default for CentOS.  Ubuntu uses `/var/www` as its default web root.  Make sure you have the correct web root configured.

### ERROR 1045, Access denied for user 'root'@'localhost' (using password: YES) ###
**Problem:** The password you have entered for administering the SQL server is wrong.

**Solution:**
  * When you install the Autotest database, a new user account is created just for this database.  The password may (should) be different than your root password.  Make sure you are using the correct password.
  * If you have forgotten your root password, the MySQL site has details on [resetting your root password](http://dev.mysql.com/doc/refman/5.1/en/resetting-permissions.html).
  * If you have forgotten the password used for administering your Autotest database, you can reset the password at the SQL server console by doing the following:
```
# mysql -u root
mysql> use mysql;
mysql> UPDATE user SET Password=PASSWORD('new-password') WHERE user='<autotest_local_user>';
mysql> FLUSH PRIVILEGES;
mysql> quit
```

### ERROR 2002, Can't connect to local MySQL server through socket ###
**Problem:** The MySQL server is not installed or the service isn't running.

**Solution:**
  * Review the page on [installing MySQL server](http://code.google.com/p/qaautotest/wiki/MySQLSetup) to make sure your SQL server is fully installed and the services are running properly.

### ERROR 2003, Can't connect to MySQL server on 'localhost' ###
**Problem:** Unable to connect to the database over the network.

**Solution:**
  * Make sure the firewall on the database server permits access to the SQL server.
  * Configure the MySQL server to allow external access to the database:
    1. Open your `my.cnf` file (`/etc/mysql/my.cnf` or `/etc/my.cnf`).
    1. If the line `skip-networking` is present, comment it out.
    1. If the line `bind-address = 127.0.0.1` is present, change `127.0.0.1` to your machine's public IP address.
    1. Restart the MySQL server: `service mysql restart` or `/etc/init.d/mysql restart`.

### How do I remove old tests, suites, or test report data? ###
Hosts that have been configured as administrative machines can remove old tests, suites, and test report records from the database through the GUI.  On the **Management** page, there should be a **Database admin** option in the drop-down menu.  Select this to administer the database.  If you do not see the **Database admin** option, your local machine is not configured as an administrative machine.

To add a host as an administrative machine, do the following:
  1. On the database server, open the database.ini file, e.g. `/var/www/html/autotest/database.ini`
  1. Add your host IP to the line "`admin = <some_ip>`" using commas as a separator, e.g. "`admin = 127.0.0.1,192.168.0.1,10.2.20.55`"
  1. Save your changes to the file.
  1. Reload the web UI on your administrative machine to see the **Database admin** drop-down option on the **Management** page.