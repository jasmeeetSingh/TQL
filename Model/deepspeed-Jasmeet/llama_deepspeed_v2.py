import pandas as pd
from dataclasses import dataclass, field
from typing import cast, Optional

import torch
from datasets import load_dataset
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    Trainer,
    DataCollatorForLanguageModeling,
    TrainingArguments,
    HfArgumentParser,
)
from peft import LoraConfig, get_peft_model
import sys
sys.path.append('/home/jupyter/TQL/')
from utils.token import hub_token


model_id = "defog/sqlcoder-7b"
dataset_name="jasmeeetsingh/sql-spider-kaggledbqa-with-context"
sample=None
train_size=0.85
lora_r=2
lora_alpha=32
lora_dropout = 0.10
seed=42

def format_example(example):
    instruction = (
        "Generate an accurate SQL query to answer the following question using only the given tables: "
    )
    q_header = "### Question"
    a_header = "### Answer"

    q = example["input"]
    a = example["SQL"]

    example[
        "text"
    ] = f"{instruction}\n\n{q_header}\n{q}\n\n{a_header}\n{a}"

    return example


def prepare_dataset(dataset, formatter_func, tokenizer, sample, seed=None):
    # formatting each sample
    dataset_prepared = dataset.map(
        formatter_func, remove_columns=list(dataset.features)
    )
    
    if sample:
        dataset_prepared = (
            dataset_prepared.shuffle(seed=seed).flatten_indices().select(range(sample))
        )

    # apply tokenizer
    dataset_prepared = dataset_prepared.map(
        lambda sample: tokenizer(sample["text"]),
        remove_columns=list(dataset_prepared.features),
    )

    return dataset_prepared


def main():

    train_args = TrainingArguments(
        output_dir="/home/jupyter/New_Model",
        optim="adamw_torch",
        per_device_train_batch_size=2,
        remove_unused_columns=False,
        learning_rate=0.0001,
        gradient_checkpointing=True,
        gradient_accumulation_steps=1,
        fp16=True,
        lr_scheduler_type="constant_with_warmup",
        warmup_steps=5,
        save_steps=1000,
        save_strategy="steps",
        save_total_limit=3,
        logging_steps=1000,
        hub_model_id="jasmeeetsingh/TQL_2",
        hub_strategy="checkpoint",
        hub_private_repo=False,
        push_to_hub=True,
        deepspeed="/home/jupyter/TQL/Model/deepspeed/ds_config_zero3.json",
        num_train_epochs = 10,
        hub_token = hub_token
)


    # loading the tokenizerdataset
    tokenizer = AutoTokenizer.from_pretrained(model_id, token = hub_token)
    tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "right"

    # loading and prepare dataset
    dataset = load_dataset(dataset_name, split="train")
    dataset = prepare_dataset(
        dataset=dataset,
        formatter_func=format_example,
        sample=sample,
        tokenizer=tokenizer,
        seed=seed,
    )

    # preparing data collator
    collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)

    # preparing lora configuration
    peft_config = LoraConfig(
        r=lora_r,
        lora_alpha=lora_alpha,
        lora_dropout=lora_dropout,
        bias="none",
        task_type="CASUAL_LM",
        target_modules = ["q_proj", "k_proj", "v_proj"]
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
    model.config.use_cache = False

    # creating trainer
    trainer = Trainer(
        model=model, args=train_args, train_dataset=dataset, data_collator=collator
    )
    # trainer.accelerator.print(f"{trainer.model}")
    trainer.model.print_trainable_parameters()

    # start training
    trainer.train()

    # save model on main process
    trainer.accelerator.wait_for_everyone()
    state_dict = trainer.accelerator.get_state_dict(trainer.deepspeed)
    unwrapped_model = trainer.accelerator.unwrap_model(trainer.deepspeed)
    if trainer.accelerator.is_main_process:
        unwrapped_model.save_pretrained(train_args.output_dir, state_dict=state_dict)
    trainer.accelerator.wait_for_everyone()

    # save everything else on main process
    if trainer.args.process_index == 0:
        trainer.model.save_pretrained(train_args.output_dir, safe_serialization=True)


if __name__ == "__main__":
    main()
