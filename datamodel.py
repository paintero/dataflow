import json
import logging
import general

logging.basicConfig(filename="dataflow.log", filemode='w', level=logging.DEBUG)

class Table:
    """A database table object"""

    # initialise table object and load table def json
    def __init__(self, table_name):
        self.table_name = table_name        
        logging.info("Table object created: " + self.table_name + ".")
        self.load_table_def()
        general.exec_sql(self.create_table_sql())

    # load the table def json file
    def load_table_def(self):
        table_def_filepath = "datamodel/" + self.table_name + ".json"
        try:
            with open(table_def_filepath) as f:
                self.table_def = json.load(f)
                logging.info("Table def file loaded: " + table_def_filepath)
        except FileNotFoundError:
            general.raise_error("Table def file not found: " + table_def_filepath)

    # return a list of the fields in the table
    def fields(self):
        return [*self.table_def['fields']]

    # return the number of fields in the table
    def num_fields(self):
        return len(self.fields())

    # return true if the table def has a primary key
    def has_primary_key(self):
        if 'primary_key' in self.table_def.keys():
            return True
        else:
            return False

    # return the sql to create the table
    def create_table_sql(self):
        sql = ""
        sql += "DROP TABLE IF EXISTS " + self.table_name + ";"
        sql += "\n" + "CREATE TABLE " + self.table_name + " ("

        num_fields = self.num_fields()
        n = 1
        for field in self.fields():
            sql = sql + "\n" + "  " + field
            if n < num_fields :
                sql += ","
            n += 1

        if self.has_primary_key():
            sql += ","
            sql += "\n" + "  CONSTRAINT " + self.table_def['primary_key']['name'] \
                + " PRIMARY KEY (" + self.table_def['primary_key']['fields'] + ")"
        
        sql += "\n);"
        sql += "\n\n"

        return sql
