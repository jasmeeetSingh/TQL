import pandas as pd

def get_spider_schema_table_files():
    
    spider_query = pd.read_csv("gs://data_tql/spider/processed/spiderQueryData.csv")
    spider_schema = pd.read_csv("gs://data_tql/spider/processed/Schemas/tablesSchemaSpider.csv")
    
    return spider_query, spider_schema