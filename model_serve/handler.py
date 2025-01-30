# handler.py

import torch
import logging
import transformers
import os
import json

import psycopg2
from pgvector.psycopg2 import register_vector

from ts.torch_handler.base_handler import BaseHandler
from transformers import AutoTokenizer, AutoModel
from safetensors.torch import save_model
logger = logging.getLogger(__name__)
logger.info("Transformers version %s", transformers.__version__)


db_info_path = "/path/to/project/llm-dict/db_info.json"
db = json.loads(open(db_info_path).read())
def mean_pooling(model_output, attention_mask):
    token_embeddings = model_output[0] #First element of model_output contains all token embeddings
    input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
    return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)
    

class ModelHandler(BaseHandler):

    def initialize(self, context):
       

        properties = context.system_properties
        self.manifest = context.manifest
        model_dir = properties.get("model_dir")
        
        # use GPU if available
        self.device = torch.device(
            "cuda:" + str(properties.get("gpu_id"))
            if torch.cuda.is_available() and properties.get("gpu_id") is not None
            else "cpu"
        )
        logger.info(f'Using device {self.device}')

        # load the model
        model_file = self.manifest['model']['modelFile']
        model_path = os.path.join(model_dir, model_file)
        
        if os.path.isfile(model_path):
            self.model = AutoModel.from_pretrained(model_dir)
            self.model.to(self.device)
            self.model.eval()
            logger.info(f'Successfully loaded model from {model_file}')
        else:
            raise RuntimeError('Missing the model file')
        
        # load tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(model_dir)
        if self.tokenizer is not None:
            logger.info('Successfully loaded tokenizer')
        else:
            raise RuntimeError('Missing tokenizer')

        table_name = db["table_name"]
        self.table_name = table_name
        db_name = db["db_name"]
        host = db["host"]
        user = db["user"]
        password = db["password"]
        port = db["port"]
        self.conn = psycopg2.connect(database=db_name,
                                host = host,
                                user = user,
                                password = password,
                                port = port)
        self.cursor = self.conn.cursor()
        self.cursor.execute('CREATE EXTENSION IF NOT EXISTS vector')
        register_vector(self.conn)
        logger.info("Connected to database")




        self.initialized = True
    
    def preprocess(self, requests):
       
    
        # unpack the data
        data = requests[0]
        if data is None:
            data = requests[0].get('data')
       
        text = str(data.get('input'))
        logger.info(text)
        logger.info(f'Received {len(text)} texts. Begin tokenizing')
    
        # tokenize the texts
        tokenized_data = self.tokenizer(text, 
                                        padding=True, 
                                        truncation=True,
                                        return_tensors='pt')
    
        logger.info('Tokenization process completed')
    
        return tokenized_data
    def inference(self, inputs):
        
        with torch.no_grad():
            model_output = self.model(**inputs.to(self.device))
        out_embedding = mean_pooling(model_output, inputs['attention_mask']).numpy().tolist()
        logger.info('Predictions successfully created.')

        return out_embedding
    def postprocess(self, outputs: list):
    
        #predictions = [self.mapping[str(label)] for label in outputs]
        #logger.info(f'PREDICTED LABELS: {predictions}')
        query = json.dumps(outputs[0])
        out_words = list()

        self.cursor.execute('SELECT id FROM '+ self.table_name + ' ORDER BY embedding <-> %s LIMIT 5', (query,))
        return [self.cursor.fetchall()]
