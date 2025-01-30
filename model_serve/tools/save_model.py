import torch
from transformers import AutoTokenizer, AutoModel
from safetensors.torch import save_model

model_id = "sentence-transformers/msmarco-distilbert-base-v3"

tokenizer = AutoTokenizer.from_pretrained(model_id)

model = AutoModel.from_pretrained(model_id)

tokenizer.save_pretrained('./sentence_tokenizer', safe_serialization=False)

model.save_pretrained('./sentence_model', safe_serialization=False)