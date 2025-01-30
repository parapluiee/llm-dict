Performs semantic search using a BERT Sentence Encoder and Postgres + PgVector to encode semantic meaning of wiktionary word senses,then finding the closest English word to user defined definitions.

Basic implementation of an LLM webapp, locally hosting the Postgres database and a Django backend, with the website communicating a local TorchServe instance of the model. 

Improvement: 
- Better sentence embedding model, as this model was not pretrained for this task
  - Contrastive Learning
 

I have the data but not the processing power to perform this task on non-english langauges. This would be much more interesting, allowing users to search for words in other languages that express nuanced ideas not expressed via a single word in english, i.e "untranslatable" words in other languages. 


https://huggingface.co/sentence-transformers/msmarco-distilbert-base-v3
https://kaikki.org/
https://github.com/tatuylonen/wiktextract
