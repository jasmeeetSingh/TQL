# TQL - Transforming Text into SQL Queries

## Introduction

Welcome to the repository for **TQL (Table Query Language)** – an innovative project dedicated to simplifying the interaction between natural language and structured database queries. In an era where data is the backbone of decision-making, TQL emerges as a powerful tool to bridge the gap between everyday language and precise database queries. This README is your guide to understanding the project's journey, its significance, and the structure of this repository.

## Table of Contents

- [Project Overview](#project-overview)
- [Why TQL?](#why-tql)
- [Data Overview](#data-overview)
- [How TQL Works](#how-tql-works)
- [The Models Behind TQL](#the-models-behind-tql)
- [The Road Ahead](#the-road-ahead)
- [Repository Structure](#repository-structure)

## Project Overview

**TQL (Table Query Language)** is a cutting-edge initiative that offers a seamless transition from natural language understanding to precise SQL queries. With TQL, you can input plain English text and watch it transform into intelligently crafted SQL queries, all while adhering to the underlying database schema. Our project aims to democratize the process of querying databases, making it accessible even to individuals with minimal SQL expertise.

## Data Overview

We mainly used two data sources:

1. Spider Dataset
   
2. KaggleDBQA

We explored the WikiSQL as well, but since our area of research was multi-tabled schemas, we used first two data sources.


We split the data into 2 CSV files:

1. CSV containing schemas.

![image](https://github.com/jasmeeetSingh/TQL/assets/71340782/f863e55c-0bca-4aa9-b06e-3d8050d13c4f)


2. CSV containing train-test data - All the queries across the two datasets that are used for training and validation.

![image](https://github.com/jasmeeetSingh/TQL/assets/71340782/85bb31db-8008-4044-b4f0-f968aa70dbec)


## Why TQL?

In a world driven by data, the ability to access and manipulate databases is invaluable. TQL offers a natural language interface, turning everyday language into powerful SQL commands. Whether you are a seasoned data professional, a researcher seeking insights, a developer streamlining database interactions, or an everyday user in search of specific information, TQL makes data retrieval accessible to all.

TQL is really good at figuring out and matching schema info. It helps us understand the data model for any given query and the related underlying schema. This tool can handle any type of schema, no matter how many tables, columns, or rows there are in the dataset.
What's cool is our way of understanding the data model – we don't have to read the actual data.


![image](https://github.com/jasmeeetSingh/TQL/assets/71340782/86eaab66-4508-4960-9f5f-b78dcf8f52da)

![image](https://github.com/jasmeeetSingh/TQL/assets/71340782/7da17df7-d0f9-480d-9d90-efa5f17a04a4)


## Comparison of TQL output with other out solutions in the market

For any given query, TQL is able to parse and accurately map the schema information to understand the data model context of any given underlying schema. 
The tool is capable of handling any given schema, no matter how many tables, columns, or rows in a dataset. 

Our unique approach to understanding the data model concept means we never have to read the underlying data. ***We just need the table names and the column names in the schema.***

Sample test case: 

The user inputs: ***What are the ids of the students who either registered or attended a course?***

Output from ChatGPT

![image](https://github.com/jasmeeetSingh/TQL/assets/71340782/b08ad8d1-a9ff-470c-b24c-bdc512a06fe0)

Although ChatGPT is able to generate the correct SQL query, it's not able to use the correct table names and only guesses what the table names would be. 

Output from LLama2 model

![image](https://github.com/jasmeeetSingh/TQL/assets/71340782/531db7a3-4afb-42c1-8378-bab2edeeee38)

If we pass all the tables we have to a state-of-the-art LLama2 model, we still get an incorrect query which doesn't give us correct results


***Note: Passing all the tables in a schema would be highly impractical. Since passing details of 100s of tables in a schema would be a very inefficient process.***


Output from **TQL**

![image](https://github.com/jasmeeetSingh/TQL/assets/71340782/d361f4cd-073b-49ed-bec9-29646a59bcc6)

Since TQL is able to understand the context in a data model, it is able to correctly map the right set of tables and which is then passed to a LLama2 model for query generation.


## How TQL Works

The journey through TQL involves the following steps:

### 1. Input Natural Language

TQL's journey begins with your simple request. Users provide queries in plain, everyday language. TQL is ready to interpret these queries and transform them into structured SQL commands.

![image](https://github.com/jasmeeetSingh/TQL/assets/71340782/974d0005-e7df-4900-985b-f1c10b1ff524)

We have given the user the option to upload a custom Excel file with the schema in the format below, where we are only concerned about the DDL and need no access to data to perform our TQL magic. 

![image](https://github.com/jasmeeetSingh/TQL/assets/71340782/f7cd90f0-80e5-40b9-a260-dcaf5164bafc)


Additionally, the user can select which schemas they have access to so they can manually select which schema they want to run queries. 

![image](https://github.com/jasmeeetSingh/TQL/assets/71340782/5a797f59-0558-42ba-b48b-183715195066)


### 2. Database Schema Integration

TQL is more than a language translator; it's a database expert. It understands the intricate structure and relationships within the database schema, ensuring data integrity and consistency.

### 3. SQL Query Generation

With all the pieces in place, TQL generates a tailored SQL query that aligns perfectly with your natural language request. This process guarantees accurate and reliable results.

![image](https://github.com/jasmeeetSingh/TQL/assets/71340782/eeaa36e9-b8a5-457e-b716-185da0483b56)


### 4. TQL Error Handling

Sometimes, the road to answers can be a bit bumpy. If TQL detects that your input text doesn't relate to any database or schema, it will kindly ask for valid input text to ensure a successful query.

![image](https://github.com/jasmeeetSingh/TQL/assets/71340782/5c1bf95b-cc1c-40be-9cd5-80a65b29a534)

### Architechure

![image](https://github.com/jasmeeetSingh/TQL/assets/71340782/8a717b22-a0f3-465a-843c-31e002869a49)


![image](https://github.com/jasmeeetSingh/TQL/assets/71340782/92d40119-14bf-4aa1-a9f3-e904e5a2e1ab)


#### High-Level Flow Summarized

![image](https://github.com/jasmeeetSingh/TQL/assets/71340782/dd432223-96d2-454a-88d4-c576d066c7a7)

<img width="720" alt="image" src="https://github.com/jasmeeetSingh/TQL/assets/58945986/e20d8e5f-d95d-455e-858f-2ca39f3cd3f3">

## The Models Behind TQL

TQL relies on two separate workflows to perform its magic. These include:

- **Mapping Logic**: To understand the structure and relationships within the data.
- **SQL Generation**: To generate accurate SQL queries tailored to the input text.

## The Models tested when building TQL

We tested the TQL logic on quite a few models, some of these include: 

- **T5**
- **T5- For code generation**
- **Llama2**
- **SQL Coder**

## Results

![image](https://github.com/jasmeeetSingh/TQL/assets/71340782/54e359a4-2269-45f5-b117-399aaf0383ba)


## The Road Ahead

As we look to the future, TQL is far from reaching its final destination. There's a lot more to explore and improve, such as:

![image](https://github.com/jasmeeetSingh/TQL/assets/71340782/506aa871-f12b-432d-b307-ebfb9bc9fd31)


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
