QA Autotest is a simple yet powerful automated test harness and test report database.  Its easy setup and support of rapid test case development make it an ideal starting place for a new software QA team who want automation to be a core part of their testing effort.  For more mature teams that lack an automation infrastructure, Autotest's suite management and test reporting facilities will seem familiar and will provide good visibility into test coverage.

There are two components to this project:
  * A test harness used for running automated tests written in Python
  * A reporting database with a web interface for pooling tests into suites and storing test execution details

## Database Features ##
  * Works with MySQL and apache2/httpd
  * Web-based user interface
  * Aggregate tests into suites for regular (nightly/weekly) or feature-specific regression tests
  * Test execution data can be logged and used for comprehensive test reports
  * Test to suite matrix view to ensure that all test cases in the database get run
  * New tests can be added easily by uploading a .csv file containing the new tests

## Harness Features ##
  * Runs on Linux and Windows
  * Works with Python 2.4, 2.5, 2.6 and 3.1`*`
  * Ideal for regular regression tests scheduled through cron
  * Native support for test cases written in Python
  * Tests written in Ruby, Perl, PHP, C/C++, Java, bash, etc. can be run in a simple Python wrapper
  * Clear test reporting and logging makes it easy to track down test failures
  * Can run interactively with the Autotest database or independently on an isolated machine
  * Easily add parameters to the harness that are unique to your own operating environment such as IPs, user names, passwords, etc.
`*`_Python 3.1 can run tests specified at the command line or through a .csv file.  Python 3 cannot access the test database until it is supported by [Python MySQLdb](http://sourceforge.net/projects/mysql-python/)._

## Getting Started ##
Fully documented setup and installation procedures.  To set up Autotest:
  1. [Prepare your MySQL server](http://code.google.com/p/qaautotest/wiki/MySQLSetup)
  1. [Install the database](http://code.google.com/p/qaautotest/wiki/InstallDatabase)
  1. [Run the sample tests](http://code.google.com/p/qaautotest/wiki/RunHarnessSampleTests)

Additional documents include:
  * [Creating your first test case](http://code.google.com/p/qaautotest/wiki/CreateTest)
  * [Running non-Python tests](http://code.google.com/p/qaautotest/wiki/NonPythonTestCase)
  * [Troubleshooting](http://code.google.com/p/qaautotest/wiki/Troubleshooting)

## Screen Shots ##
#### Output of the harness running the template tests included in the source code repository: ####

![http://qaautotest.googlecode.com/files/screenshot_harness_report.png](http://qaautotest.googlecode.com/files/screenshot_harness_report.png)
<br /><br />
#### Example of the test report page showing test pass/fail details and execution time: ####

![http://qaautotest.googlecode.com/files/screenshot_suite_report.png](http://qaautotest.googlecode.com/files/screenshot_suite_report.png)
<br /><br />
#### The test upload page where new tests are added to the database.  The existing tests are also visible: ####

![http://qaautotest.googlecode.com/files/screenshot_upload_tests.png](http://qaautotest.googlecode.com/files/screenshot_upload_tests.png)
<br /><br />
#### Test to suite matrix.  Use this to identify tests that are not a part of any suite.  It may be intentional, but it's always good to know which of your tests are not being run. ####

![http://qaautotest.googlecode.com/files/screenshot_test_to_suite_matrix.png](http://qaautotest.googlecode.com/files/screenshot_test_to_suite_matrix.png)
