import sys
sys.path.append('../utils/')
sys.path.append('../queryProcessing/')

from utils import *
from TableMapper import TableMapper

from tqdm.notebook import tqdm
tqdm.pandas()

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
from torch.utils.data import Dataset, DataLoader
from torch.utils.tensorboard import SummaryWriter

class TQLRunner():

    def __init__(self):

        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.tokenizer = AutoTokenizer.from_pretrained("defog/sqlcoder-7b")
        self.model = \
            AutoModelForCausalLM.from_pretrained(
                "defog/sqlcoder-7b", device_map="auto"
            )
        # self.model.to(self.device)

        print('LLM Model initialized')
        
    
    def set_schema(self, schema_id):
        
        if(schema_id is None):
            raise Exception("Schema ID is needed")

        self.query, self.schema = get_spider_schema_table_files()
        self.tableMapper = TableMapper(self.query, self.schema)

        self.s, self.t = self.tableMapper.get_filtered_schema(schema_id)

        print('All libraries loaded')

    def create_schema_natural_language(self, row):

        schema_id = row['schema_id']
        table_name = row['table_name']
        primary_key = row['primary_key']
        column_list = eval(row['column_list_original'])
        datatype_list = eval(row['column_datatypes'])
        foreign_key = eval(row['foreign_keys'])

        column_list_with_datatype = []
        for column, datatype in zip(column_list, datatype_list):
            column_list_with_datatype.append(' '.join([column, datatype]))


        schema_natural_language = f"CREATE TABLE {table_name} ({', '.join(column_list_with_datatype)}) which has {primary_key} as primary key"

        return schema_natural_language

    
    def get_schema_details(self):
        return self.schema


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

        return '\n\n'.join(prompt_tables)


    def get_final_prompt(self, input_text):

        table_prompt = self.get_table_prompt(input_text)
        
        prompt = f"""\
            ### Instructions:
            Your task is convert a question into a SQL query, given a Postgres database schema.\
            Adhere to these rules:
            - **Deliberately go through the question and database schema word by word** to appropriately answer the question
            - **Use Table Aliases** to prevent ambiguity. For example, `SELECT table1.col1, table2.col1 FROM table1 JOIN table2 ON table1.id = table2.id`.
            - When creating a ratio, always cast the numerator as float

            ### Input:
            Generate a SQL query that answers the question '{input_text}`.\n
            This query will run on a database whose schema is represented in this string:

            {table_prompt}

            ### Response:
            Based on your instructions, here is the SQL query I have generated to answer the question `{input_text}`:
            ```sql
        """

        return prompt


    def get_SQL_query(self, input_text):

        prompt = self.get_final_prompt(input_text)
        eos_token_id = self.tokenizer.convert_tokens_to_ids(["```"])[0]
        inputs = self.tokenizer(prompt, return_tensors="pt").to('cuda')
        generated_ids = self.model.generate(
            **inputs,
            num_return_sequences=1,
            eos_token_id=eos_token_id,
            pad_token_id=eos_token_id,
            max_new_tokens=400,
            do_sample=False,
            num_beams=5
        )
        outputs = self.tokenizer.batch_decode(generated_ids, skip_special_tokens=True)
        torch.cuda.empty_cache()
        return outputs[0].split("```sql")[-1].split("```")[0].split(";")[0].strip()