import os, re, sys
import MySQLdb
from dbaccess import dbaccess
import logging
import csv

class AddTestSuite (dbaccess):
    def __init__ (self, csvTextFile, suiteName):
        print "Test CSV file:%s"%csvTextFile
        self.suiteName = suiteName
        dbaccess.__init__ (self, "qa.maxiscale.com", "tester", "tester", "autotest")
        try:
            self.connect_db ()
        except:
            # Failed to open DB
            print "Failed to open DB."
            sys.exit (0)
        testFileFD = open (csvTextFile, "r")
        # Run the files through the CSV reader
        csvLines = csv.reader (testFileFD)
        for line in csvLines:
            if (line[0] == "") or not (re.search ("(?i)\.py", line[0])):
                continue
            # Try to break the CSV line into expect values
            try:
                # This is an required field.
                fileName = line[0]
            except:
                # Bad line?
                print "Fail to process line file value : %s"%line
                continue
            try:
                # This is an required field.
                fileClass = line[1]
            except:
                # Bad line?
                print "Fail to process line class value : %s"%line
                continue
            try:
                # The product version the test is written for.
                targetVer = line[2]
            except:
                # If no product version we assume version 1 of the product
                targetVer = "1"  

            cRet, tid = self.checkEntryExist (fileName, fileClass, targetVer)
            if cRet == False:
                # For now don't add if there is already an entry
                print "DB already have entry for %s,%s,%s"%(fileName, fileClass, targetVer)
                continue
            else:
                self.addTestSuite (suiteName, fileName, fileClass, tid)
        try:
            self.disconnect_db()
        except:
            print "Failed to close db connection, already closed?"
        testFileFD.close()

    def checkEntryExist (self, fileName, fileClass, targetVer):
        sqlstring = "select File, Class, targetVersion, id from auto_test_case where File=\"%s\" and Class=\"%s\" and targetVersion=\"%s\""%(fileName, fileClass, targetVer)
        sqlRet = self.query (sqlstring)
        if sqlRet != ():
            return True, sqlRet[0]['id']
        return False, 0

    def addTestSuite (self, suiteName, fileName, fileClass, id):
        # Check if we already got this line.
        qRt = self.query ("select * from auto_test_suites where auto_suite_name=\"%s\" and testFile=\"%s\" and testClass=\"%s\" and id=%s"%(suiteName, fileName, fileClass, id))
        if qRt != ():
            print "Test %s : %s is already in %s suite"%(fileName, fileClass, suiteName)
            return

        sqlString = "insert into auto_test_suites (auto_suite_name, testFile, testClass, id) values (\"%s\",\"%s\",\"%s\", %s)"%(suiteName, fileName, fileClass, id)

        try:
            updateCnt = self.update (sqlString)
            if updateCnt < 1:
                print "Failed to update 1 row"
                return False
        except:
            print "SQL Update auto_test_suites failed"
            return False
        return True

if __name__ == "__main__":
    csvTextFile = sys.argv[1]
    suiteName = sys.argv[2]
    q = AddTestSuite (csvTextFile, suiteName)
