import re
import pandas as pd
import torch
from transformers import AutoModel, AutoTokenizer
from tqdm import tqdm
from fuzzywuzzy import fuzz
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer

nltk.download('stopwords')
nltk.download('punkt')

class TableMapperBERT:
    def __init__(self, query, schema):
        self.query = query
        self.schema = schema
        self.stemmer = PorterStemmer()
        self.stop_words = set(stopwords.words('english'))
        self.stop_words.add('number')
        self.tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
        self.model = AutoModel.from_pretrained("bert-base-uncased")
        self.model.eval()

    def remove_stopwords(self, sentence):
        word_tokens = word_tokenize(sentence)
        filtered_sentence = [self.stemmer.stem(w) for w in word_tokens if not w.lower() in self.stop_words]
        filtered_sentence = ' '.join(filtered_sentence)
        return re.sub('[^a-zA-Z ]', '', filtered_sentence.lower()).split()

    def get_filtered_schema(self, schema_id):
        s = self.schema[self.schema['schema_id'] == schema_id].reset_index(drop=True)
        t = self.query[self.query['db_id'] == schema_id].reset_index(drop=True)
        return s, t
    
    def get_bert_embeddings(self, text):
        inputs = self.tokenizer(text, return_tensors="pt", padding=True, truncation=True)
        with torch.no_grad():
            outputs = self.model(**inputs)
        embeddings = outputs.last_hidden_state.mean(dim=1).squeeze()
        return embeddings

    def get_scores_with_bert(self, query, column_list_full):
        scores = []
        query_embeddings = self.get_bert_embeddings(" ".join(query))
        
        for column_list in column_list_full:
            score = 0
            for word in query:
                word_embeddings = self.get_bert_embeddings(word)
                similarity = torch.cosine_similarity(query_embeddings, word_embeddings, dim=0)
                if similarity > 0.65:
                    score += 1
            if score > 0:
                scores.append([query, column_list, score])

        scores_df = pd.DataFrame(scores, columns=['query_words', 'col_list', 'score']) \
            .sort_values(by='score', ascending=False) \
            .reset_index(drop=True)
        return scores_df

    def get_column_overlap_score(self, scores):
        final = []
        for column_list, query in zip(scores.col_list.to_list(), scores.query_words.to_list()):
            score_temp = 0
            for word in query[:]:
                for column in column_list[:]:
                    col = self.stemmer.stem(column)
                    if word.startswith(col) or word.endswith(col) \
                            or col.startswith(word) or col.endswith(word):
                        score_temp += 1
                        query.remove(word)
                        break
            if score_temp > 0:
                final.append([column_list, query, score_temp])
        return final

    def get_table_names_tql(self, s, query):
        stop_words_query = self.remove_stopwords(query)
        col_list = s.apply(lambda x: self.get_column_list_from_row(x), axis=1).to_list()
        score = self.get_scores_with_bert(stop_words_query, col_list)
        over_lap_score = self.get_column_overlap_score(score)
        table_names_mapping = []
        for j in over_lap_score:
            table_names_mapping.append(j[0][-1])
        return table_names_mapping

    def get_column_list_from_row(self, filtered_schema_row):
        table_name_in_row_original = filtered_schema_row.table_name_original
        table_name_in_row = filtered_schema_row.table_name_original
        col_list = re.sub('\'', '', filtered_schema_row.column_list[1:-1]).split(', ')
        col_list.append(table_name_in_row)
        col_list.append(table_name_in_row_original)
        return col_list

    def get_exact_match_accuracy(self, s, t, verbosity=0):
        count = 0
        for i in range(len(t)):
            table_names_mapping = [k.lower() for k in self.get_table_names_tql(s, t.TQL.iloc[i])]
            sql_tokens = [token for token in re.sub('[^a-zA-Z_ ]', '', t.SQL.iloc[i]).lower().split()
                          if ((token not in self.stop_words) and len(token) > 2)]
            actual_list = []
            for token in sql_tokens:
                for table_name in s.table_name_original.values:
                    if token == table_name.lower():
                        actual_list.append(token.lower())
            if list(set(actual_list)) != list(set(table_names_mapping)):
                if verbosity == 1:
                    print(t.TQL.iloc[i])
                    print(t.SQL.iloc[i])
                    print(self.remove_stopwords(t.TQL.iloc[i]))
                    print('----------------------------------------------------------------------------')
                    print('Actual List', actual_list, '| Predicted List', table_names_mapping, i)
                    print('----------------------------------------------------------------------------')
            else:
                count += 1
        return count, len(t)