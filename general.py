# general functions used across modules that don't
# have an obvious home

import logging
import sys
import sqlite3
import json

# this will ensure that logger writes to the same file
# defined in the main module
log = logging.getLogger(__name__)


# General function to log an error, print it, and exit the program
def raise_error(msg):
    logging.error(msg)
    print("ERROR: " + msg)
    sys.exit(0)


# General function to execute sql on the database
def exec_sql(sql):
    db_connection = sqlite3.connect('dataflow.db')
    db_cursor = db_connection.cursor()
    # Assume sql has more than one statement
    # and loop through each as sqlite3 can only run one at a time
    for statement in sql.split(";"):
        statement += ";"
        if statement != ";":
            logging.info("Executing sql: " + statement)
            db_cursor.execute(statement)
        
    db_connection.commit()
    db_connection.close()


# General function for loading a json definition file
def load_json_config(obj_type, obj_name):
    if obj_type == "app":
        folder = "apps"
    elif obj_type == "table":
        folder = "datamodel"
    else:
        raise_error("Unrecognised json definition type: " + obj_type)

    filepath = folder + "/" + obj_name + ".json"
    try:
        with open(filepath) as f:
            config = json.load(f)
            logging.info(folder + " config file loaded:" + filepath)
            return config 
    except FileNotFoundError:
        raise_error(folder + " config file not found: " + filepath)

