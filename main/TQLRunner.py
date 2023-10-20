import sys
sys.path.append('../utils/')
sys.path.append('../queryProcessing/')

from utils import *
from TableMapper import TableMapper

from tqdm.notebook import tqdm
tqdm.pandas()

from transformers import T5Tokenizer, T5ForConditionalGeneration
import torch
from torch.utils.data import Dataset, DataLoader
from torch.utils.tensorboard import SummaryWriter

class TQLRunner():
    
    def __init__(self, schema_id):
        
        if(schema_id is None):
            raise Exception("Schema ID is needed")
        
        self.query, self.schema = get_spider_schema_table_files()
        self.tableMapper = TableMapper(self.query, self.schema)
        
        self.s, self.t = self.tableMapper.get_filtered_schema(schema_id)
        
        print('All libraries loaded')
        
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.tokenizer = T5Tokenizer.from_pretrained('t5-small')
        self.model = torch.load('model.pt', map_location=torch.device(self.device))
        
        print('LLM Model initialized')
        
        
    def create_schema_natural_language(self, row):

        schema_id = row['schema_id']
        table_name = row['table_name']
        primary_key = row['primary_key']
        column_list = eval(row['column_list_original'])
        datatype_list = eval(row['column_datatypes'])
        foreign_key = eval(row['foreign_keys'])

        column_list_with_datatype = []
        for column, datatype in zip(column_list, datatype_list):
            column_list_with_datatype.append(\
                     ' has datatype '.join([column, datatype])
            )

        schema_natural_language = \
                f"Given the Table {table_name} having columns as \
                        {', '.join(column_list_with_datatype)} \
                            which has {primary_key}"
        return schema_natural_language
    
    
    def get_table_prompt(self, input_text):
        
        table_names_from_tql = self.tableMapper.get_table_names_tql(self.s, input_text)
        
        if(len(table_names_from_tql) == 0):
            raise Exception("No tables found, please repharse the query and try again")
        
        prompt_tables = []
        for i in table_names_from_tql:
            prompt_tables.append(
                self.s[self.s['table_name_original'] == i].apply(
                    self.create_schema_natural_language, axis = 1
                ).reset_index(drop = True).iloc[0]
            )
                
        return ' and '.join(prompt_tables)
    
    
    def get_final_prompt(self, input_text):
        
        task_prefix = 'Generate an SQL Query for'
        table_prompt = self.get_table_prompt(input_text)
        
        final_prompt = task_prefix + ' ' + input_text + ' ' + table_prompt
        
        return final_prompt
        
        
    def get_SQL_query(self, input_text):
        
        prompt = self.get_final_prompt(input_text)
        
        tokens = self.tokenizer(prompt, 
                           return_tensors="pt", max_length=512, 
                           truncation=True, padding="max_length")
        
        outputs = self.model.generate(input_ids=tokens.input_ids.to(self.device), max_new_tokens = 512)
        predicted_query = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        return predicted_query