import json
import logging
import general
import sqlite3
from eventq import *

logging.basicConfig(
    filename="dataflow.log", 
    filemode="w", 
    format="%(asctime)s %(levelname)-8s %(message)s",
    datefmt="%H:%M:%S",
    level=logging.DEBUG)


class System:
    """An object representing a system of applications"""
    def __init__(self, sys_name):
        self.app_objects = {}
        self.sys_name = sys_name
        self.event_q = EventQ()
        logging.info("Created system: " + sys_name)

    def register_application(self, app_name, app_object):
        self.app_objects[app_name] = app_object
        msg = "Registered Application " + app_name
        msg += " with System " + self.sys_name
        logging.info(msg)


class App:
    """An app object representing an IT application (or component)."""

    # initialise app object and load the application config json
    def __init__(self, application_name, system_object):
        logging.info("Creating App: " + application_name + ".")
        # so the app knows which system it is part of
        self.parent_system = system_object
        self.load_config(application_name)
        self.create_tables()
        self.create_api_routes()
        self.subscribe_to_event_topics()
        # so the system knows which apps it has
        system_object.register_application(application_name, self)


    # load the app config from json file
    def load_config(self, app_name):
        self.config = general.load_json_file("app", app_name, "config")
        self.app_name = self.config['app_name']
        self.app_folder = "config/" + self.config['app_folder']
        if 'event_topic_subscriptions' in self.config:
            self.event_topic_subscriptions = self.config['event_topic_subscriptions']


    def subscribe_to_event_topics(self):
        if 'event_topic_subscriptions' in dir(self):
            logging.info("Registering event Q subscriptions")
            for subscription in self.event_topic_subscriptions:
                s = Subscriber(self, self.app_name, subscription['topic'])
                self.parent_system.event_q.subscribe(s)
                logging.info("Subscribing App " + self.app_name + " to event Q topic " + subscription['topic'])

    # lookup a topic in the subscriptions and return the subcription dict
    def lookup_event_topic_subscription(self, topic):
        if 'event_topic_subscriptions' in dir(self):
            for subscription in self.event_topic_subscriptions:
                if topic == subscription['topic']:
                    return subscription
            return False


    # called by the eventQ to pass in a message which then fires the
    # appropriate api call to fetch the updated data
    def notify(self, message):
        # call the GET api route to retrieve the new data from the
        # originating app
        message.app_author.api_call(self, message.api_route, *message.params)
        # now call the PUT api route on this app to load the data
        # the PUT api route to use is defined in the app config event subscriptions
        subscription = self.lookup_event_topic_subscription(message.topic)
        post_api_route = subscription['post_api_route']
        print("post api route: ", post_api_route)
        print("params: ", *message.params)
        self.api_call(self, post_api_route, )

    
    def table_objects(self):
        return self._table_objects
    
    # load and create all of the tables in this app
    def create_tables(self):
        logging.info("Creating tables for App: " + self.app_name)
        self._table_objects = {}
        for table in self.config['tables']:
            self._table_objects[table] = Table(table, self)

    
    #  load and create all of the api_routes in this app
    def create_api_routes(self):
        logging.info("Creating API routes for App: " + self.app_name)
        self.api_route_objects = {}
        if 'api_routes' in self.config:
            for api_route in self.config['api_routes'].keys():
                self.api_route_objects[api_route] = Api_Route(self, api_route, self.config["api_routes"][api_route]) 
        else:
            logging.info("There are no API routes defined for app " + self.app_name)

    # check if api route name provided to the handler is that of an existing api route
    def is_api_route(self, api_route):
        return api_route in self.config['api_routes'].keys()

    # handle an api call
    def api_call(self, calling_app, api_route, *args):
        logging.info("Handling API call for App[" + self.app_name
                     + "]: " + api_route + " called by " + calling_app.app_name)
        
        #validations
        if not self.is_api_route(api_route):
            general.raise_error("API route does not exist: " + api_route)

        # call the API route's exec method
        self.api_route_objects[api_route].exec(calling_app, args)


class Table:
    """A database table object"""

    # initialise table object and load table def json
    def __init__(self, tab_name, app_object):
        logging.info("Creating Table: " + tab_name + ".")
        self.parent_app = app_object
        self.config = general.load_json_file("table", tab_name, self.parent_app.app_folder)
        self.create_table()

    def table_name(self):
        return self.config['name']

    # return a list of the fields in the table
    def fields(self):
        return [*self.config['fields']]
    
    # return the number of fields in the table
    def num_fields(self):
        return len(self.fields())

    def primary_key_name(self):
        return self.config['primary_key']['name']

    def primary_key_fields(self):
        return self.config['primary_key']['fields']
    
    # return true if the table def has a primary key
    def has_primary_key(self):
        if 'primary_key' in self.config.keys():
            return True
        else:
            return False
  
    # return the sql to create the table
    def create_table_sql(self):
        sql = ""
        sql += "DROP TABLE IF EXISTS " + self.table_name() + ";"
        sql += "\n" + "CREATE TABLE " + self.table_name() + " ("

        num_fields = self.num_fields()
        n = 1
        for field in self.fields():
            sql = sql + "\n" + "  " + field
            if n < num_fields :
                sql += ","
            n += 1

        if self.has_primary_key():
            sql += ","
            sql += "\n" + "  CONSTRAINT " + self.primary_key_name() \
                + " PRIMARY KEY (" + self.primary_key_fields() + ")"
        
        sql += "\n);"
        return sql
    
    # create the table in the database
    def create_table(self):
        general.exec_sql_script(self.create_table_sql())

        
class Api_Route:
    """A class representing an api route."""

    # initialise api route object and load the api route config json
    def __init__(self, parent_app, api_route, api_route_config):
        # a reference to the parent Application object
        self.parent_app = parent_app
        # the api route name
        self.api_route = api_route
        # the json config for the api taken from the Application config
        self.config = api_route_config
        self.api_method = self.config['method']
        self.api_type = self.config['type']
        # the topic which this route covers
        if 'topic' in self.config:
            self.topic = self.config['topic']
        else:
            msg = "API route " + self.api_route
            msg += " in application " + self.parent_app.app_name
            msg += " does not have a topic defined."
            general.raise_error(msg)
        
        logging.info("Creating API route: " + self.api_route)
        self.validate_config()


    def validate_config(self):
        # check the api route table matches a table object in the app
        # if the api is a straight table load from JSON data file
        if self.api_method == 'JSON':
            table_in_config = self.config['table']
            list_of_tables_in_parent_app = self.parent_app.table_objects().keys()
            if not table_in_config in list_of_tables_in_parent_app:
                msg = "Table [" + self.config['table'] 
                msg += "] referenced in API route [" + self.api_route
                msg += "] is not a valid table in app [" + self.parent_app.app_name + "]"
                general.raise_error(msg)

            # check the api fields match fields on the table
            list_of_api_route_fields = self.config['fields']
            list_of_table_object_fields = self.parent_app.table_objects()[table_in_config].fields()
            missing_fields = general.elements_from_arr1_not_in_arr2(list_of_api_route_fields, list_of_table_object_fields)
            if len(missing_fields) > 0:
                msg = "Fields in the API route [" + self.api_route
                msg += "] for App [" + self.parent_app.app_name
                msg += "] are not in the table: " + str(missing_fields)
                general.raise_error(msg)
    

    def validate_json_data_file(self):
        logging.info("Validating JSON data file " + self.exec_params["json_data_file_name"])
        # check the api_route name in the data file matches that of this api route object
        if not self.api_route == self.exec_params["json_data_file"]["api_route"]:
            msg = "API route name[" + self.exec_params["json_data_file"]["api_route"]
            msg += "] in data file [" + self.exec_params["json_data_file_name"]
            msg += "] does not match the route name [" + self.api_route
            msg += "] in the API route called."
            general.raise_error(msg)

    def validate_data_fields_match_table_fields(self):    
        # check that the field names in the datafile match those in the table definition
        fields_in_data_file = self.exec_params["json_data_file"]['fields']
        fields_in_table = self.parent_app.table_objects()[self.config['table']].fields()
        extra_fields_in_data_file = general.elements_from_arr1_not_in_arr2(fields_in_data_file, fields_in_table)
        fields_missing_from_data_file = general.elements_from_arr1_not_in_arr2(fields_in_table, fields_in_data_file)
        msg = ""
        if len(extra_fields_in_data_file) > 0:
            msg = "There are fields " + str(extra_fields_in_data_file)
            msg += " in the data file [" + self.exec_params["json_data_file_name"]
            msg += "] that are not in the API route["
            msg += self.api_route + "]."
        if len(fields_missing_from_data_file) > 0:
            if msg != "":
                msg += "\n"
            msg += "There are fields " + str(fields_missing_from_data_file)
            msg += " missing from the data file [" + self.exec_params["json_data_file_name"] + "]"
        if msg != "":
            general.raise_error(msg)


    def sql_insert_statement(self):
        insert_sql = "INSERT INTO "
        insert_sql += self.config['table']            
        insert_sql += " ("
        insert_sql += general.array_to_comma_sep_string(self.exec_params["json_data_file"]['fields'])
        insert_sql += ") VALUES ("
        insert_sql += general.array_to_comma_sep_string(self.exec_params["json_data_file"]['fields'], "?")
        insert_sql += ")"
        return insert_sql

    def load_data_from_json(self):
        self.validate_data_fields_match_table_fields()
        sql_insert_statement = self.sql_insert_statement()
        logging.debug(sql_insert_statement)
        data=[]
        for row in self.exec_params['json_data_file']['data']:
            tuple_row = tuple(row)
            data.append(tuple_row)
        
        logging.debug(data)
        general.exec_sql_many(sql_insert_statement, data)


    def update_eventq(self):
        if 'event_messages' in self.exec_params['json_data_file']:
            parent_app_object = self.parent_app
            for em in self.exec_params['json_data_file']['event_messages']:
                topic = em['topic']
                api_route = em['api_route']
                params = em["params"]
                eventm = Event_Message(parent_app_object, topic, api_route, params)
                self.parent_app.parent_system.event_q.append(eventm)
        else:
            pass    

    # execute the api route with the parameters passed in
    def exec(self, calling_app, args):
        logging.debug("Executing API: " + self.api_route + " called by App [" + calling_app.app_name + "]")
        self.exec_params = {} # use this to hold the parameters associated with a specific api route execution
        self.exec_params["args"] = {} # this will hold the API arguments as name-value pairs
        
        # if this is a route for a POST for a JSON data file
        if self.api_method == "POST" and self.api_type == "JSON":
            # POST data from a JSON data file
            # The api route fields are expected to be the same as the table def
            self.exec_params["json_data_file_name"] = args[0]
            self.exec_params["json_data_file"] = general.load_json_file('data', self.exec_params["json_data_file_name"], self.parent_app.app_folder)
            self.validate_json_data_file()
            self.load_data_from_json()
            self.update_eventq()
        
        # if this is a GET using an SQL script
        elif self.api_method == "GET" and self.api_type == "SQL":
            # check we have the number of args expected by the API
            if len(args) != len(self.config['args']):
                general.raise_error("Missing arguments in API call " + self.api_route)
            # create name/value pairs for the arg names and the arg values provided
            for n in range(0, len(args)):
                self.exec_params["args"][self.config["args"][n]] = args[n]
            logging.debug(self.exec_params["args"])
            sql = general.load_text_file(self.config['sql_file'], self.parent_app.app_folder)
            logging.debug(sql)
            
            results = general.exec_sql(sql, self.exec_params["args"])
            
            # save results to a json data file
            json_results = json.dumps(results, indent=2)
            output_file_name = self.topic
            for arg in self.exec_params['args']:
                output_file_name += "_"
                output_file_name += str(self.exec_params['args'][arg])
            output_file_name = calling_app.app_folder + "/GET_requests/" + output_file_name + ".json"
            with open(output_file_name, 'w') as f:
                f.write(json_results)

            
            

