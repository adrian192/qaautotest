# Test Case Workflow #

When the harness used to run a test case, the following workflow is engaged:
  * The harness loads a set of working parameters that are used during test execution.  These parameters are specified at the command line or in an .ini file.
  * The test case, a Python class, is instantiated and the parameters are passed into it by the harness through the class `__init__()` method.
  * The harness calls the test case `run()` method.  This method should return `True` if the test case passed or `False` if the test case failed.
  * The harness will print out the test case status at the end of it's run.

## Defining Test Case Parameters ##

Usually, a test case will need some information about its operating environment in order to run.  This information can be in the form of a host name, an IP address, a user name and password, a mount point, etc.  There are two ways the harness can build its collection of parameters:
  * Parameters can be defined in the .ini file (easy).
  * Parameters can be defined with command line arguments (more work).

The template .ini file (found in the harness directory) contains a set of parameters that can be used for running your tests.  Additional parameters can be added following the same syntax.  These will be automatically passed into your test case's `__init__()` method as a dictionary.

For example, assume you have an .ini file called harness.ini that contains the following:
```
[harness]
test_dir: /home/user/svn/qaautotest/trunk/tests
log_dir: /tmp
log_level: 10               # DEBUG:10; INFO:20; WARNING:30; ERROR:40
stop_on_fail: False
run_as_root: False
iterations: 1
target_ip: 192.168.1.110
user_name: root
password: root
mount_point: /mnt/test
```

When you run the harness, pass in the .ini file as a command line argument: `./harness.py ./csv/sample.csv -c ./harness.ini`

When the harness calls your test case's `__init__()` method, it will pass in a dictionary containing all of the parameters, e.g.:
```
{"test_dir": "/home/user/svn/qaautotest/trunk/tests",
"log_dir": "/tmp"
"log_level": 10
"stop_on_fail": False
"run_as_root": False
"iterations": 1
"target_ip": "192.168.1.110"
"user_name": "root"
"password": "root"
"mount_point": "/mnt/test"}
```

Test case parameters can be changed for a new test run simply by changing the .ini file.

Obviously, new code can be added to handle options passed in at the command line.  However, doing so is outside the scope of this document.

## Test Case Structure ##

As described above, a test case is a Python class constructed in a specific way.  It must have an `__init__()` method for taking in the harness parameters and a `run()` method that returns `True` or `False`, which runs the test and indicates whether the test passed or failed.  The following is a template that can be used as the basis for any new test case:
```
import logging

class MyFirstTest(object):
    def __init__(self, parameters):
        self.parameters = parameters # Passed in from the harness
        self.log = logging.getLogger("MyFirstTest")
        self.log.setLevel(parameters["log_level"])

    def run(self):
        test_passed = True
        self.log.info("Running MyFirstTest.")
        if not self.test_step_one():
            test_passed = False
        if not self.test_step_two():
            test_passed = False
        return test_passed

    def test_step_one(self):
        # Your test code
        return True # or False if the test step failed

    def test_step_two(self):
        # Your test code
        return True # or False if the test step failed
```