# dataflow
Work in progress

## Overview
Dataflow is a tool for quickly mocking up a system of applications or components and their dataflows.
Applications, their tables and APIs can be mocked up by creating JSON files.
Data can be injected from JSON files and then flows through the system as defined by the processes also defined in JSON.

## Object hierarchy
System
    - Application
        - Table
        - API route

E.g.
Library(System)
    - Lending UI (Application)
        - Members(table)
        - Books(table)
        - Lending(table)
        - Add_member_POST(API)
        - Add_book_POST(API)
        - Lend_POST(API)