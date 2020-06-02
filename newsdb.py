import urllib.request, urllib.parse, urllib.error
import requests
import pandas as pd
from pandas.io.json import json_normalize
import pyodbc 
from sqlalchemy import create_engine
import json
class NewsDB:

    def __init__(self):
        '''
        self.engine.execute('CREATE TABLE news ('
                   'author varchar,'
                   'title VARCHAR, '
                   'description varchar,'
                   'url varchar,'
                   'publishedAt varchar,'
                   'content varchar,'
                   'source_name varchar,'
                   'keyword varchar);'
        )
        '''

        self.engine = create_engine('postgresql://ahmed:ahmed@localhost/ahmed')
        return 
    #store in database the articles we have adding to the keyword !
    def store_db(self, keyword, articles_json):
        '''
        self.conn_ = pyodbc.connect()
        cursor = self.conn_.cursor()
        cursor.execute(('INSERT INTO News '
                        '(author, title, description, url, publishedAt, content, source_name, keyword) VALUES {vals}'
                        .format(vals=",".join(["('" + str(i[1]['author']) + "', "
                                                    + str(i[1]['title']) + "', "
                                                    + str(i[1]['description']) + "', "
                                                    + str(i[1]['url']) + "', "
                                                    + str(i[1]['publishedAt']) + "', "
                                                    + str(i[1]['content']) + "', "
                                                    + str(i[1]['source_name']) + "', "
                                                    + str(i[1]['keyword']) + ")"
                                            for i in df.iterrows()]))))
        cursor.commit()
        cursor.close()
        '''        
        
        df_before = pd.read_sql("SELECT * FROM news WHERE keyword='"+str(keyword.lower())+"';", self.engine)
        print(df_before)
        df = json_normalize(articles_json['articles'])
        df['keyword'] = keyword.lower()
        del df['urlToImage']
        del df['source.id']
        df = df.rename(columns={"source.name": "source_name","publishedAt":"publishedat"})
        print(df)

        df_after = df[~df.astype(str).apply(tuple, 1).isin(df_before.astype(str).apply(tuple, 1))]
        print(df_after)
        
        if(len(df_after) > 0):
            print(df_after)
            df_after.to_sql('news', con=self.engine, if_exists='append', index=False)
            
          
    #get historical news associated to the entered keyword
    def get_news_db(self, keyword):
        if(keyword == ""):
            return 
        sql_req = "SELECT * FROM news WHERE keyword = '" + str(keyword.lower()) + "';"
        df = pd.read_sql(sql_req, self.engine)

        return df
