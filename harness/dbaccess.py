import os, re, sys
import MySQLdb
import logging

class dbaccess:
    """ This class provide wrappers around DB access commands from MySQLdb """
    def __init__ (self, dbHost=None, dbUser=None, dbPass=None, dbName=None):
        self.log = logging.getLogger ("HarnessSQL")
        self.log.setLevel (logging.INFO)
        self.db=None  # This is the MySQL SQL object.
        self.dbHost=dbHost
        self.dbUser=dbUser
        self.dbPass=dbPass
        self.dbName=dbName

    def connect_db (self):
        """ Connect to the database using the variables defined in init. The resulting database
            object will be stored in the self.db variable. """
        try:
            self.db = MySQLdb.connect (
                host = self.dbHost,
                user = self.dbUser,
                passwd = self.dbPass,
                db = self.dbName)
        except MySQLdb.Error, dbErr:
            self.log.error ("Error %d: %s"%(dbErr.args[0], dbErr.args[1]))
            # TODO: Should add a logger here.
        return

    def disconnect_db (self):
        """ Disconnect database if there is an active db. """
        if self.db != None:
            try:
                self.db.close ()
            except MySQLdb.Error, dbErr:
                self.log.error ("Error %d: %s"%(dbErr.args[0], dbErr.args[1]))
                # TODO: Should add a logger here.
        return

    def query (self, sqlString):
        """ The function will grab a DB cursor, sent the sqlString with the cursor
            close the cursor so it will sync with the database, and try to catch any
            database error codes.  The return values are list of rows with dictionaries 
            for the column names as keys.  """
        rows = None
        try:
            self.log.debug (r"Sent SQL queryString: %s"%sqlString)
            cursor = self.db.cursor (MySQLdb.cursors.DictCursor)
            cursor.execute (sqlString)
            rows = cursor.fetchall ()
            cursor.close()
        except MySQLdb.Error, dbErr:
            raise
            self.log.error("SQL query failed with code %d: %s"%(dbErr.args[0], dbErr.args[1]))
        return rows

    def update (self, sqlString):
        """ This function will grab a DB cursor, sent an update message sqlString and
            close the cursor.  Return value is the number of rows updated base on the
            sqlString.  This function doesn't actually limit sqlString to update. """
        rowCount = 0
        try:
            self.log.debug (r"Sent SQL updateString: %s"%sqlString)
            cursor = self.db.cursor (MySQLdb.cursors.DictCursor)
            cursor.execute (sqlString)
            rowCount = cursor.rowcount
            cursor.close()
        except MySQLdb.Error, dbErr:
            raise
            self.log.error("SQL update failed with code %d: %s"%(dbErr.args[0], dbErr.args[1]))
        return rowCount
