# TQL - Transforming Text into SQL Queries

## Introduction

Welcome to the repository for **TQL (Table Query Language)** – an innovative project dedicated to simplifying the interaction between natural language and structured database queries. In an era where data is the backbone of decision-making, TQL emerges as a powerful tool to bridge the gap between everyday language and precise database queries. This README is your guide to understanding the project's journey, its significance, and the structure of this repository.

## Table of Contents

- [Project Overview](#project-overview)
- [Why TQL?](#why-tql)
- [How TQL Works](#how-tql-works)
- [The Models Behind TQL](#the-models-behind-tql)
- [The Road Ahead](#the-road-ahead)
- [Repository Structure](#repository-structure)

## Project Overview

**TQL (Table Query Language)** is a cutting-edge initiative that offers a seamless transition from natural language understanding to precise SQL queries. With TQL, you can input plain English text and watch it transform into intelligently crafted SQL queries, all while adhering to the underlying database schema. Our project aims to democratize the process of querying databases, making it accessible even to individuals with minimal SQL expertise.

## Why TQL?

In a world driven by data, the ability to access and manipulate databases is invaluable. TQL offers a natural language interface, turning everyday language into powerful SQL commands. Whether you are a seasoned data professional, a researcher seeking insights, a developer streamlining database interactions, or an everyday user in search of specific information, TQL makes data retrieval accessible to all.

## How TQL Works

The journey through TQL involves the following steps:

### 1. Input Natural Language

TQL's journey begins with your simple request. Users provide queries in plain, everyday language. TQL is ready to interpret these queries and transform them into structured SQL commands.

![TQL Initial UI](images/TQL-UI.jpeg)

### 2. Database Schema Integration

TQL is more than a language translator; it's a database expert. It understands the intricate structure and relationships within the database schema, ensuring data integrity and consistency.

### 3. SQL Query Generation

With all the pieces in place, TQL generates a tailored SQL query that aligns perfectly with your natural language request. This process guarantees accurate and reliable results.

![TQL Results](images/TQL-results.jpeg)

### 4. TQL Error Handling

Sometimes, the road to answers can be a bit bumpy. If TQL detects that your input text doesn't relate to any database or schema, it will kindly ask for valid input text to ensure a successful query.

![TQL Error Handling](images/TQL-Error_Handling.jpeg)

### Architechure

<img width="720" alt="image" src="https://github.com/jasmeeetSingh/TQL/assets/58945986/e20d8e5f-d95d-455e-858f-2ca39f3cd3f3">

## The Models Behind TQL

TQL relies on several models and approaches to perform its magic. These include:

- **Natural Language Processing (NLP)**: To interpret and translate user queries.
- **Mapping Logic**: To understand the structure and relationships within the data.
- **Machine Learning**: To generate accurate SQL queries tailored to the input text.

## The Models tested when building TQL

We tested the TQL logic on quite a few models, some of these include: 

- **T5**: To interpret and translate user queries.
- **T5- For code generation**: To understand the structure and relationships within the data.

## The Road Ahead

As we look to the future, TQL is far from reaching its final destination. There's a lot more to explore and improve, such as:

- **Advanced NLP Models**: Leveraging state-of-the-art NLP models for even more accurate translations.
- **Enhanced User Experience**: Continuously refining the user interface to make TQL even more user-friendly.
- **Support for Multiple Databases**: Expanding compatibility with various database management systems.
- **Community Contributions**: We welcome contributions from the community to enhance TQL and make it even more versatile.

## Repository Structure

Now, you may be wondering where all the magic happens. Here's a glimpse of the repository structure:

- `.ipynb_checkpoints`: Checkpoint files generated by Jupyter Notebooks.
- `Flask`: Files related to the Flask application.
  - `Templates`: HTML templates used in the Flask app.
  - `app.py`: The main Flask application file.
- `Model`: Files related to the project's machine learning model.
  - `baseModel.ipynb`: Jupyter Notebook containing the base model.
- `databaseDesign`: Database-related files.
  - `KaggleDBQA`: Files related to the Kaggle database.
    - `KaggleDBQA.csv`: Kaggle DBQA csv data.
    - `KaggleDBQAParser.ipynb`: Jupyter Notebook for parsing KaggleDBQA.
    - `KaggleDBQA_Parser.py`: Python script for parsing KaggleDBQA.
    - `KaggleDBQA_schema.csv`: Schema of KaggleDBQA.
    - `KaggleDBQA_tables.json`: JSON file for tables.
  - `__init__.py`: Initialization file.
- `MySQL`: MySQL database-related files.
  - `DatabaseUtils.py`: Python script for database utilities.
  - `__init__.py`: Initialization file.
  - `databaseUtilsRunner.ipynb`: Jupyter Notebook for running database utilities.
  - `sqlite_to_mysql.py`: Python script for converting SQLite to MySQL.
- `Spider`: Spider-related files.
  - `.ipynb_checkpoints`: Checkpoint files.
  - `dataLoad-checkpoint.ipynb`: Jupyter Notebook for data loading.
  - `__pycache__`: Python cache files.
  - `TableParserSpider.py`: Spider script.
  - `__init__.py`: Initialization file.
  - `dataLoad.ipynb`: Jupyter Notebook for data loading.
  - `tableParserSpiderRunner.ipynb`: Jupyter Notebook for running the spider.
- `WikiSQL`: Files related to WikiSQL data.
  - `WikiSQLDataLoad.ipynb`: Jupyter Notebook for loading WikiSQL data.
  - `wikiSQLprocesisng.ipynb`: Jupyter Notebook for processing WikiSQL data.
  - `__pycache__`: Python cache files.
- `main`: Main application files.
  - `TQLRunner.py`: Python script for TQL (Table Query Language) execution.
  - `tqlRunner.ipynb`: Jupyter Notebook for running TQL.
- `queryProcessing`: Query processing-related files.
  - `TableMapper.py`: Python script for mapping tables.
  - `tableMapperRunner.ipynb`: Jupyter Notebook for running the table mapper.
- `utils`: Utility functions and scripts.
  - `__init__.py`: Initialization file.
  - `utils.py`: Utility functions.
