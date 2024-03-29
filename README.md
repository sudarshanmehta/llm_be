# Open-Source Large Language Model Backend

This is a Python-Flask based backend for developing and training Large Language based models tailored for specific purposes.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [Table Structures](#table-structures)

## Prerequisites

- Python 3.x installed on your system ([Download Python](https://www.python.org/downloads/))
- [Optional] Virtual environment manager like `venv`, `virtualenv`, `pipenv`, or `poetry` for managing dependencies

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/sudarshanmehta/llm_be.git
   ```

2. Navigate to the project directory:
   ```bash
   cd llm_be
   ```

3. [Optional] Set up a virtual environment:
   ```bash
   # Using venv (Python 3.x)
   python3 -m venv venv
   # Activate the virtual environment
   source venv/bin/activate
   ```

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Run the application:
   ```bash
   python app.py
   ```

2. Access the API endpoints:
   - Open your web browser or use tools like Postman to access the endpoints.
   - Available endpoints:
     - `GET /tasks`: Get a list of tasks.
     - `GET /datasets`: Get a list of available dataset for a given classification.
     - `GET /models`: Get a list of models for a given classification.
     - `GET /hyperparameters`: Get a list of hyperparameters for a given model.
     - `POST /train_model`: Starts training of selected model with input as model_id, dataset-id and hyperparameter (array).

## Table Structures

### Tasks Table

| Column       | Type    | Description             |
|--------------|---------|-------------------------|
| id           | Integer | Primary key             |
| task_id      | String  | Task ID                 |
| task         | String  | Task description        |
| description  | String  | Task description        |


### Datasets Table

| Column Name | Data Type | Description                              |
|-------------|-----------|------------------------------------------|
| id          | Integer   | Primary key, auto-incrementing           |
| task_id     | String    | Unique identifier for the task           |
| dataset_name| String    | Name of the dataset                      |


### Hyperparameters Table Structure

The `Hyperparameters` table stores hyperparameters for different models.

| Column Name  | Data Type | Description                                      |
|--------------|-----------|--------------------------------------------------|
| id           | INTEGER   | Primary key, auto-incremented                    |
| model_id     | TEXT      | Model identifier                                 |
| hyper_param  | TEXT      | Hyperparameter name                              |
| hyper_value  | TEXT      | Value of the corresponding hyperparameter        |

Example entry:

| id | model_id            | hyper_param      | hyper_value |
|----|---------------------|------------------|-------------|
| 1  | standard            | MAX_LEN          | 256         |
| 2  | standard            | TRAIN_BATCH_SIZE | 32          |
| 3  | standard            | VALID_BATCH_SIZE | 32          |
| 4  | standard            | EPOCHS           | 2           |
| 5  | standard            | LEARNING_RATE    | 1e-05       |
| 6  | distilbert-base...  | TRAIN_BATCH_SIZE | 32          |
| 7  | distilbert-base...  | VALID_BATCH_SIZE | 32          |
| 8  | distilbert-base...  | EPOCHS           | 2           |
| 9  | distilbert-base...  | LEARNING_RATE    | 1e-05       |
| 10 | flan-t5-small       | LEARNING_RATE    | 5e-5        |
| 11 | flan-t5-small       | EPOCHS           | 5           |
| 12 | flan-t5-small       | TRAIN_BATCH_SIZE | 8           |
| 13 | flan-t5-small       | VALID_BATCH_SIZE | 8           |


### Models Table README File Format

| Column Name | Data Type | Description                                      |
|-------------|-----------|--------------------------------------------------|
| id          | INTEGER   | Primary key, auto-incremented                    |
| task_id     | INTEGER   | ID of the associated task from tasks table       |
| model_id    | TEXT      | Identifier for the model                         |
| memory      | DOUBLE    | Size of the model in memory (in bytes)           |
| hits        | DOUBLE    | Number of hits/downloads for the model           |
