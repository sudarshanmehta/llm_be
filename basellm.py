# -*- coding: utf-8 -*-
"""BaseLLM.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1sKG7sS0NTUilUUf_Zy7ipbX2KtadI5bL
"""

!pip install pymongo

import os
import sys
import pymongo

class BaseLLM(object):

    model: str

    #For future use cases

    # roles: List[str]

    # messages: List[List[str]]

    # max_tokens: int

    # args: str

    def __init__(self, dataset_id, model_id):

        try:
            self.model = model_id
        except:
            pass

        try:
            self.dataset_id = dataset_id
        except:
            pass



    def init(self, Prompt):
        # Pass in Prompt object and run model with prompt
        return

    #For future use cases

    # def get_content(self, response):
    #     # Implementer needs to write interface for this
    #     return

    # def get_content(self, response):
    #     # Implementer needs to write interface for this
    #     return


    def is_code(self, response):
        import re
        regex_pattern = r"```(?:[a-zA-Z]+)?(?:[a-zA-Z]+\n)?([^`]+)(?:```)?"
        matches = re.findall(regex_pattern, response)
        if matches:
            return True
        else:
            return False