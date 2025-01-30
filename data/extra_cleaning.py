import json

#In general, much slower than jq but invalid words are more complicated


#key  : json tag
#list : if any of these items are in a sense, remove that sense
exceptions = {
    "tags" : ["form-of", "abbreviation", "alt-of", "morpheme"],
    "pos"  : ["symbol"]
}
#bad data
#tags: formof, abbreviation, alt-of, morpheme
#pos: symbol


words = list()
total_lines = 0
#remove all senses which are disallowed
#if a word has no senses, remove from words
with open("/kaikki.org-dictionary-English.jsonl", 'r') as f:
    #to see how many are removed
    for line in f:
        total_lines+=1
        #full word json
        word = json.loads(line)
        
        #list of valid senses
        new_senses = list()
        for sense in word["senses"]:
            if sense == None:
                continue
            #probably not a good method
            good_sense = True
            for exception in exceptions:
                #if this sense has this json tag
                #fact some senses do not have a "tag" feature means it is impossible (or difficult) to do this with list comprehension
                #also true of None type senses
                if (exception in sense):
                    for violation in exceptions[exception]:
                        if violation in sense[exception]:
                            good_sense=False
            
            if "glosses" in sense and good_sense:
                #turn "sense" json into only it's glosses, i.e no tags
                for gloss in sense["glosses"]:
                    new_senses.append(gloss)
        if (new_senses):
            #replace senses with valid ones
            word["senses"] = new_senses
            #add to output, trimming all fat
            words.append({"word" : word["word"], "pos" : word["pos"], "senses" : new_senses})            
with open('eng_dict_extraclean.jsonl', 'w') as f:
    json.dump({"words" : words}, f)

print(total_lines)
print(len(words))
