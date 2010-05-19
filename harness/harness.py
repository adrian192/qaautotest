#!/usr/bin/env python

import sys, os, re, time
import copy
import random
import signal
import traceback
import threading
import logging
import logging.handlers
if sys.version_info[0] < 3:
    import ConfigParser as configparser
else:
    import configparser

import core as profile

try:
    import MySQLdb
    from dbaccess import dbaccess
except ImportError:
    pass


def main():
    config = profile.get_config()
    harness = Harness(config["log_dir"], config["log_level"])
    harness.initialize_database(os.path.join(os.path.split(os.path.abspath(__file__))[0], "database.ini"))
    harness.add_tests(config["test_dir"], config["tests"])
    harness.run_tests(config, config["store_to_database"], config["stop_on_fail"], config["iterations"])
    failures = harness.print_to_screen()
    if failures > 0:
        sys.exit(1)
    else:
        sys.exit(0)


class Harness(object):
    def __init__(self, log_dir=None, log_level=logging.DEBUG):
        self.harness_path = os.getcwd()
        self.__setup_logging(log_dir, log_level)
        self.dbA = None # initialize with self.initialize_datbase()
        self.test_dir = "" # initialize with self.add_tests()
        self.file_to_dir = {} # initialize with self.add_tests()
        self.test_list = [] # initialize with self.add_tests()
        self.suite_id = 0 # recorded by self.__build_test_list_from_database()
        self.test_start_time = 0 # recorded by self.run_tests()
        self.test_end_time = 0 # recorded by self.run_tests()
        self.test_results = {} # populated by self.run_tests()
    
    def __setup_logging(self, dir, log_level):
        # Set up the core logging engine
        logging.basicConfig(level=log_level,
                    format='%(asctime)s %(name)-24s %(levelname)-8s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')
        self.log = logging.getLogger("Harness")
        logging.addLevelName(100, "REPORT")
        
        # Set up the log file and log file rotation
        dir = os.path.abspath(dir)
        self.log_file = os.path.join(dir, "harness.log")
        rollover_count = 5
        log_fmt = logging.Formatter("%(asctime)s %(name)-24s %(levelname)-8s %(message)s",
                                    "%Y-%m-%d %H:%M:%S")
        if not os.access(dir, os.W_OK):
            self.log.warning("There is no write access to the specified log "
                             "directory %s  No log file will be created." %dir)
        else:
            try:
                log_handle = logging.handlers.RotatingFileHandler(self.log_file, "w",
                                                                  100*1024*1024,
                                                                  rollover_count)
                log_handle.setFormatter(log_fmt)
                logging.getLogger("").addHandler(log_handle)
                if os.path.exists(self.log_file):
                    log_handle.doRollover()
            except:
                self.log.warning("Failed to rollover the log file.  The "
                                 "results will not be recorded.")
    
    def initialize_database(self, ini):
        try:
            dir(MySQLdb)
        except NameError:
            self.dbA = None
            return False
        config = configparser.SafeConfigParser()
        try:
            config.read(ini)
        except configparser.MissingSectionHeaderError:
            self.log.warning("The database configuration file %s is not in the "
                             "expected format.  It contains no section headers."
                             %ini)
            self.dbA = None
            return False
        if not config.has_section("database"):
            self.log.warning("The database configuration file %s has no section "
                  "\"[database]\".  This section is required." %ini)
            self.dbA = None
            return False
        try:
            host = config.get("database", "host").split()[0]
            user = config.get("database", "user").split()[0]
            password = config.get("database", "password").split()[0]
            db_name = config.get("database", "db_name").split()[0]
        except configparser.NoOptionError:
            self.log.warning("Unable to retrieve the required information from "
                             "the database configuration file.  Ensure that "
                             "the host, user, password, and datbase name are "
                             "specified.")
            self.dbA = None
            return False
        
        # Create the DB object, it is not connected yet.  Any function using
        # this need to open and close it.
        try:
            self.dbA = dbaccess(host, user, password, db_name)
            return True
        except:
            self.log.info("Unable to connect to the database.  Test results "
                          "will not be reported to the database.")
            self.dbA = None
            self.notUpdateDB = True
            return False
        
    def add_tests(self, test_dir, tests):
        file_dict = {}
        self.test_dir = os.path.abspath(test_dir)
        if not os.path.exists(self.test_dir):
            self.log.error("The test directory provided %s doesn't exist."
                           %self.test_dir)
            sys.exit(1)
        
        # Generate a list of all files in the test path
        for path, dirs, files in os.walk(self.test_dir):
            for f in files:
                file_dict[f] = path
        self.file_to_dir = file_dict
        
        if re.search("(?i)\.csv$", tests):
            test_list = self.__build_test_list_from_csv(tests)
        elif tests.find("py:") != -1:
            test_list = self.__build_test_list_from_cli(tests)
        else:
            test_list = self.__build_test_list_from_database(tests)
        if test_list == None:
            self.log.error("Unable to generate a test list from the provided "
                           "input: %s" %tests)
            sys.exit(1)
        self.test_list = test_list
        return True
    
    def __build_test_list_from_csv(self, csv_file):
        self.dbA = None
        import csv
        test_list = []
        try:
            csv_file = open(csv_file, "r")
        except (OSError, IOError):
            self.log.error("Unable to open the test .csv file %s" %csv)
            return None
        
        tf = csv.reader(csv_file)
        for item in tf:
            if item == []: # probably an empty line or a DOS character
                continue
            if re.search("(?i)\.py", item[0]):
                test_list.append(item)
        csv_file.close()
        return test_list
    
    def __build_test_list_from_cli(self, cli):
        self.dbA = None
        test_list = []
        try:
            file_name, class_name = cli.split(":")
            file_name = file_name.strip()
            class_name = class_name.strip()
            test_list.append([file_name, class_name, 1, "", ""])
            return test_list
        except:
            return None
    
    def __build_test_list_from_database(self, suite):
        test_list = []
        if self.dbA == None:
            self.log.error("A suite name was specified but no connection to "
                           "the test database could be made.")
            return None
        try:
            self.dbA.connect_db()
        except:
            self.log.error("Unable to connect to database to check for the "
                           "suite named \"%s\".  Test run failed." %suite)
            sys.exit(1)
        # suite query.
        qReturn = self.dbA.query("select * from auto_suite_list where suite_name=\"%s\"" %suite)
        if qReturn == ():
            self.log.error("The given suite \"%s\" is not in the autotest "
                           "database." %suite)
            self.dbA.disconnect_db()
            sys.exit(1)

        # First get the suite ID from the query
        try:
            self.suite_id = qReturn[0]['id']
            self.log.debug("Running Suite ID %s: %s" %(str(self.suite_id), suite))
        except:
            # Should never get here.
            raise
        
        # If the suite is in the database check which tests are part of this suite.
        qReturn = self.dbA.query("select id, testFile, testClass from auto_test_suites where auto_suite_name=\"%s\"" %suite)
        if qReturn == ():
            self.log.error("Given suite \"%s\" does not have any tests "
                           "associated with it." %suite)
            self.dbA.disconnect_db()
            sys.exit(1)

        # If we got the suite and we have tests in the suite, build the testList.
        # We need to query the test list to get other info, like xfail, skip values.
        atc_File = []
        atc_Class = []
        atc_list = [] # Create a pair with File and Class, to allow same test name in different files.
        for item in qReturn:
            file_name = item['testFile']
            class_name = item['testClass']
            # Do a search on the auto_test_case list for testFile and testClass
            if file_name not in atc_File:
                atc_File.append(file_name)
            if class_name not in atc_Class:
                atc_Class.append(class_name)
            atc_list.append("%s:%s"%(file_name, class_name))
        atc_File = "\"%s\""%"\",\"".join(atc_File)
        atc_Class = "\"%s\""%"\",\"".join(atc_Class)
        testListReturn = self.dbA.query("select File, Class, targetVersion, "
                                        "testRunFlag, runAsRoot from "
                                        "auto_test_case where File in (%s) "
                                        "and Class in (%s) order by File, Class"
                                        %(atc_File, atc_Class))
        if testListReturn == ():
            self.log.error("Failed to create test case list from the database.")
            self.dbA.disconnect_db()
            sys.exit(1)
        # Update the testList with testFileName, testClassName, targetVersion, runTimeFlag, Discription
        # The targetVersion and Discription will be '' string.
        for item in testListReturn:
            if ("%s:%s" %(item['File'], item['Class']) in atc_list):
                test_list.append([item['File'], item['Class'],
                                 item['targetVersion'], item['testRunFlag'],
                                 item['runAsRoot'], ''])
        return test_list
    
    def run_tests(self, config=None, store_to_database=False, 
                  stop_on_fail=False, iterations=1, threads=0):
        directives = profile.SuiteDirectives(config)
        if not directives.start():
            self.log.error("One of the pre-suite directives failed.  The tests "
                           "cannot be run.")
            sys.exit(1)
        self.test_start_time = int(time.time())
        
        ######################################################################
        # Single threaded running of tests
        if threads <= 1:
            for i in range(iterations):
                if iterations > 1:
                    self.log.info("Executing test iteration %s" %(i + 1))
                for item in self.test_list:
                    result = self.__execute_test_case(config, item)
                    if (result == False) and (stop_on_fail == True):
                        self.log.info("stop-on-fail is set.  Exiting.")
                        os._exit(1)
        
        ######################################################################
        # Multi-threaded test execution
        # BUGBUG: Doesn't work right now
        else:
            while True:  # Break if not loop
                for item in self.test_list:
                    tid = threading.Thread(None, self.runTest, None, (item, varObj))
                    self.threadList.append(tid)
                    tid.start()
                    # If we are doing threading, when we hit the maximum thread list 
                    # wait and let tests complete before starting more threads.
                    while (len(self.threadList) >= self.thread):
                        self.__checkThreadTests()
                        if item == testList[-1]:
                            # If the test we just started is the last test, get 
                            # out of this while loop.
                            break
                        time.sleep(1)
                while (len(self.threadList) > 0):
                    #self.log.error("Current threadList = %s"%len(self.threadList))
                    for tRun in self.threadList:
                        if not tRun.isAlive():
                            self.threadList.pop(self.threadList.index(tRun))
                    time.sleep(1)
            while (len(self.threadList) > 0):
                #self.log.error("Current threadList = %s"%len(self.threadList))
                for tRun in self.threadList:
                    if not tRun.isAlive():
                        self.threadList.pop(self.threadList.index(tRun))
                time.sleep(1)
        
        ######################################################################
        # Run the post-test check and report the results to the database.
        if not directives.end():
            self.log.error("One of the post-suite directives failed.  The "
                           "system may not have been restored to the same "
                           "state it was in when the test started.")
        self.test_end_time = int(time.time())
        if store_to_database:
            self.__update_database()
        return
    
    def __execute_test_case(self, config, test_case_params):
        test_status = {"test_file": "",
                       "test_class": "",
                       "target_version": 0,
                       "run_flag": None,
                       "startTime": 0, # wall-clock time start
                       "endTime": 0, # wall-clock time end
                       "stime": 0, # kernel time duration
                       "utime": 0, # user time duration
                       "status": "FAIL",
                       "message": ""}
        rar_dict = {"": False,
                    0: False,
                    "0": False,
                    "False": False,
                    False: False,
                    None: False,
                    "disabled": False,
                    1: True,
                    "1": True,
                    "True": True,
                    True: True,
                    "enabled": True}
        
        test_config = copy.copy(config)
        test_status["test_file"] = test_case_params[0]
        test_status["test_class"] = test_case_params[1]
        test_status["target_version"] = test_case_params[2]
        test_status["run_flag"] = test_case_params[3]
        if len(test_case_params) > 4:
            try:
                test_config["run_as_root"] = rar_dict[test_case_params[4]]
            except KeyError:
                self.log.debug("run_as_root value for test %s:%s is set to '%s'."
                               %(test_status["test_file"],
                                 test_status["test_class"], test_case_params[4]))
                test_config["run_as_root"] = False
        
        #######################################################################
        # Various checks to go through before running the test.
        # If the test is set to "SKIP", dont' bother running it.
        if re.match("(?i)skip", test_status["run_flag"]):
            test_status["status"] = "SKIP"
            self.__process_result(test_status)
            return True
        
        # Check the pre-test case directives.  This sets up the test 
        # environment.  If it fails, the test case will likely not run.
        try:
            directives = profile.TestCaseDirectives(self.file_to_dir[test_status["test_file"]],
                                                    test_config)
        except KeyError:
            self.log.error("The test file %s does not exist in the specified "
                           "test path %s"
                           %(test_status["test_file"], self.test_dir))
            return False
            
        if not directives.start():
            self.log.error("One of the pre-test case directives failed.  The "
                           "test cannot be run.")
            directives.end()
            test_status["status"] = "FAIL"
            self.__process_result(test_status)
            return False
        
        # Make sure the test file is in the path so it can be imported.
        try:
            if self.file_to_dir[test_status["test_file"]] not in sys.path:
                sys.path.append(self.file_to_dir[test_status["test_file"]])
        except:
            self.log.error("Unable to find the test case %s in any file in the "
                           "test path %s." %(test_status["test_file"], self.test_dir))
            test_status["status"] = "FAIL"
            self.__process_result(test_status)
            return False
        
        # Import the test file and instantiate the test class.
        try:
            os.chdir(self.file_to_dir[test_status["test_file"]])
            exec("import %s" %test_status["test_file"].split(".")[0])
            exec("test_object = %s.%s(test_config)"
                 %(test_status["test_file"].split(".")[0],
                   test_status["test_class"]))
            os.chdir(self.harness_path)
        except AttributeError:
            self.log.error("The test case %s cannot be found in the file %s."
                           %(test_status["test_class"],
                             test_status["test_file"]))
            test_status["status"] = "FAIL"
            if os.getcwd() != self.harness_path:
                os.chdir(self.harness_path)
            self.__process_result(test_status)
            return False
        except:
            self.log.error("The following error occurred instantiating the "
                           "test class: %s" %traceback.format_exc())
            test_status["status"] = "FAIL"
            if os.getcwd() != self.harness_path:
                os.chdir(self.harness_path)
            self.__process_result(test_status)
            return False
        #######################################################################
        
        test_status["startTime"] = time.time()
        test_status["endTime"] = time.time()
        self.log.debug("Run test %s:%s" %(test_status["test_file"],
                                          test_status["test_class"]))
        os_times = os.times()
        user_time_start = user_time_end = os_times[0]
        kernel_time_start = kernel_time_end = os_times[1]
        try:
            os.chdir(self.file_to_dir[test_status["test_file"]])
            exec("test_status[\"status\"] = test_object.run()")
            del test_object
            os.chdir(self.harness_path)
        except AssertionError:
            self.log.error("The test case failed with an AssertionError and "
                           "will exit immediately.")
            os._exit(1)
        except:
            self.log.error("Handled exception %s" %traceback.format_exc())
            if os.getcwd() != self.harness_path:
                os.chdir(self.harness_path)
        os_times = os.times()
        user_time_end = os_times[0]
        kernel_time_end = os_times[1]
        test_status["stime"] = kernel_time_end - kernel_time_start
        test_status["utime"] = user_time_end - user_time_start
        test_status["endTime"] = time.time()
        
        if not directives.end():
            self.log.error("One of the post-test case directives failed.  The "
                           "test will be marked as failed.")
            test_status["status"] = "FAIL"
            self.__process_result(test_status)
            return False
        
        if not self.__process_result(test_status):
            return False
        return True
    
    def __checkThreadTests(self):
        """ If we are running multiple thread, check if threads are done, if
        it is pop it from the threadList. """
        for tRun in self.threadList:
            if not tRun.isAlive():
                self.threadList.pop(self.threadList.index(tRun))

    def __process_result(self, test_status):
        """ This will process the test results.  The return value from the test 
        run could be of two types:  One is an Boolean for test pass or fail.  
        Two, a tuple or list with 2 values, first value is the boolean, second 
        value is a dictionary for test specific results. 
        """
        final_status = "FAIL"  # default to fail -- override with other status
        recorded_result = test_status["status"]
        string_extra = ""
        # Check what is the first or only return value, this value must be either
        # a text string of pass/fail or boolean True/False.  If testResult is 
        # a tuple/list, then the first value in the tuple/list is the pass/fail value.
        if isinstance(recorded_result, str):
            if re.match("(?i)pass", recorded_result):
                final_status = "PASS"
            elif re.match("(?i)skip", recorded_result):
                final_status = "SKIP"
        elif isinstance(recorded_result, bool):
            if recorded_result == True:
                final_status = "PASS"
        elif isinstance(recorded_result, (list, tuple)):
            # This is a list/tuple so the first value must be boolean or string.
            # Second value is expected to be a dictionary.
            if isinstance(recorded_result[0], bool):
                if recorded_result[0] == True:
                    final_status = "PASS"
            elif isinstance(recorded_result[0], str):
                if re.match("(?i)pass", recorded_result[0]):
                    final_status = "PASS"
            else:
                self.log.error("Unable to process tests result for %s:%s.  "
                               "Test status valued was recorded as %s"
                               %(test_status["test_file"],
                                 test_status["test_class"],
                                 recorded_result[0]))
            if not isinstance(recorded_result[1], dict):
                self.log.error("The second argument returned from the test "
                               "%s:%s is not a one-level dictionary."
                               %(test_status["test_file"],
                                 test_status["test_class"]))
            else:
                # Convert the dictionary to a flat string.
                for key, value in recorded_result[1].items():
                    try:
                        if type (value) == float:
                            # Float, need to convert to text first.
                            # Get upto 4 decimal points.
                            value = "%0.4f"%value
                        string_extra += "%s:%s," %(key, value)
                    except:
                        self.log.error("Unable to process test result "
                                       "dictionary into text, key:%s, value:%s"
                                       %(key, value))
            # Change string_extra to None if there are no items.
            if string_extra == "":
                string_extra = None
        test_status["test_data"] = string_extra
        if re.search("(?i)xfail", test_status["run_flag"]):
            # If the run is supposed to fail, and it did fail, the status is
            # set to XFAIL, i.e. a status indicating a known failure.
            if final_status == "FAIL":
                final_status = "XFAIL"
            else:
                self.log.error("Test %s:%s was expected to failed, but passed."
                               %(test_status["test_file"],
                                 test_status["test_class"]))
                final_status = "FAIL"
                
        test_status["status"] = final_status
        self.log.info("Test %s:%s: %s" %(test_status["test_file"],
                                         test_status["test_class"],
                                         test_status["status"]))
        self.test_results["%s:%s" %(test_status["test_file"],
                                    test_status["test_class"])] = test_status
        
        if test_status["status"] == "FAIL":
            return False
        else:
            return True
        
    def __update_database(self):
        job_id = 0
        if self.dbA == None:
            return False
        try:
            self.dbA.connect_db()
        except:
            self.log.error("The following exception was raised accessing the "
                           "database: %s" %traceback.format_exc())
            return False
        
        # insert into the job table and get back the insert ID, the insertID is the new jobID
        addJobQuery = "insert into auto_test_jobs (startTime, status, version, jobHTML, primeTestUnit, suiteID) "+\
                      "values (%s, '%s', '%s', '%s', '%s', %s)" \
                      %(self.test_start_time, "running", "1", "none", get_local_ip(), self.suite_id)
        dbReturn = self.dbA.update(addJobQuery)
        if dbReturn != 0: # If we added at least 1 row to the table.
            job_id = self.dbA.db.insert_id()  # The insert ID is the jobID, this is the primary ID field in the table.
        
        for label, test in self.test_results.iteritems():
            # 3: Compose the update line
            update_line = ""
            if test["startTime"] != None:
                update_line += "startTime=%f," %test["startTime"]
            if test["endTime"] != None:
                update_line += "endTime=%f," %test["endTime"]
                update_line += "runTime=%f," %(test["endTime"] - test["startTime"])
            if test["status"] != None:
                update_line += "testStatus='%s'," %test["status"]
            if test["test_data"] != None:
                update_line += "testData='%s'," %test["test_data"]
            if test["stime"] != None:
                update_line += "stime=%f," %test["stime"]
            if test["utime"] != None:
                update_line += "utime=%f," %test["utime"]
            update_line = update_line.rstrip(",")
            
            query_line = "insert into auto_test_item set testFile='%s',testClass='%s',jobID=%s,%s" \
                        %(test["test_file"], test["test_class"], job_id, update_line)
            dbReturn = self.dbA.update(query_line)
            if dbReturn == 0:
                self.log.error("Failed to update the database with data.")  
        
        self.dbA.disconnect_db()
        return True

    def print_to_screen(self):
        """ This will take the test result dic and print it to screen. """
        if len(self.test_results) == 0:
            self.log.warning("No results recorded in test output.")
            return
        pass_count = 0
        fail_count = 0
        skip_count = 0
        xfail_count = 0
        total_count = len(self.test_results)
        keys = self.test_results.keys()
        keys.sort()
        
        final_output = "\r\n"
        final_output += "".ljust(80, "#")+"\r\n"
        final_output += "#"+"TEST RESULTS SUMMARY".center(78)+"#\r\n"
        final_output += "".ljust(80, "#")+"\r\n"
        
        current_file = ""
        for key in keys:
            value = self.test_results[key]["status"]
            file_name, class_name = key.split(":")
            if value.find("PASS") == 0:
                pass_count += 1
            elif value.find("FAIL") == 0:
                fail_count += 1
            elif value.find("SKIP") == 0:
                skip_count += 1
            elif value.find("XFAIL") == 0:
                xfail_count += 1
            if file_name != current_file:
                current_file = file_name
                final_output += "\n" + ("= " + file_name + "  ").ljust(80, "=") + "\r\n"
            final_output += ("  " + str(class_name) + " ").ljust(74, ".") + value + "\r\n"
        
        final_output += "\r\n"
        final_output += "Total run:    %s\r\n"% total_count
        final_output += "Total PASS:   %s\r\n"%pass_count
        final_output += "Total FAIL:   %s\r\n"%fail_count
        final_output += "Total SKIP:   %s\r\n"%skip_count
        final_output += "Total XFAIL:  %s\r\n"%xfail_count
        if (total_count != pass_count + fail_count + skip_count + xfail_count):
            final_output += "NOTE: Some tests didn't report results.\r\n\r\n"
        self.log.log(100, final_output)
        return fail_count
    
    
def intrupt_handle(sig, b):
    print("\nCaught signal: %s.  Exiting." %str(sig))
        # Restore signal handler default
    if os.name == "posix":
        signal.signal(signal.SIGHUP, signal.SIG_DFL)
        signal.signal(signal.SIGQUIT, signal.SIG_DFL)
        signal.signal(signal.SIGALRM, signal.SIG_DFL)
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    signal.signal(signal.SIGTERM, signal.SIG_DFL)
    os._exit(1)
    
def get_local_ip():
    """ Return the IP address of the local machine. """
    import socket
    if sys.platform == "win32":
        try:
            return socket.gethostbyname(socket.gethostname())
        except:
            return ""
    import fcntl
    import struct
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256s', "eth0"[:15])
    )[20:24])


if __name__ == "__main__":
    ## Setup the signal handles, mainly use for safe Ctrl-C exits.
    if os.name == "posix":
        # These don't do a lot of good on windows.
        signal.signal(signal.SIGHUP, intrupt_handle)
        signal.signal(signal.SIGQUIT, intrupt_handle)
        signal.signal(signal.SIGALRM, intrupt_handle)
    # General sig that could happen on windows systems.
    signal.signal(signal.SIGINT, intrupt_handle)
    signal.signal(signal.SIGTERM, intrupt_handle)
    main()
    
