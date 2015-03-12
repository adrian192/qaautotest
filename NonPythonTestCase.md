# Introduction #

The harness is written in Python and is designed to run Python test code.  However, some tests may already be written in another language and it may not be desirable to rewrite them.  Or, there may be unique attributes of a language that make it difficult, if not impossible, to reproduce exactly in Python.

## Example ##

Running a non-Python test case only requires that the existing test case is encapsulated in a Python wrapper.  The following example illustrates how to do that:

```
import os
import logging
import subprocess

perl_code = r"""
#!/usr/bin/perl -w
use strict;

my $test_passed = 1;
# Test steps

if ($test_passed != 1)
{
    exit(1);
}
else
{
    exit(0);
}
"""

class MyPerlTest(object):
    def __init__(self, parameters):
        self.log = logging.getLogger("MyPerlTest")
        self.log.setLevel(parameters["log_level"])

    def run(self):
        self.log.info("Running MyPerlTest.")
        source_file = "my_perl_file.pl"
        try:
            file = open(source_file, "wb")
            file.write(perl_code)
            file.close()
        except (OSError, IOError):
            self.log.error("Unable to create the source file.")
            return False
        try:
            pipe = subprocess.Popen("perl %s" %(source_file),
                                    shell=True,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT)
            output = pipe.stdout.read()
            pipe.wait()
            os.remove(source_file)
        except:
            self.log.error("An error occurred running the perl script.")
            return False
        if pipe.returncode == 0:
            self.log.info("Test case passed.")
            return True
        else:
            self.log.error("Return code from the perl script: %s" %pipe.returncode)
            self.log.error("Output from the test is: %s" %output)
            return False
```