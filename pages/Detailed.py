import pandas as pd
import streamlit as st
from collections import Counter
from wordcloud import WordCloud, STOPWORDS
import altair as alt
from datetime import timedelta
from PIL import Image

st.sidebar.header("Detailed info on Elon Musk tweets")

if 'dataframe' in st.session_state:
    df = st.session_state['dataframe']

st.write(df)

# Define controls
SELECT_EMOTIONS_KEY = 'select_emotions'
SELECT_TOPICS_KEY = 'select_topics'

# Create the slider for the date to select
min_date = df['date'].dt.date.min()
max_date = df['date'].dt.date.max()
selected_date = (min_date + timedelta(days=30), max_date)
slider_date = st.sidebar.slider(
    'Select date', min_value=min_date, max_value=max_date, value=selected_date)


# Create the emotions drop down
def on_select_emotions_change():
    st.session_state[SELECT_TOPICS_KEY] = 'All'


emotions = list(df.loc[0, 'emotion_scores'])
emotions_list = ['All'] + [x['label'] for x in emotions]
select_emotions = st.sidebar.selectbox(
    'Select Elon Musk emotions', emotions_list, key=SELECT_EMOTIONS_KEY, on_change=on_select_emotions_change)


st.sidebar.markdown('<center><b>OR</b></center>', unsafe_allow_html=True)

# Create the dropdown for the topic on which elon musk is talking (Topic and the number of times it appeared)
# Retrive the topics from the dataframe based on the date selected
topics = list(df[df['date'].dt.date.between(
    slider_date[0], slider_date[1])]['noun_keyphrases'])

# Create the list of topics which elon musk talked about in the date range selected
topics_list = []
for value in topics:
    for item in value:
        if len(item) != 0:
            topics_list.append(item)
# get the frequency count of each topic
topics_with_count = Counter(topics_list)

# if 'topics' in st.session_state:
#     topics = st.session_state['topics']

# sort the topics based on the frequency in an ascending order and filter the
# ones with 1 frequency
topics_dict = {k: v for k, v in sorted(
    topics_with_count.items(), reverse=True, key=lambda value: value[1]) if v > 1}


# Using the format_func to change how the value will appear in drop down
def concatenate(topic_key):
    if topic_key == 'All':
        return topic_key
    return topic_key + '-' + str(topics_dict[topic_key])


def on_select_topics_change():
    st.session_state[SELECT_EMOTIONS_KEY] = 'All'


# create dropdown for the user to select the topics
topics_list = ['All'] + list(topics_dict.keys())
select_topics = st.sidebar.selectbox(
    'Select Topics', options=topics_list, key=SELECT_TOPICS_KEY, format_func=concatenate, on_change=on_select_topics_change)


# Reset filters


# filter records based on the selected values


def filter_records(record):
    result = True

    # Filter using date slider value
    result = result and slider_date[0] <= record['date'].date(
    ) <= slider_date[1]

    # Filter using select topics
    if select_topics != 'All':
        splitted = select_topics.split('-')
        result = result and splitted[0] in record['noun_keyphrases']

    if select_emotions != 'All':
        result = result and (
            record['emotion1'] == select_emotions or record['emotion1'] == select_emotions)

    return result


# apply the filter mask
filter_mask = df.apply(filter_records, axis=1)
df_filtered = df[filter_mask]


# Show the data
st.write(df_filtered)

# generate wordcloud from the filtered data
stopwords = set(STOPWORDS)
stopwords.update(['us', 'one', 'will', 'said', 'now', 'well', 'man', 'may',
                  'little', 'say', 'must', 'way', 'long', 'yet', 'mean',
                  'put', 'seem', 'asked', 'made', 'half', 'much',
                  'certainly', 'might', 'came', 'true', 'ago', 'really',
                  'rather', 'using', 'many', 'sure', 'lot', 'vs', 'run',
                  'top', 'wait', 'every', 'everything', 'whoever'])
cloud = WordCloud(background_color="white",
                  width=800,
                  height=500,
                  stopwords=stopwords,
                  random_state=42)
wc = cloud.generate(' '.join(df_filtered['cleaned_tweets'].to_list()))
st.image(wc.to_array())

# graph about tweets posted per day. Instead of adding date part column in dataframe, the
# value is calculated in the groupby function itself
day_tweets = df_filtered.groupby(df_filtered['date'].dt.date)[
    'tweets'].size().reset_index(name='count')

daily_line_chart = alt.Chart(day_tweets, title="Daily Frequency of Elon Musk Tweets").mark_line(color='red')\
    .encode(alt.X('date',
                  sort='ascending',
                  title='Date'),
            alt.Y('count', title='Total Tweets Posted'),
            tooltip=alt.Tooltip('count')
            )

st.altair_chart(daily_line_chart, use_container_width=True)

# graph about number of tweets liked by the followers (binning done on the number of likes)
likes_tweets = df_filtered.groupby(
    'likes')['tweets'].size().reset_index(name='count')
hist_chart = alt.Chart(likes_tweets).mark_bar().encode(
    alt.X("likes:O", bin=alt.Bin(maxbins=100,
                                 anchor=df_filtered.likes.min()),
          title='Bins of the Likes'
          ),
    alt.Y('count', title='Number of tweets lying in bin'),
    alt.Tooltip(['likes', 'count'])
)
st.altair_chart(hist_chart, use_container_width=True)


# graph about number of tweets retweeted by the followers (binning done on the number of retweets)
retweets_tweets = df_filtered.groupby(
    'retweets')['tweets'].size().reset_index(name='count')
hist_chart1 = alt.Chart(retweets_tweets, title='Number of retweets on Elon Musk tweets').mark_bar().encode(
    alt.X("retweets:O", bin=alt.Bin(maxbins=100,
                                    anchor=df_filtered.retweets.min()),
          title='Bins of the Retweets'
          ),
    alt.Y('count', title='Retweets Count'),
    alt.Tooltip(['retweets', 'count'])
)
st.altair_chart(hist_chart1, use_container_width=True)


# Total number calculations
st.write("Total Likes: " + str(df_filtered['likes'].sum()))
st.write("Total Retweets: " + str(df_filtered['retweets'].sum()))
st.write("Count of Tweets: " + str(df_filtered.shape[0]))

# Overall emotion calculation
total_emotion_scores = {x['label']: 0 for x in emotions}


def calculate_agg_emotion(score, total):
    for item in score:
        total[item['label']] += item['score']


df_filtered['emotion_scores'].apply(
    calculate_agg_emotion, args=(total_emotion_scores,))


st.write(total_emotion_scores)
max_emotion = max(total_emotion_scores, key=total_emotion_scores.get)

emotion_image = Image.open('./emotion-images/' + max_emotion + '.png')
st.image(emotion_image)


# Bar chart for Adjective
if select_topics != 'All':
    min_word = 2
    adjs = df_filtered['adjectives'].explode().dropna().to_list()
    st.write(adjs)
    word_freq = Counter(adjs)
    
    df_freq = pd.DataFrame(list(word_freq.items()),columns = ['Words', 'Word_Count'])
 
    # Plot the bar chart where the word count should be >= min_word
    df_freq = df_freq.loc[df_freq['Word_Count'] >= min_word , :]
    # # Only use the top max_word set by the user
    # df_freq = df_freq.iloc[:max_word, :]

    # Get the maximum count of the word
    max_count = df_freq['Word_Count'].max()
    # the height of the bar should increase as the max_word increases
    scale = alt.Scale(
        domain=[min_word, max_count],            
        scheme='blues',
        type='linear'
    )
    bar_chart = alt.Chart(df_freq , title = "Bar Chart for - " + select_topics).mark_bar().encode(                
                                                alt.X('Word_Count', title='Frequencies'),
                                                alt.Y('Words', sort = alt.EncodingSortField(field="Word_Count", op="sum", order="descending")),
                                                text = 'Word_Count',
                                                color=alt.Color('Word_Count', scale=scale)
                                                            
                                            ) 
    text = bar_chart.mark_text(
                            align='left',
                            baseline='middle',                                
                            dx=3  # Nudges text to right so it doesn't appear on top of the bar
                        ).encode(
                            text='Word_Count'
                        )
    # cht_expander = st.expander('', expanded=True)
    # cht_expander.altair_chart(bar_chart + text, use_container_width=True)                            
    st.altair_chart(bar_chart + text, use_container_width=True)



    min_word = 2
    verbs = df_filtered['verbs'].explode().dropna().to_list()
    word_freq = Counter(verbs)
    df_freq = pd.DataFrame(list(word_freq.items()),columns = ['Words', 'Word_Count'])
 
    # Plot the bar chart where the word count should be >= min_word
    df_freq = df_freq.loc[df_freq['Word_Count'] >= min_word , :]
    # # Only use the top max_word set by the user
    # df_freq = df_freq.iloc[:max_word, :]

    # Get the maximum count of the word
    max_count = df_freq['Word_Count'].max()
    # the height of the bar should increase as the max_word increases
    scale = alt.Scale(
        domain=[min_word, max_count],            
        scheme='blues',
        type='linear'
    )
    bar_chart = alt.Chart(df_freq , title = "Bar Chart for - " + select_topics).mark_bar().encode(                
                                                alt.X('Word_Count', title='Frequencies'),
                                                alt.Y('Words', sort = alt.EncodingSortField(field="Word_Count", op="sum", order="descending")),
                                                text = 'Word_Count',
                                                color=alt.Color('Word_Count', scale=scale)
                                                            
                                            ) 
    text = bar_chart.mark_text(
                            align='left',
                            baseline='middle',                                
                            dx=3  # Nudges text to right so it doesn't appear on top of the bar
                        ).encode(
                            text='Word_Count'
                        )
    # cht_expander = st.expander('', expanded=True)
    # cht_expander.altair_chart(bar_chart + text, use_container_width=True)                            
    st.altair_chart(bar_chart + text, use_container_width=True)