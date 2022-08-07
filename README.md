# dataflow
Work in progress

## Overview
Dataflow is a tool for quickly mocking up a system of applications or components and their dataflows.

Applications, their tables and APIs can be mocked up by creating JSON files.
Data can be injected from JSON files and then flows through the system as defined by the processes also defined in JSON.

Dataflow's two main objectives are to:

1. Allow system designers and business analysts to quickly mock up a system that actually functions and processes data. So that they can test their theoretical designs.
2. Output documentation for that system based on the data in the JSON files that define the various parts of the system.

## Object hierarchy
- System
  - Application
    - Table
    - API route
    - Process (design pending)

There can be one system, many applications, with many tables and many APIs.

E.g.
- Profit and Loss (System)
  - Trading (Application)
    - Trading Activity(table)
    - Positions(table)
    - Measures(table)
    - Add_Trade_POST(API route)
    - Get_Positions_GET(API route)
  - Finance (Application)
    - Accounts (table)
    - P&L Explains (table)
    - Accounts_POST (API route)
    - Accounts_GET (API route)
    - Create_account_record (Process)
    - Create_pl_explain_record (Process)

With such a system mocked up, you could load the Trading Application with sample test data, then run the processes that use the API routes to get data, process it and push it to the Finance Application.

## Documentation
Dataflow has classes for Applications, Tables, and API routes. It creates an object of each class in accordance with the JSON definition files.

### Application Class
`self.config{}` holds the entire API JSON config file.
Application name: `self.config['name']`
Application tables: `self.config['tables']`

`self.table_objects{}` holds the table objects created from the JSON table definitions. Access an object using `self.table_objects['table_name'].

`self.api_route_objects{}` holds the API route objects as defined in the JSON config file for the App.




