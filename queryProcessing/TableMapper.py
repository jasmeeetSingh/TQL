import re

import nltk
nltk.download('stopwords', quiet=True)
nltk.download('punkt', quiet=True)
from nltk.corpus import wordnet
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer, PorterStemmer
from fuzzywuzzy import fuzz


import pandas as pd

class TableMapper():
    
    def __init__(self, query, schema):
        self.query = query
        self.schema = schema
        self.stemmer = PorterStemmer()

        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))
        self.stop_words.add('number')
      
    
    def get_filtered_schema(self, schema_id):
        '''
        Returns the filtered schema and query df for a given schema_id
        EX: get all queries and table details for 'college_2'
        '''
        s = self.schema[self.schema.schema_id == schema_id].reset_index(drop = True)
        t = self.query[self.query.db_id == schema_id].reset_index(drop = True)
        
        return s, t
    
    def get_wordnet_pos(self, treebank_tag):
        '''
        Map treebank part-of-speech tags to WordNet part-of-speech tags
        '''
        if treebank_tag.startswith('J'):
            return wordnet.ADJ
        elif treebank_tag.startswith('V'):
            return wordnet.VERB
        elif treebank_tag.startswith('N'):
            return wordnet.NOUN
        elif treebank_tag.startswith('R'):
            return wordnet.ADV
        else:
            return wordnet.NOUN  # Default to noun
    
    def remove_stopwords(self, sentence):    
        '''
        Remove all stopwords from a TQL query
        '''
        words = word_tokenize(sentence)
        pos_tags = nltk.pos_tag(words)
        lemmatized_words = [self.lemmatizer.lemmatize(word, self.get_wordnet_pos(pos)) for word, pos in pos_tags 
                            if not word.lower() and len(word) > 3 in self.stop_words]
        
        filtered_sentence = [self.stemmer.stem(w) for w in words if not w.lower() and len(w) > 3 in self.stop_words]
        filtered_sentence = ' '.join(filtered_sentence)
        return list(set((re.sub('[^a-zA-Z ]', '', filtered_sentence.lower()) + ' ' +\
                re.sub("[^a-zA-Z ]", '', ' '.join(lemmatized_words)).lower()).split()))
    
    
    def get_column_list_from_row(self, filtered_schema_row):
        '''
        Get all column names in a schema row
        Appends table name in the column_list as well
        '''
        table_name_in_row_original = filtered_schema_row.table_name_original
        table_name_in_row = filtered_schema_row.table_name_original
        col_list = re.sub('\'', '', filtered_schema_row.column_list[1:-1]).split(', ')
        col_list.append(table_name_in_row)
        col_list.append(table_name_in_row_original)
        
        return col_list
    
    
    def get_scores(self, query, column_list_full):
        
        #Get score based on number of words that are in query and the (colum list + table_name) list
        
        scores = []
        for column_list in column_list_full:
            score = 0
            for word in query:
                for column in column_list:
                    col = self.lemmatizer.lemmatize(column, wordnet.NOUN)
                    if(word.startswith(col) or word.endswith(col)
                       or col.startswith(word) or col.endswith(word)):
                        score += 1    
            if(score > 0):
                scores.append([query, column_list, score])

        scores_df = pd.DataFrame(scores, columns = ['query_words', 'col_list', 'score'])\
                    .sort_values(by = 'score', ascending = False)\
                    .reset_index(drop = True)
        # display(scores_df)
        return scores_df
    
    def get_column_overlap_score(self, scores):
        
        #Second iteration of scores dataframe to reduce the impact of ordering in table.
        #Takes in the scores dataframe and iterates through it and removes the words from query already matched.
        
        final = []
        for column_list, query in zip(scores.col_list.to_list(), scores.query_words.to_list()):
            score_temp = 0
            for word in query[:]:
                for column in column_list[:]:
                    col = self.lemmatizer.lemmatize(column, wordnet.NOUN)
                    if(word.startswith(col) or word.endswith(col)
                       or col.startswith(word) or col.endswith(word)):
                    # if(word in col or col in word):
                        # print(word, column)
                        score_temp += 1
                        query.remove(word)
                        break
                        break

            if(score_temp > 0):
                final.append([column_list, query, score_temp])
                
        # display(pd.DataFrame(final))

        return final 
    
    
    def get_table_names_tql(self, s, query):
        '''
        returns table names extracted from the TQL mapped with the schema details
        '''
        
        stop_words_query = self.remove_stopwords(query)
        
        # for each table gets the column_list for table in filtered schema dataframe
        col_list = s.apply(lambda x : self.get_column_list_from_row(x), axis = 1).to_list()
        
        # get first iteration of scores
        score = self.get_scores(stop_words_query, col_list)
        # second iteration for scores that removes query words afer matching
        over_lap_score = self.get_column_overlap_score(score)

        # Extracting table names from matched column_list
        table_names_mapping = []
        for j in over_lap_score:
            table_names_mapping.append(j[0][-1])
            
        return table_names_mapping
        
    
    def get_exact_match_accuracy(self, s, t, verbosity = 0):
        '''
        Take in the filtered tables of query and schema and returns the percentage of exact match columns
        '''
        count = 0

        # for each query
        for i in range(len(t)):
                
            table_names_mapping = [k.lower() for k in self.get_table_names_tql(s, t.TQL.iloc[i])]

            # Getting actual table names from the SQL query
            sql_tokens = [
                            token for token in re.sub('[^a-zA-Z_ ]', '', t.SQL.iloc[i]).lower().split() \
                            if ((token not in self.stop_words) and len(token) > 2)
                         ]
            actual_list = []
            for token in sql_tokens:
                for table_name in s.table_name_original.values:
                    if(token == table_name.lower()):
                        actual_list.append(token.lower())

            # If we want to check subset, uncomment this if-else 
            # if(not set(actual_list).issubset(set(table_names_mapping))):
            if(list(set(actual_list)) != list(set(table_names_mapping))):
                if(verbosity == 1):
                    print(t.TQL.iloc[i])
                    print(t.SQL.iloc[i])
                    print(self.remove_stopwords(t.TQL.iloc[i]))
                    print('----------------------------------------------------------------------------')
                    print('Actual List', actual_list, '| Predicted List', table_names_mapping, i)
                    print('----------------------------------------------------------------------------')
                
                else:
                    continue
            else:
                count += 1

        return count, len(t)