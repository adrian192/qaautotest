#!/usr/bin/env python

import os
import sys
import re
import stat
import socket
import signal
import getpass
import logging
import dbaccess

# This table list is all the tables
tables_list = {
"auto_suite_list":"create table auto_suite_list"
" (id int(10) unsigned not null auto_increment,"
" suite_name text,"
" PRIMARY KEY (id)"
") engine=MyISAM auto_increment=1 default charset=latin1",

"auto_test_case":"create table auto_test_case ("
" File varchar(80) NOT NULL default '',"
" Class varchar(80) NOT NULL default '',"
" targetVersion varchar(20) default '1',"
" lastRunVersion varchar(40) default NULL,"
" lastRunTime int(10) default NULL,"
" lastRunHTML varchar(100) default NULL,"
" svnLocation varchar(100) default NULL,"
" testSchedule int(10) unsigned default NULL,"
" testRunFlag varchar(8) default '',"
" xfailBugID varchar(10) default NULL,"
" testLinkId int(32) unsigned default NULL,"
" id int(10) unsigned NOT NULL auto_increment,"
" runAsRoot int(1) NOT NULL default '0',"
" PRIMARY KEY  (id)"
") ENGINE=MyISAM AUTO_INCREMENT=1 DEFAULT CHARSET=latin1",

"auto_test_item":"CREATE TABLE auto_test_item ("
"  testFile varchar(80) NOT NULL default '',"
"  testClass varchar(80) NOT NULL default '',"
"  jobID int(32) unsigned NOT NULL default '0',"
"  startTime int(32) unsigned default NULL,"
"  endTime int(32) unsigned default NULL,"
"  testStatus varchar(32) default NULL,"
"  testHTML varchar(100) default NULL,"
"  testData text,"
"  utime float(10,4) default NULL,"
"  stime float(10,4) default NULL,"
"  runTime float NOT NULL default '0',"
"  PRIMARY KEY  (testFile,testClass,jobID)"
") ENGINE=MyISAM DEFAULT CHARSET=latin1",

"auto_test_jobs":"CREATE TABLE auto_test_jobs ( "
"  id int(11) NOT NULL auto_increment, "
"  startTime int(11) default NULL, "
"  endTime int(11) default NULL, "
"  status varchar(32) default NULL, "
"  version varchar(40) default NULL, "
"  jobHTML varchar(100) default NULL, "
"  primeTestUnit varchar(40) default NULL, "
"  comment text, "
"  userId varchar(80) default NULL, "
"  suiteID int(10) unsigned NOT NULL default '0', "
"  PRIMARY KEY  (id) "
") ENGINE=MyISAM AUTO_INCREMENT=1 DEFAULT CHARSET=latin1",

"auto_test_suites":"CREATE TABLE auto_test_suites ("
"  auto_suite_name varchar(100) NOT NULL default '',"
"  testFile varchar(80) NOT NULL default '',"
"  testClass varchar(80) NOT NULL default '',"
"  id int(11) NOT NULL default '0',"
"  require_pass int(1) NOT NULL default '1'"
") ENGINE=MyISAM DEFAULT CHARSET=latin1",

"harness_list":"CREATE TABLE harness_list ("
"  id int(10) unsigned NOT NULL auto_increment,"
"  primary_ip varchar(16) default '0.0.0.0',"
"  status int(8) unsigned default '0',"
"  reserve_user varchar(40) default '',"
"  reserve_time int(10) unsigned default '0',"
"  currentOS int(10) unsigned default '0',"
"  MAC_ADDR varchar(40) NOT NULL default '',"
"  SerialCon varchar(40) NOT NULL default '',"
"  SerialCon_port int(10) unsigned default '0',"
"  hname varchar(40) NOT NULL default '',"
"  supportedOS varchar(20) NOT NULL default '1,2,3,4,5',"
"  pdu_name varchar(20) NOT NULL default '',"
"  pdu_port int(10) unsigned default '0',"
"  pdu2_name varchar(20) NOT NULL default '',"
"  pdu2_port int(10) unsigned NOT NULL default '0',"
"  PRIMARY KEY  (id)"
") ENGINE=MyISAM AUTO_INCREMENT=1 DEFAULT CHARSET=latin1",

"harness_os_list":"CREATE TABLE harness_os_list ("
"  id int(11) NOT NULL auto_increment,"
"  os_type varchar(40) NOT NULL default '',"
"  os_default varchar(60) NOT NULL default '',"
"  os_append varchar(100) NOT NULL default '',"
"  root_dir varchar(40) NOT NULL default '',"
"  kernelType varchar(10) default NULL,"
"  PRIMARY KEY  (id)"
") ENGINE=MyISAM AUTO_INCREMENT=1 DEFAULT CHARSET=latin1",

"user_list":"CREATE TABLE user_list ("
"  email varchar(40) default NULL"
") ENGINE=MyISAM DEFAULT CHARSET=latin1"
}

# Handle ctrl-c exit
def sig_handler(signum, frame):
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    print("")
    sys.exit(1)
signal.signal(signal.SIGINT, sig_handler)

def main():
    input_array = []
    input_array = get_input()
    if not pre_flight_check(input_array):
        sys.exit(1)
    
    # Try to create the database tables first
    b = CreateTestDatabase(input_array[0], input_array[1], input_array[2], input_array[3], input_array[5], input_array[6])
    
    # Now copy the files into the web root.
    target_dir = os.path.join(input_array[4], input_array[1])
    os.makedirs(target_dir)
    os.mkdir(os.path.join(target_dir, "csv"))
    os.chmod(os.path.join(target_dir, "csv"), stat.S_IRWXU|stat.S_IRWXG|stat.S_IRWXO)
    os.system("cp -p *.inc *.php *.html %s" %target_dir)
    create_ini(target_dir, input_array[0], input_array[1], input_array[5], input_array[6])
    print("Installation successful!")
    print("Connect to the GUI at http://%s/%s" %(input_array[0], input_array[1]))
    print("For troubleshooting tips, go to http://%s/%s/help.html" %(input_array[0], input_array[1]))
    
def get_input():
    input = []
    sql_host = ""
    dbname = ""
    user = ""
    password = ""
    webroot = ""
    test_user = ""
    test_password = ""
    
    sql_host = raw_input("Enter the MySQL host name [localhost]: ")
    if sql_host == "":
        sql_host = "localhost"
    try:
        socket.gethostbyname(sql_host)
    except socket.gaierror:
        print("Unable to resolve host %s." %sql_host)
        sys.exit(1)
    input.append(sql_host)
    
    dbname = raw_input("Enter the name for the database [autotest]: ")
    if dbname == "":
        dbname = "autotest"
    input.append(dbname)
    
    user = raw_input("Enter the root user name for the MySQL database [root]: ")
    if user == "":
        user = "root"
    input.append(user)
    
    password = getpass.getpass("Enter the corresponding password for the MySQL database: ")
    input.append(password)
    
    webroot = raw_input("Enter the name of your web root [/var/www/html]: ")
    if webroot == "":
        webroot = "/var/www/html"
    input.append(webroot)
    
    test_user = raw_input("Create a normal user for the database [tester1]: ")
    if test_user == "":
        test_user = "tester1"
    input.append (test_user)

    test_password = getpass.getpass("Create a password for the normal user: ")
    input.append (test_password)
    
    return input
    
def pre_flight_check(input):
    target_dir = os.path.join(input[4], input[1])
    if not os.access(input[4], os.W_OK):
        print("Write access is not allowed to the web root %s" %input[4])
        if os.geteuid() != 0:
            print "Rerun using sudo."
            sys.exit(1)
        print("Add write access to the directory and try again.")
    if os.path.exists(target_dir):
        print("The installation directory %s already exists." %target_dir)
        print("Remove the directory or specify a new database name.")
        sys.exit(1)
    return True
    
def create_ini(target_dir, host, db_name, user, password):
    file = open(os.path.join(target_dir, "database.ini"), "wb")
    file.write("[database]\n")
    file.write("host = %s\n" %host)
    file.write("db_name = %s\n" %db_name)
    file.write("user = %s\n" %user)
    file.write("password = %s\n" %password)
    file.write("testlink = disabled\n")
    file.close()


class CreateTestDatabase(object):
    def __init__(self, db_host, db_name, db_user, db_pass, test_user="tester1", test_password="tester1"):
        self.db_name = db_name
        # test_user and test_password is the user name and password for
        # everyday use of the harness and test system.
        self.test_user = test_user
        self.test_password = test_password
        self.dba = dbaccess.dbaccess(db_host, db_user, db_pass, "")
        try:
            self.dba.connect_db()
        except:
            print("Failed to connect to database.")
        self.create_db(db_name)
        self.create_tables()
        self.createTesterUser (self.test_user, self.test_password)
        self.dba.disconnect_db()
    
    def create_db(self, db_name):
        # Check if the database already exists.
        query = "show databases like \"%s\"" %db_name
        rc = self.dba.update(query)
        if rc == 1:
            print("Unable to create the database.  An existing database called \'%s\' already exists." %db_name)
            print("To overwrite the database, you must manually drop the existing database first.")
            print("Steps:")
            print("   1: Open a mysql connection to the server, \"mysql -h <host> -u <user> -p")
            print("   2: Command: drop database %s;" %db_name)
            self.dba.disconnect_db()
            sys.exit(0)
        create = "create database if not exists %s" %db_name
        rc = self.dba.update(create)
        self.dba.update("use %s" %db_name)

    def create_tables(self):
        #print(tables_list["auto_suite_list"])
        #print(tables_list["user_list"])
        for item in tables_list:
            query = tables_list[item]
            rc = self.dba.update(query)
            if rc != 0:
                print("Failed to create table %s" %item)

    def createTesterUser (self, user, password):
        createString = "CREATE USER \"%s\"@\"%%\" IDENTIFIED BY \"%s\""%(user, password)
        createString2 = "CREATE USER \"%s\"@\"localhost\" IDENTIFIED BY \"%s\""%(user, password)
        privString = "GRANT ALTER, CREATE, CREATE TEMPORARY TABLES, DELETE, INDEX, INSERT, LOCK TABLES, "
        privString += "SELECT, UPDATE ON %s.* TO "%self.db_name
        privString2 = privString + "\"%s\"@\"localhost\""%user
        privString += "\"%s\"@\"%%\""%user
        rc = self.dba.update (createString)
        if rc == 1:
            print ("Unable to create the \"%s\" user.  User may already exist."%user)
        rc = self.dba.update (createString2)
        if rc == 1:
            print ("Unable to create the \"%s\" user for localhost.  User may already exist."%user)

        print ("Setting up database privileges for the test user \"%s\"."%user)
        rc = self.dba.update (privString)
        if rc == 1:
            print ("Unable to setup remote privileges for \"%s\" user."%user)
        rc = self.dba.update (privString2)
        if rc == 1:
            print ("Unable to setup localhost privileges for \"%s\" user."%user)
        return


if __name__ == "__main__":
    main()
