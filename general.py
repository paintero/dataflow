# general functions used across modules that don't
# have an obvious home

import logging
import sys
import sqlite3
import json

# this will ensure that logger writes to the same file
# defined in the main module
log = logging.getLogger(__name__)

class HaltException(Exception): pass

# General function to log an error, print it, and exit the program
def raise_error(msg):
    logging.error(msg)
    print("ERROR: " + msg)
    #sys.exit(0)
    raise HaltException("Stop")


# General function to execute an sql script on the database
def exec_sql_script(sql_script):
    db_connection = sqlite3.connect('dataflow.db')
    with db_connection:
        db_connection.executescript(sql_script)

    db_connection.close()


# General function to load a dataset on the database
def exec_sql_many(sql_insert, dataset):
    db_connection = sqlite3.connect('dataflow.db')
    try:
        with db_connection:
            db_connection.executemany(sql_insert, dataset)
    except sqlite3.IntegrityError as err:
        raise_error("Database Integrity error. " + str(err))
    db_connection.close()


# General function for loading a json file
def load_json_file(obj_type, obj_name):
    if obj_type == "app":
        folder = "apps"
    elif obj_type == "table":
        folder = "datamodel"
    elif obj_type == "data":
        folder = "data"
    else:
        raise_error("Unrecognised JSON object type: " + obj_type)

    filepath = folder + "/" + obj_name + ".json"
    try:
        with open(filepath) as f:
            json_object = json.load(f)
            logging.info("JSON file loaded: " + filepath)
            return json_object 
    except FileNotFoundError:
        raise_error(folder + " JSON file not found: " + filepath)

# General function for checking if the values in one array are all
# in another array
def elements_from_arr1_not_in_arr2(arr1, arr2):
    x_not_in_y = []
    for x in arr1:
        if not x in arr2:
                x_not_in_y.append(x)
    return x_not_in_y

# General function for converting an array to a comma separated
# string of the elements. If replace_with is not blank then rather than 
# returning the items, a comma separated list of replace_with will be returned.
def array_to_comma_sep_string(arr, replace_with=""):
    comma_sep_string = ""
    count = 0
    len_array = len(arr)
    for item in arr:
        if replace_with == "":
            comma_sep_string += item
        else:
            comma_sep_string += replace_with
        count += 1
        if count >= len_array:
            return comma_sep_string
        comma_sep_string += ", "

