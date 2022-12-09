import pandas as pd
from collections import Counter
from wordcloud import WordCloud, STOPWORDS

# Function to load the data and add some additional columns
def load_data():
    data = pd.read_parquet('./data/processed_data.parquet')
    def lowercase(x): return str(x).lower()
    data.rename(lowercase, axis='columns', inplace=True)
    # Add the names of the weekday
    data['weekday'] = data.date.dt.day_name()
    # Convert the UTC timezone in EST and extract the hour part from it
    data['hour'] = data.date.dt.tz_localize(
        'UTC').dt.tz_convert('US/Eastern').dt.hour
    return data

# Function to create the detailed page WordCloud
def create_wordcloud(data, width, height, mask = None):
    stopwords = set(STOPWORDS)
    stopwords.update(['us', 'one', 'will', 'said', 'now', 'well', 'man', 'may',
                    'little', 'say', 'must', 'way', 'long', 'yet', 'mean','less',
                    'put', 'seem', 'asked', 'made', 'half', 'much','people','even',
                    'certainly', 'might', 'came', 'true', 'ago', 'really','think','thing',
                    'rather', 'using', 'many', 'sure', 'lot', 'vs', 'run','something',
                    'top', 'wait', 'every', 'everything', 'whoever','yes','lmk','gets','9s','60b',
                    'let','want','anyone','come','making','done','soon','twice','bs','go','gave','make','etc'])
    cloud = WordCloud(background_color="white",
                    width=width,
                    height=height,
                    stopwords=stopwords,
                    mask = mask,                    
                    collocations=False,
                    random_state=42).generate(' '.join(data['cleaned_tweets'].str.lower().to_list()))
    return cloud
