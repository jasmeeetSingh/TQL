import os

import sqlalchemy, pymysql
from sqlalchemy import inspect


class DatabaseUtils():
       
    def __init__(self):
        pass
       
    def connect_to_db(self):
        
        db_host = '35.193.112.203' 
        db_user = 'root' 
        db_pass = 'helloworld123' 
        db_name = 'mysql' 
        db_port = 0 

        pool = sqlalchemy.create_engine(
            sqlalchemy.engine.url.URL.create(
                drivername="mysql+pymysql",
                username=db_user,
                password=db_pass,
                host=db_host,
                port=db_port,
                database=db_name,
            ),
        )
        return pool
        
    def connect_to_engine(self, engine):
        return engine.connect()
    
    def inspect_pool(self, engine):
        return inspect(engine)
    
    def get_connection(self):
        connection = self.connect_to_db()
        engine = self.connect_to_engine(connection)
        inspection = self.inspect_pool(engine)
        return engine, inspection
        
    def get_schema_names(self):
        
        engine, inspection = self.get_connection()
        schema_names = inspection.get_schema_names()
        engine.close()
        
        return schema_names                             
    
    def create_schema(self, schema_name):
               
        engine, inspection = self.get_connection()
        
        if (schema_name not in inspection.get_schema_names()):
            engine.execute(sqlalchemy.schema.CreateSchema(schema_name))
            engine.commit()         
        else:
            raise Exception(f"Schema name {schema_name} already exists.")
            
        engine.close()
            
    def drop_schema(self, schema_name):
        
        engine, inspection = self.get_connection()
        
        if (schema_name in inspection.get_schema_names()):
            engine.execute(sqlalchemy.schema.DropSchema(schema_name))
            engine.commit()
        else:
            raise Exception(f"Schema name {schema_name} does not exist.")
            
        engine.close()
         
    def execute_query(self, query):
        
        engine, inspection = self.get_connection()
        
        if('select' in query.lower()):
            result = engine.execute(sqlalchemy.text(query))
            engine.close()
            return result
        else:
            engine.execute(sqlalchemy.text(query))
            engine.commit()
            engine.close()
            return None
     