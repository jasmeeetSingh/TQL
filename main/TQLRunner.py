import sys
import os
sys.path.append('../utils/')
sys.path.append('../queryProcessing/')
sys.path.append('/home/jupyter/TQL/')

from utils import *
from TableMapper import TableMapper

import pandas as pd
import numpy as np
from tqdm.notebook import tqdm
tqdm.pandas()

import torch
from torch.utils.data import Dataset, DataLoader
from torch.utils.tensorboard import SummaryWriter
from typing import Dict
from sklearn.model_selection import train_test_split
from dataclasses import dataclass, field
from typing import cast, Optional
from datasets import load_dataset
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    pipeline
)
from transformers.trainer_pt_utils import LabelSmoother
from peft import PeftConfig, PeftModel

IGNORE_TOKEN_ID = LabelSmoother.ignore_index
from token import *


class TQLRunner():
    
    def __init__(self, schema_id):
        
        if(schema_id is None):
            raise Exception("Schema ID is needed")
        
        self.query, self.schema = get_spider_schema_table_files()
        self.tableMapper = TableMapper(self.query, self.schema)
        
        self.s, self.t = self.tableMapper.get_filtered_schema(schema_id)
        
        print('All libraries loaded')
        
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model, self.tokenizer, self.base_model = \
                self.load_model(
                    'naman1011/TQL', 
                    torch.cuda.device_count(), 
                    max_gpu_memory=None
                )
        self.tokenizer.pad_token = self.tokenizer.eos_token
        self.tokenizer.padding_side = "right"
            
        print('LLM Model initialized')
        
        
    def format_example(self, example):
        instruction = (
            "Given the context, answer the question by writing the appropriate SQL code."
        )
        q_header = "### Question"
        a_header = "### Answer"

        q = example

        return f"{instruction}\n\n{q_header}\n{q}\n\n{a_header}\n"

    def get_gpu_memory(self, max_gpus=None):
        """Get available memory for each GPU."""
        import torch
        gpu_memory = []
        num_gpus = (
            torch.cuda.device_count()
            if max_gpus is None
            else min(max_gpus, torch.cuda.device_count())
        )
        for gpu_id in range(num_gpus):
            with torch.cuda.device(gpu_id):
                device = torch.cuda.current_device()
                gpu_properties = torch.cuda.get_device_properties(device)
                total_memory = gpu_properties.total_memory / (1024**3)
                allocated_memory = torch.cuda.memory_allocated() / (1024**3)
                available_memory = total_memory - allocated_memory
                gpu_memory.append(available_memory)
        return gpu_memory

    def load_model(self, model_path, num_gpus, max_gpu_memory=None):

        kwargs = {"torch_dtype": torch.float16}
        kwargs["device_map"] = "auto"
        if max_gpu_memory is None:
            kwargs[
                "device_map"
            ] = "sequential"  # This is important for not the same VRAM sizes
            available_gpu_memory = self.get_gpu_memory(num_gpus)
            kwargs["max_memory"] = {
                i: str(int(available_gpu_memory[i] * 0.85)) + "GiB"
                for i in range(num_gpus)
            }
        else:
            kwargs["max_memory"] = {i: max_gpu_memory for i in range(num_gpus)}

        config = PeftConfig.from_pretrained(model_path)
        base_model_path = config.base_model_name_or_path
        tokenizer = AutoTokenizer.from_pretrained(
            base_model_path, use_fast=False
        )
        base_model = AutoModelForCausalLM.from_pretrained(
            base_model_path,
            low_cpu_mem_usage=True,
            **kwargs,
        )
        model = PeftModel.from_pretrained(base_model, model_path)

        return model, tokenizer, base_model
        
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
        
        final_prompt = input_text + ' ' + table_prompt
        # print(final_prompt)
        
        return self.format_example(final_prompt)
        
        
    def get_SQL_query(self, input_text):
        
        prompt = self.get_final_prompt(input_text)
        pipe = pipeline(task="text-generation", model=self.model, tokenizer=self.tokenizer)
        result = pipe(f"<s>[INST] {prompt} [/INST]")
        
        return (result[0]['generated_text'].split('[/INST]')[-1].split(';')[0].strip())