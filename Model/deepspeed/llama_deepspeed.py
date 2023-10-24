from typing import Dict
from sklearn.model_selection import train_test_split

from dataclasses import dataclass, field
from typing import cast, Optional

import torch
from datasets import load_dataset
from torch.utils.data import Dataset
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    Trainer,
    DataCollatorForLanguageModeling,
    TrainingArguments,
    HfArgumentParser,
    PreTrainedTokenizer
)
from transformers.trainer_pt_utils import LabelSmoother
from transformers.integrations import deepspeed

from peft import LoraConfig, get_peft_model

import os
IGNORE_TOKEN_ID = LabelSmoother.ignore_index
import pandas as pd

queryData = pd.read_csv('gs://data_tql/spider/processed/spiderQueryData.csv')
tableData = pd.read_csv('gs://data_tql/spider/processed/Schemas/tablesSchemaSpider.csv')

def format_examples(question, answer):
    """
    Formats a record of training data into the below format.

    ```
    <instruction>

    ### Question:
    <question>

    ### Answer:
    <answer>
    ```
    """
    formatted = []

    instruction = (
        "Given the question with the data dictionary, answer the question by writing the appropriate SQL code."
    )
    q_header = "### Question:"
    a_header = "### Answer:"

    q = question
    a = answer

    text = f"{instruction}\n\n{q_header}\n{q}\n\\n\n{a_header}\n{a}"

    return text

def create_schema_natural_language(row):

    schema_id = row['schema_id']
    table_name = row['table_name']
    primary_key = row['primary_key']
    column_list = eval(row['column_list_original'])
    datatype_list = eval(row['column_datatypes'])
    foreign_key = eval(row['foreign_keys'])

    column_list_with_datatype = []
    for column, datatype in zip(column_list, datatype_list):
        column_list_with_datatype.append(' has datatype '.join([column, datatype]))

    schema_natural_language = f"Given the Table {table_name} having columns as {', '.join(column_list_with_datatype)} which has {primary_key}"
    return schema_natural_language

tableData['schema_natural_language'] = tableData.apply(create_schema_natural_language, axis = 1)
tableData.head(3)

all_schemas = tableData['schema_id'].unique()
schema_table_query = {}
for schema in all_schemas:
    schema_details = ' and '.join(tableData[tableData['schema_id'] == schema]['schema_natural_language'].values)
    schema_table_query[schema] = schema_details

queryData['schema_natural_language'] = queryData['db_id'].map(schema_table_query)
queryData['final_TQL'] = queryData['TQL'] + ' ' + queryData['schema_natural_language']

model_id = "meta-llama/Llama-2-7b-hf"

tokenizer = AutoTokenizer.from_pretrained(
    model_id,
    model_max_length=4096,
    padding_side="right",
    use_fast=False,
    token = hub_token
)
tokenizer.pad_token = tokenizer.unk_token

# Define a custom dataset for training
class SQLDataset(Dataset):
    def __init__(self, input_texts, target_queries, tokenizer):
        self.input_texts = input_texts
        self.target_queries = target_queries
        self.tokenizer = tokenizer

    def __len__(self):
        return len(self.input_texts)

    def __getitem__(self, index):
        
        input_text = self.input_texts[index]
        target_query = self.target_queries[index]
                
        input_text = format_examples(input_text, target_query)

        input_encoding = self.tokenizer([input_text], return_tensors="pt", max_length=512, truncation=True, padding="max_length")
        target_encoding = self.tokenizer([target_query], return_tensors="pt", max_length=512, truncation=True, padding="max_length")
        
        return {
            'input_ids': input_encoding.input_ids.squeeze(0),
            'attention_mask': input_encoding.attention_mask.squeeze(0),
            'labels': target_encoding.input_ids.squeeze(0),
        }
    
# Load the labeled dataset
input_texts = queryData['final_TQL'].values # List of input texts
target_queries = queryData['SQL'].values  # List of corresponding target SQL queries

# Split the dataset into train and validation sets
train_input_texts, val_input_texts, train_target_queries, val_target_queries = train_test_split(input_texts, target_queries, test_size=0.2, random_state=42)

# Create instances of the custom dataset
train_dataset = SQLDataset(train_input_texts, train_target_queries, tokenizer)
val_dataset = SQLDataset(val_input_texts, val_target_queries, tokenizer)


data_module = dict(train_dataset=train_dataset, eval_dataset=val_dataset)

train_args = TrainingArguments(
    output_dir="/home/jupyter/Model",
    optim="adamw_torch",
    per_device_train_batch_size=1,
    remove_unused_columns=False,
    learning_rate=1e-5,
    gradient_checkpointing=True,
    gradient_accumulation_steps=1,
    fp16=True,
    lr_scheduler_type="constant_with_warmup",
    warmup_steps=5,
    save_steps=50,
    save_strategy="steps",
    save_total_limit=3,
    logging_steps=10,
    hub_model_id="kargil8320/TQL",
    hub_strategy="checkpoint",
    hub_private_repo=True,
    push_to_hub=True,
    deepspeed="/home/jupyter/ds_config_zero3.json",
    num_train_epochs = 3,
    hub_token = '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'
)

lora_r = 8
lora_alpha = 16
lora_dropout = 0.1
target_modules=["q_proj", "k_proj", "v_proj", "out_proj", "fc_in", "fc_out", "wte"]


# preparing lora configuration
peft_config = LoraConfig(
    r=lora_r,
    lora_alpha=lora_alpha,
    lora_dropout=lora_dropout,
    bias="none",
    task_type="CASUAL_LM",
    target_modules=target_modules,
)

# loading the base model
model = AutoModelForCausalLM.from_pretrained(
    model_id, use_cache=not train_args.gradient_checkpointing,
    token = hub_token
)
if train_args.gradient_checkpointing:
    model.gradient_checkpointing_enable()

# getting peft model
model = get_peft_model(model, peft_config)
model.print_trainable_parameters()

# creating trainer
trainer = Trainer(
    model=model, tokenizer=tokenizer, args=train_args, **data_module
)
model.config.use_cache = False

# trainer.accelerator.print(f"{trainer.model}")
trainer.model.print_trainable_parameters()

trainer.train()