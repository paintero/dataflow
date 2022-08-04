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
        self.config = general.load_json_file("table", table_name)

    
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
        self.create_api_routes()


    # load the app config from json file
    def load_config(self, app_name):
        self.config = general.load_json_file("app", app_name)


    # retun app name
    def app_name(self):
        return self.config['meta_data']['name']

    # get list of tables in the app
    def tables(self):
        return self.config['tables']

    # load and create all of the tables in this app
    def create_tables(self):
        logging.info("Creating tables for App: " + self.app_name())
        self.table_objects = {}
        for table in self.tables():
            self.table_objects[table] = Table(table)

    # get a list of the API routes
    def api_routes(self):
        return self.config['api_routes'].keys()

    # check if api name is correct
    def is_api_route(self, api_route):
        return api_route in self.api_routes()

    #  load and create all of the api_routes in this app
    def create_api_routes(self):
        logging.info("Creating API routes for App: " + self.app_name())
        self.api_route_objects = {}
        for api_route in self.api_routes():
            self.api_route_objects[api_route] = Api_Route(self, api_route, self.config["api_routes"][api_route]) 


    # handle an api call
    def api_call(self, api_route, *args):
        logging.info("API call for App[" + self.app_name()
                     + "]: " + api_route)
        
        #validations
        if not self.is_api_route(api_route):
            general.raise_error("API route does not exist: " + api_route)
        
        api_route_config = self.config["api_routes"][api_route]

        if not api_route_config["table"] in self.tables():
            general.raise_error("API route [" + api_route + "] refers to a table [" + api_route_config['table'] + "] that does not exist in the app.")

        # if the API type is JSON then we can create the insert sql
        # based on the fields in the data file.
        if api_route_config["type"] == "JSON":
            json_data_file_name = args[0]
            json_data_config = general.load_json_file("data", json_data_file_name)
            # create insert statement
            insert = "INSERT INTO "
            insert += api_route_config["table"]
            insert += "("
            values = ""
            for field in json_data_config[api_route]['fields']:
                # note: add validation that fields match table def (or maybe do all validations when files are loaded)
                insert += field + ", "
                values += "?, "
            insert += ") values (" + values + ")"
            #print(insert)
            
            # now take the data from the file and run executemany
            for data_row in json_data_config[api_route]['data']:
                # print(data_row)
                pass


class Api_Route:
    """An object representing an api route for this app."""

    # initialise api route object and load the api route config json
    def __init__(self, parent_app, api_route, api_route_config):
        self.parent_app = parent_app
        self.api_route = api_route
        self.api_route_config = api_route_config
        logging.info("Creating API route: " + self.api_route)
        self.validate_api_route_config()
        
    def validate_api_route_config(self):
        # check the api route table matches a table object in the app
        table_in_api_route_config = self.api_route_config['table']
        list_of_tables_in_parent_app = self.parent_app.table_objects.keys()
        if not table_in_api_route_config in list_of_tables_in_parent_app:
            msg = "Table [" + self.api_route_config['table'] 
            msg += "] referenced in API route [" + self.api_route
            msg += "] is not a valid table in app [" + self.parent_app.app_name() + "]"
            general.raise_error(msg)

        # check the api fields match fields on the table
        list_of_api_route_fields = self.api_route_config['fields']
        print(list_of_api_route_fields)



    




        
