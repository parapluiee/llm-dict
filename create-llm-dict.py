import json
import torch
from transformers import AutoTokenizer, AutoModel
import psycopg2
from pgvector.psycopg2 import register_vector



def mean_pooling(model_output, attention_mask):
    token_embeddings = model_output[0] #First element of model_output contains all token embeddings
    input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
    return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)
    
def insert_vectors(word_pos_def_triples, batch_size=8):
    print("Connecting to database")
    db = json.loads(open("db_info.json"))
    table_name = db["table_name"]
    db_name = db["db_name"]
    host = db["host"]
    user = db["user"]
    password = db["password"]
    port = db["port"]

    conn = psycopg2.connect(database=db_name,
                            host = host,
                            user = user,
                            password = password,
                            port = port)
    cursor = conn.cursor()
    cursor.execute('CREATE EXTENSION IF NOT EXISTS vector')
    register_vector(conn)
    print("Connected to database")




    # Initializing a ModernBert style configuration
    print("Loading sentence-transformers-BERT model")
    model_id = "sentence-transformers/msmarco-distilbert-base-v3"
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    model = AutoModel.from_pretrained(model_id)

    print("\nModel Loaded")
    num_triples = len(word_pos_def_triples)
    num_batches = int(num_triples / batch_size) + (not (num_triples%batch_size == 0))
    print("Creating vectors, then sending to databse")
    for i in range(num_batches):
        print("batch: ", i + 1, "\\", num_batches)
        data_start = i*batch_size
        data_end = min(num_triples, (i+1) * batch_size)
        word, pos_s, sentences = zip(*word_pos_def_triples[data_start:data_end])
        inputs = tokenizer(sentences, padding=True, truncation=True, return_tensors="pt")
        with torch.no_grad():

            model_output = model(**inputs)

        embeddings = map(json.dumps, mean_pooling(model_output, inputs['attention_mask']).numpy().tolist())
        args = zip(word, pos_s, embeddings)
        
        cursor.executemany('INSERT INTO ' + table_name + ' (word, pos, embedding) VALUES (%s, %s, %s)', args)
    print("All vectors loaded into databse")
    """
    test_input = tokenizer('To remove.', padding=True, truncation=True, return_tensors="pt")
    with torch.no_grad():
        test_output = model(**test_input)
    test_query = json.dumps(mean_pooling(test_output, test_input['attention_mask']).numpy().tolist()[0])
    cursor.execute('SELECT word FROM words ORDER BY embedding <-> %s LIMIT 5', (test_query,))
    print(cursor.fetchall())
    """
    print("Committing")
    conn.commit()


def load_data(data):
    print("Creating word, pos, sense triples")
    data_triples = list()
    for word in data:
        for sense in word["senses"]:
            #create new entry for each word sense
            #possible to have many "words" for each word, even if they are the same part of speech
            data_triples.append((word["word"], word["pos"], sense))
    print(len(data), " words")
    print(len(data_triples), " senses loaded into memory")
    print("{:.2f} average senses per word".format(len(data_triples) / len(data)))
    insert_vectors(data_triples, batch_size=32)





data_path = "data/eng_dict_extraclean.jsonl"
print("Opening file: ", data_path)
with open(data_path) as f:
    print("Loading json into memory")
    json_file = json.load(f)


#Begin writing to database

#Testing: 
test_data = json_file["words"][0:1000]
dictionary = set(sense["word"] for sense in test_data)

load_data(test_data)
print(dictionary)
print("Done.")
