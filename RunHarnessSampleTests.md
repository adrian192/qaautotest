# Introduction #

This page describes how to run the included sample test cases through the harness.

## Requirements ##
  * Linux host (tested with Ubuntu 10.04 and CentOS 5.5 x64)
  * Python 2.4 or later (**Ubuntu:** 2.6.5; **CentOS:** 2.4.3)
  * A local copy of the source code

To run a test suite from the database, or to store test results to the database, the following additional requirements must be met:
  * MySQL client for Python (**Ubuntu:** 1.2.2; **CentOS:** 1.2.1-1 [http://sourceforge.net/projects/mysql-python/](http://sourceforge.net/projects/mysql-python/); **Windows:** 1.2.3c1 [http://www.codegood.com/](http://www.codegood.com/))
  * The test case database must already be installed on either the local or a remote machine
  * The `database.ini` file in the harness directory must be configured

## Running the tests from the .csv file ##
  * From the trunk directory, run the harness, specifying the .csv file containing the tests:
```
$ ./harness/harness.py ./harness/csv/sample.csv -t ./tests
```
  * One test case is expected to pass, one is expected to fail.  Your results should look similar to the following:
```
[test@localhost trunk]$ ./harness/harness.py ./harness/csv/sample.csv -t ./tests
2010-08-17 10:18:21 SuiteDirectives          DEBUG    Running pre-suite validation.
2010-08-17 10:18:21 TestDirectives           DEBUG    Running pre-test case setup.
2010-08-17 10:18:21 Harness                  DEBUG    Run test harness_ut.py:PassingTestExample
2010-08-17 10:18:21 PassingTestExample       INFO     Running the PassingTestExample() test case.
2010-08-17 10:18:21 PassingTestExample       INFO     Test case passed.
2010-08-17 10:18:21 TestDirectives           DEBUG    Running post test case cleanup.
2010-08-17 10:18:21 Harness                  INFO     Test harness_ut.py:PassingTestExample: PASS
2010-08-17 10:18:21 TestDirectives           DEBUG    Running pre-test case setup.
2010-08-17 10:18:21 Harness                  DEBUG    Run test harness_ut.py:FailingTestExample
2010-08-17 10:18:21 FailingTestExample       INFO     Running the FailingTestExample() test case.
2010-08-17 10:18:21 FailingTestExample       ERROR    Test case failed.
2010-08-17 10:18:21 TestDirectives           DEBUG    Running post test case cleanup.
2010-08-17 10:18:21 Harness                  INFO     Test harness_ut.py:FailingTestExample: FAIL
2010-08-17 10:18:21 SuiteDirectives          DEBUG    Running post-suite validation.
2010-08-17 10:18:21 Harness                  REPORT   
################################################################################
#                             TEST RESULTS SUMMARY                             #
################################################################################

= harness_ut.py  ===============================================================
  FailingTestExample .....................................................FAIL
  PassingTestExample .....................................................PASS

Total run:    2
Total PASS:   1
Total FAIL:   1
Total SKIP:   0
Total XFAIL:  0
```


## Running an individual test from the command line ##
This can be a useful option when creating new test cases as it allows rapid execution of a single, explicit test case.
  * From the trunk directory, run the harness, specifying the test to run at the command line:
```
$ ./harness/harness.py harness_ut.py:PassingTestExample -t ./tests
```
  * The output will look similar to the above.  However, only the specified test will have been run.

## Running the tests from the database ##
### Configure the local database.ini file ###
Open the file harness/database.ini and update the values to match your own SQL server.  Default values are as follows:
```
[database]
host: localhost
db_name: autotest
user: tester
password: password
```

The keys hold the following data:
  * **host:** The host name or IP address of your database server.
  * **db\_name:** The name given to the database when it was installed, e.g. autotest.
  * **user:** A user account that has access rights to the test database.  This should be the user accounted created during the database installation.  The MySQL root account can be used, but this is not recommended.
  * **password:** The password corresponding to the user account that will administer the database.

### Create a new test suite in the database ###
  * Connect to your test database, e.g. `http://localhost/autotest`
  * From the drop-down menu in the top-left corner, select **Management**.
  * From the **Upload tests** menu, click the **Choose File** button.
  * Navigate to the harness/csv/sample.csv file and click **Update database**.
  * Switch from the **Upload tests** view to **Test suite management**.
  * In the text field next to **Create Suite**, enter a test suite name, e.g. sample.
  * Click **Create**.
  * Ctrl-click the two test cases from the left-side frame, i.e. `FailingTestExample` and `PassingTestExample`.
  * Click **Add tests to suite**.

You have now successfully created a test suite called `sample`.  This suite is stored in the database and contains two test cases.

### Run the tests, fetching the suite details from the database ###
  * From the trunk directory, run the harness, specifying suite name created above.  Optionally, add the --store option to archive the test pass/fail data into the database.
```
$ ./harness/harness.py sample -t ./tests --store
```
  * As before, one test case is expected to pass, one is expected to fail.  Your results should look similar to what was reported above.  However, one additional line will be displayed at the top of the output:
```
2010-05-17 10:34:36 Harness                  DEBUG    Running Suite ID 1: sample
```

This indicates that a suite called `sample`, stored in the database as suite ID 1 has been run.