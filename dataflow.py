import json
import logging
import general

logging.basicConfig(
    filename="dataflow.log", 
    filemode="w", 
    format="%(asctime)s %(levelname)-8s %(message)s",
    datefmt="%H:%M:%S",
    level=logging.DEBUG)

class Table:
    """A database table object"""

    
    # initialise table object and load table def json
    def __init__(self, table_name):
        logging.info("Creating Table: " + table_name + ".")
        self.load_config(table_name)
        self.create_table()

    
    # load the table def json file
    def load_config(self, table_name):
        self.config = general.load_json_config("table", table_name)

    
    # return a list of the fields in the table
    def fields(self):
        return [*self.config['fields']]

    
    # return the number of fields in the table
    def num_fields(self):
        return len(self.fields())

    
    # return true if the table def has a primary key
    def has_primary_key(self):
        if 'primary_key' in self.config.keys():
            return True
        else:
            return False

    
    # return the sql to create the table
    def create_table_sql(self):
        sql = ""
        sql += "DROP TABLE IF EXISTS " + self.config['meta_data']['name'] + ";"
        sql += "\n" + "CREATE TABLE " + self.config['meta_data']['name'] + " ("

        num_fields = self.num_fields()
        n = 1
        for field in self.fields():
            sql = sql + "\n" + "  " + field
            if n < num_fields :
                sql += ","
            n += 1

        if self.has_primary_key():
            sql += ","
            sql += "\n" + "  CONSTRAINT " + self.config['primary_key']['name'] \
                + " PRIMARY KEY (" + self.config['primary_key']['fields'] + ")"
        
        sql += "\n);"
        return sql

    
    # create the table in the database
    def create_table(self):
        general.exec_sql(self.create_table_sql())


class App:
    """An app object representing an IT application (or component)."""

    # initialise app object and load the application config json
    def __init__(self, app_name):
        logging.info("Creating App: " + app_name + ".")
        self.load_config(app_name)
        self.create_tables()


    # load the app config from json file
    def load_config(self, app_name):
        self.config = general.load_json_config("app", app_name)


    # load and create all of the tables in this app
    def create_tables(self):
        logging.info("Creating tables for App: " + self.config['meta_data']['name'])
        self.tables = {}
        for table in self.config['tables']:
            self.tables[table] = Table(table)


    # handle an api call
    # def handle_api_call(self, api_name, )