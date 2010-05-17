import os, re, sys
import MySQLdb
from dbaccess import dbaccess
import logging
import csv

class AddTestCase (dbaccess):
    def __init__ (self, csvTextFile):
        print "Test CSV file:%s"%csvTextFile
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
            try:
                # Run flag, usually it is empty, could be "", skip, or xfail
                testRunFlag = line[3]
            except:
                # If nothing assume empty
                testRunFlag = ""
            try:
                # Should the test be run as root?
                runAsRoot = line[4]
                if len (runAsRoot) > 1:
                    # runAsRoot should be either a 0 or 1, if nothing don't change it.
                    runAsRoot = ""
                else:
                    try:
                        runAsRoot = int(runAsRoot)
                    except:
                        # Can't convert to int, so not a value run as root flag.
                        runAsRoot = ""
            except:
                # Should the test be run as root?  Default is 0, don't run as root.
                runAsRoot = 0
            try:
                # SVN location, this is a required value, but we don't need to force input into DB.
                svnLocation = line[5]
            except:
                svnLocation = ""

            if self.checkEntryExist (fileName, fileClass, targetVer):
                # For now don't add if there is already an entry
#                print "DB already have entry for %s,%s,%s"%(fileName, fileClass, targetVer)
                self.updateTestCase (fileName, fileClass, targetVer, svnLocation, runAsRoot, testRunFlag)
            else:
                print "Add new DB entry for %s,%s,%s"%(fileName, fileClass, targetVer)
                self.addTestCase (fileName, fileClass, targetVer, svnLocation, runAsRoot, testRunFlag)
        try:
            self.disconnect_db()
        except:
            print "Failed to close db connection, already closed?"
        testFileFD.close()

    def checkEntryExist (self, fileName, fileClass, targetVer):
        sqlstring = "select File, Class, targetVersion from auto_test_case where File=\"%s\" and Class=\"%s\" and targetVersion=\"%s\""%(fileName, fileClass, targetVer)
        sqlRet = self.query (sqlstring)
        if sqlRet != ():
            return True
        return False

    def getCurrentValue (self, fileName, fileClass, targetVer):
        sqlstring = "select * from auto_test_case where File=\"%s\" and Class=\"%s\" and targetVersion=\"%s\""%(fileName, fileClass, targetVer)
        sqlRet = self.query (sqlstring)
        if len (sqlRet) == 0:
            print " No existing DB entry for File=\"%s\", Class=\"%s\", and targetVersion=\"%s\""%(fileName, fileClass, targetVer)
        elif len (sqlRet) > 1:
            print " Multiple version of the same entry exist in DB.  Ask DB admin to cleanup. (Josh for now.)"
        elif len (sqlRet) == 1:
            return sqlRet[0]
        else:
            print "How did you get here?"
        return {}
        
    def updateTestCase (self, fileName, fileClass, targetVer, svnLocation, runAsRoot, testRunFlag):
        sqlLineHead = "update auto_test_case set "
        curVal = self.getCurrentValue (fileName, fileClass, targetVer)
        sqlLine = ""
        if svnLocation.strip() != "" and svnLocation.strip() != curVal['svnLocation']:
            sqlLine = sqlLine+"svnLocation=\"%s\","%svnLocation.strip()
        if runAsRoot.strip() != "" and runAsRoot.strip() != curVal['runAsRoot']:
            sqlLine = sqlLine+"runAsRoot=\"%s\","%runAsRoot.strip()
        if testRunFlag.strip() != curVal['testRunFlag']:
            sqlLine = sqlLine+"testRunFlag=\"%s\""%testRunFlag.strip()
        if sqlLine == "":
#            print "No values changed"
            return True
        sqlLine = sqlLine.rstrip (",")
        sqlLine = sqlLineHead + sqlLine + " where File=\"%s\" and Class=\"%s\" and targetVersion=%s"%(fileName, fileClass, targetVer)
        try:
            updateCnt = self.update (sqlLine)
            if updateCnt < 1:
                print "Failed to update 1 row"
                print sqlLine
                return False
            else:
                print "Updated File=\"%s\", Class=\"%s\", and targetVersion=%s"%(fileName, fileClass, targetVer)
        except:
            print "SQL Update test_case failed"
            return False
        return True


    def addTestCase (self, fileName, fileClass, targetVer, svnLocation, runAsRoot, testRunFlag):
        sqlLine = "insert into auto_test_case (File, Class"
        valueline = " values (\"%s\",\"%s\""%(fileName.strip(), fileClass.strip())
        if targetVer.strip() != "":
            sqlLine = sqlLine+", targetVersion"
            valueline = valueline+",\"%s\""%targetVer.strip()
        if svnLocation.strip() != "":
            sqlLine = sqlLine+", svnLocation"
            valueline = valueline+",\"%s\""%svnLocation.strip()
        if runAsRoot.strip() != "":
            sqlLine = sqlLine+", runAsRoot"
            valueline = valueline+",\"%s\""%runAsRoot.strip()
        if testRunFlag.strip() != "":
            sqlLine = sqlLine+", testRunFlag"
            valueline = valueline+",\"%s\""%testRunFlag.strip()
        sqlLine = sqlLine + ") "
        valueline = valueline +")"
        sqlString = sqlLine + valueline
        try:
            updateCnt = self.update (sqlString)
            if updateCnt < 1:
                print "Failed to update 1 row"
                return False
        except:
            print "SQL Update test_case failed"
            return False
        return True

if __name__ == "__main__":
    csvTextFile = sys.argv[1]
    q = AddTestCase (csvTextFile)
