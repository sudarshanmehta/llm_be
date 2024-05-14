# -*- coding: utf-8 -*-
"""Untitled3.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1w_DBapNHQcaxQzwp843xLZF1oDv17a2F
"""

import numpy as np
import pandas as pd
import evaluate
from datasets import load_dataset

# from utilities import *
from transformers import AutoTokenizer
from transformers import AutoModelForCausalLM, AutoModelForSequenceClassification
from transformers import Trainer, TrainingArguments
from huggingface_hub import HfFolder

class Bert:
  def __init__(self, dataset_id, model_id, hyperparametes):
    self.dataset_id = 'yelp_review_full'
    self.model_id = model_id
    self.dataset = None
    self.tokenizer = None
    self.model = None
    self.training_args = hyperparametes
    self.trainer = None
    self.summarizer = None
    self.metric = None
    self.tokenized_dataset = None
    self.tokenized_inputs = None
    self.initialize()
    self.train_model()

  def initialize(self):
    # Load dataset from the hub
    self.dataset = load_dataset(self.dataset_id)

    # Load tokenizer of Bert
    self.tokenizer = AutoTokenizer.from_pretrained(self.model_id)

    def tokenize(data):
      self.tokenizer.truncation_side = "right"
      self.tokenized_inputs = self.tokenizer(
          data['text'],
          return_tensors="np",
          truncation=True,
          padding='max_length')
      return self.tokenized_inputs

    raw_dataset =  self.dataset.rename_column("label", "labels") # to match Trainer
    print(raw_dataset)
    self.tokenized_dataset = raw_dataset.map(tokenize, batched = True, remove_columns = ["text"])

    labels = self.tokenized_dataset["train"].features["labels"].names
    num_labels = len(labels)
    label2id, id2label = dict(), dict()
    for i, label in enumerate(labels):
      label2id[label] = str(i)
      id2label[str(i)] = label

    # Download the model from huggingface.co/models
    self.model = AutoModelForSequenceClassification.from_pretrained(
        self.model_id, num_labels=num_labels, label2id=label2id, id2label=id2label
    )

    print(self.model)

  def train_model(self):
    def show_metrics(self):
      # Metric computation
      metric = evaluate.load("f1")
      return self.metric

    def compute_metrics(eval_pred):
      predictions, labels = eval_pred
      predictions = np.argmax(predictions, axis=1)
      return self.metric.compute(predictions=predictions, references=labels, average="weighted")


    try:
      # Additional setup for training
      repository_id = "bert-base-banking77-pt2"
      # Define training args
      training_args = TrainingArguments(
          output_dir=repository_id,
          per_device_train_batch_size=4,
          per_device_eval_batch_size=2,
          learning_rate=5e-5,
          num_train_epochs=3,
          # logging & evaluation strategies
          logging_dir=f"{repository_id}/logs",
          logging_strategy="steps",
          logging_steps=100,
          evaluation_strategy="epoch",
          save_strategy="epoch",
          save_total_limit=2,
          metric_for_best_model="f1",
          # push to hub parameters
          report_to="tensorboard",
          push_to_hub=False,
          hub_strategy="every_save",
          hub_model_id=repository_id,
          hub_token=HfFolder.get_token(),
          )

      # Create Trainer instance
      trainer = Trainer(
          model = self.model,
          args = training_args,
          train_dataset = self.tokenized_dataset["train"],
          eval_dataset = self.tokenized_dataset["test"],
          compute_metrics=compute_metrics,
          )

      # Start training
      trainer.train()

      # You might want to save the trained model or perform other post-training tasks here
    except Exception as e:
      print(f"Error during training: {str(e)}")


    def summarize_sample(self, sample):
      try:
        # Ensure that the summarizer is initialized
        if self.summarizer is None:
          print("Summarizer is not initialized. Please ensure the model is trained.")
          return None

        # Select a random test sample
        # You can use the provided sample instead of selecting a random one
        input_text = sample["dialogue"]

        # Summarize using the initialized summarizer
        summary_result = self.summarizer(input_text)

        # Extract the summary text from the result
        summary_text = summary_result[0]['summary_text']

        return summary_text

      except Exception as e:
        print(f"Error during summarization: {str(e)}")
        return None