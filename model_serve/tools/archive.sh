#!/bin/bash

torch-model-archiver --model-name BERTSentenceEmbedding --version 1.0 --model-file sentence_model/pytorch_model.bin --handler handler.py --extra-files "sentence_model/config.json,sentence_model/tokenizer"