#!/bin/bash

cat $1 | jq -c '{"word":.word, "pos":.pos, "senses": .senses}' | sed '$!s/$/,/' | sed '1 i\{"words": [' > eng_dict.jsonl
echo ']}' >> eng_dict.jsonl


