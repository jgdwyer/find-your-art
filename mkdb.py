import pickle
import cln
from sqlalchemy import create_engine
import pandas as pd
import psycopg2

def store_db():
    df=pd.read_pickle('./dfs/art_c.pickle')
    df['date'] = cln.convert_year(df['date'], debug=False)
    engine = create_engine('postgresql://jgdwyer:1234@localhost/art_2')
    print(engine.url)
    df.to_sql('artworks', engine, if_exists='replace')
