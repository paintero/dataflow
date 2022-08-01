# general functions used across modules that don't
# have an obvious home

import logging
import sys
import sqlite3

# this will ensure that logger writes to the same file
# defined in the main module
log = logging.getLogger(__name__)

# log an error, print it, and exit the program
def raise_error(msg):
    logging.error(msg)
    print("ERROR: " + msg)
    sys.exit(0)

def exec_sql(sql):
    db_connection = sqlite3.connect('dataflow.db')
    db_cursor = db_connection.cursor()
    # Assume sql has more than one statement
    # and loop through each as sqlite3 can only run one at a time
    for statement in sql.split(";"):
        statement += ";"
        logging.info("Executing sql: " + statement)
        db_cursor.execute(statement)
        
    db_connection.commit()
    db_connection.close()
