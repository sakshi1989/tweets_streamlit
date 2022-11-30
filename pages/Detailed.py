import pandas as pd
import streamlit as st
from collections import Counter
from wordcloud import WordCloud, STOPWORDS
import altair as alt
from datetime import timedelta
from PIL import Image
from millify import millify
import numpy as np

if 'dataframe' in st.session_state:
    df = st.session_state['dataframe']

st.sidebar.header("Detailed info on Elon Musk tweets")

# Define controls
SELECT_EMOTIONS_KEY = 'select_emotions'
SELECT_TOPICS_KEY = 'select_topics'

# Create the slider for the date to select
min_date = df['date'].dt.date.min()
max_date = df['date'].dt.date.max()
# Initial value to set the date on the slider
selected_date = (min_date + timedelta(days=272), max_date)
slider_date = st.sidebar.slider(
                'Select date', min_value=min_date, max_value=max_date, value=selected_date)

# Filter the dataframe based on the date range slider
df_date_filtered = df[df['date'].dt.date.between(slider_date[0], slider_date[1])]               


# Create the emotions drop down

def on_select_emotions_change():   # Callback function when emotion is selected by the user 
    # Set the key value to all
    st.session_state[SELECT_TOPICS_KEY] = 'All'

# Get the first record of the dataframe for the column "emotion_scores" to retrive emotions text
# emotions = list(df.loc[0, 'emotion_scores'])
emotions_list = list(set(df_date_filtered['emotion1']))

# Add the "all" label to the emotions extracted
# emotions_list = ['All'] + [x['label'] for x in emotions]

select_emotions = st.sidebar.selectbox(
    'Select Elon Musk emotions', ['All'] + emotions_list, key=SELECT_EMOTIONS_KEY, on_change=on_select_emotions_change)


st.sidebar.markdown('<center><b>OR</b></center>', unsafe_allow_html=True)

# Create the dropdown for the topic on which elon musk is talking (Topic and the number of times it appeared)
# Retrive the topics from the dataframe based on the date selected
topics = list(df_date_filtered['noun_keyphrases'])

# Creating the combined list of all the topics
topics_list = []
for value in topics:
    for item in value:
        if len(item) != 0:
            topics_list.append(item)

# get the frequency count of each topic
topics_with_count = Counter(topics_list)

# sort the topics based on the frequency in the descending order and filter the
# ones with 1 frequency
topics_dict = {k: v for k, v in sorted(
                    topics_with_count.items(), reverse=True, key=lambda value: value[1]) if v > 1}


# Using the format_func to change how the value will appear in drop down
def concatenate(topic_key):
    if topic_key == 'All':
        return topic_key
    return topic_key + '-' + str(topics_dict[topic_key])


def on_select_topics_change():
    st.session_state[SELECT_EMOTIONS_KEY] = 'All'  # If topic selected, individual emotion cannot be selected


# create dropdown for the user to select the topics
topics_list = ['All'] + list(topics_dict.keys())
select_topics = st.sidebar.selectbox(
    'Select Topics', options=topics_list, key=SELECT_TOPICS_KEY, format_func=concatenate, on_change=on_select_topics_change)


# filter records based on the selected values
def filter_records(record):
    result = True

    # # Filter using date slider value
    # result = result and slider_date[0] <= record['date'].date(
    # ) <= slider_date[1]

    # Filter using select topics
    if select_topics != 'All':
        splitted = select_topics.split('-')
        result = result and splitted[0] in record['noun_keyphrases']

    if select_emotions != 'All':
        result = result and (record['emotion1'] == select_emotions)

    return result


# apply the filter mask
filter_mask = df_date_filtered.apply(filter_records, axis=1)
df_filtered = df_date_filtered[filter_mask].copy()
df_filtered.reset_index(drop=True, inplace=True)

# Overall emotion calculation
# Create the dictionary with key as the emotions and initialize the value with 0
total_emotion_scores = {x['label']: 0 for x in df_filtered.loc[0,'emotion_scores']}

if select_emotions == 'All':
    for value in df_filtered['emotion_scores']:
        # Convert the numpy ndarray to the dictionary
        value = { index[0]: v for index, v in np.ndenumerate(value) }          
        # As there are 6 emotions in each record of the dataframe, we need to process each emotion score  
        for record in value:   
            # Add the values of all the records in the dataframe for a particular emotion      
            total_emotion_scores[value[record]['label']] += value[record]['score']
    # From all the emotions get the emotion with high value
    max_emotion = max(total_emotion_scores, key=total_emotion_scores.get) 
else:
    max_emotion = select_emotions 
   
emotion_image = Image.open('./emotion-images/' + max_emotion + '.png')
st.columns(5)[2].image(emotion_image)

st.markdown("#")

# Create the tabs
whitespace = 9
tab1, tab2, tab3 = st.tabs([s.center(whitespace, "\u2001")
                     for s in ['Topics','Topics Adjectives', 'Topics Verbs']])

st.markdown("#")

with tab1:
    # Total number calculations
    col1, col2, col3 = st.columns(3)
    col1.metric(label= '**Total Likes :+1:**', value=millify(df_filtered['likes'].sum()))
    col2.metric(label = "**Total Retweets**", value = millify(df_filtered['retweets'].sum()))
    col3.metric(label = "**Count of Tweets**", value =  str(df_filtered.shape[0]))

    st.markdown("#")
    st.markdown("#")

    # generate wordcloud from the filtered data
    if select_emotions == 'All' and select_topics == 'All':
        st.markdown(f'<div style="text-align: center; color : #000000;"><b><i><u>What Elon is saying in the period  \
                                            {slider_date[0]} to {slider_date[1]} </u></i></b></div>', unsafe_allow_html=True)
    elif select_emotions != 'All' and select_topics == 'All':
        st.markdown(f'<div style="text-align: center; color : #000000;"><b><i><u>What does Elon write when he is in  \
                                            "{select_emotions}" mood </u></i></b></div>', unsafe_allow_html=True)  
    elif select_emotions == 'All' and select_topics != 'All':
        topic_val = select_topics.split('-')[0]
        st.markdown(f'<div style="text-align: center; color : #000000;"><b><i><u>What Elon is writing about  \
                                            "{topic_val}"</u></i></b></div>', unsafe_allow_html=True)                                                                            
                                                
        # st.markdown(f"What Elon is saying in the period '{slider_date[0]}' to '{slider_date[1]}'")
    st.markdown("#")

    stopwords = set(STOPWORDS)
    stopwords.update(['us', 'one', 'will', 'said', 'now', 'well', 'man', 'may',
                    'little', 'say', 'must', 'way', 'long', 'yet', 'mean',
                    'put', 'seem', 'asked', 'made', 'half', 'much',
                    'certainly', 'might', 'came', 'true', 'ago', 'really',
                    'rather', 'using', 'many', 'sure', 'lot', 'vs', 'run',
                    'top', 'wait', 'every', 'everything', 'whoever','yes','lmk','gets','9s','60b',
                    'let','want','anyone','come','making','done','soon','twice','bs','go','gave','make','etc'])
    cloud = WordCloud(background_color="white",
                    width=800,
                    height=500,
                    stopwords=stopwords,
                    random_state=42)
    wc = cloud.generate(' '.join(df_filtered['cleaned_tweets'].str.lower().to_list()))

    col1, col2, col3 = st.columns([1,6,1])

    col2.image(wc.to_array())

    # Graph about tweets posted per day. 
    day_tweets = df_filtered.groupby(df_filtered['date'].dt.date)[
        'tweets'].size().reset_index(name='count')
    # Altair parse the date in UTC which was making the dates to be displayed in altair as date - 1
    day_tweets['date'] = pd.to_datetime(day_tweets['date']).dt.tz_localize('US/Eastern')

    # If the number of records in the dataframe are greater than 5 then show
    # line chart else show bar chart
    st.write(len(set(day_tweets.date)))
    if len(set(day_tweets.date)) > 30:

        posting_chart = alt.Chart(day_tweets, title="Daily Frequency of Elon Musk Tweets").mark_line(color='green')\
            .encode(alt.X('date',
                        sort='ascending',
                        title='Date'),
                    alt.Y('count', title='Total Tweets Posted'),
                    tooltip=alt.Tooltip(['date','count'])
                    )
    else:
        posting_chart = alt.Chart(day_tweets, title="Daily Frequency of Elon Musk Tweets").mark_bar(color='green', size = 15)\
            .encode(alt.X('date',
                        sort='ascending',
                        title='Date'),
                    alt.Y('count', title='Total Tweets Posted'),
                    tooltip=alt.Tooltip(['date','count'])
                    )

    st.altair_chart(posting_chart, use_container_width=True)

    # # graph about number of tweets liked by the followers (binning done on the number of likes)
    # likes_tweets = df_filtered.groupby(
    #     'likes')['tweets'].size().reset_index(name='count')
    # hist_chart = alt.Chart(likes_tweets).mark_bar().encode(
    #     alt.X("likes:O", bin=alt.Bin(maxbins=100,
    #                                  anchor=df_filtered.likes.min()),
    #           title='Bins of the Likes'
    #           ),
    #     alt.Y('count', title='Number of tweets lying in bin'),
    #     alt.Tooltip(['likes', 'count'])
    # )
    # st.altair_chart(hist_chart, use_container_width=True)


    # # graph about number of tweets retweeted by the followers (binning done on the number of retweets)
    # retweets_tweets = df_filtered.groupby(
    #     'retweets')['tweets'].size().reset_index(name='count')
    # hist_chart1 = alt.Chart(retweets_tweets, title='Number of retweets on Elon Musk tweets').mark_bar().encode(
    #     alt.X("retweets:O", bin=alt.Bin(maxbins=100,
    #                                     anchor=df_filtered.retweets.min()),
    #           title='Bins of the Retweets'
    #           ),
    #     alt.Y('count', title='Retweets Count'),
    #     alt.Tooltip(['retweets', 'count'])
    # )
    # st.altair_chart(hist_chart1, use_container_width=True)

#--------------------------------------------------------------------------------------------------------------------------
with tab2:

    # Bar chart for Adjective
    if select_topics != 'All':      
        
        adjs = df_filtered['adjectives'].explode().dropna().to_list()
        
        word_freq = Counter(adjs)
        
        
        df_freq = pd.DataFrame(list(word_freq.items()),columns = ['Words', 'Word_Count'])
                
        min_count = df_freq['Word_Count'].min()
        max_count = df_freq['Word_Count'].max()

        col_list = st.columns(5)
        but1 = col_list[1].button('Top 5 Adjectives')
        but2 = col_list[2].button('Top 10 Adjectives')
        but3 = col_list[3].button('All Adjectives')

        if but1:
            df_freq = df_freq.sort_values(by = 'Word_Count', ascending=False).head(5)
        elif but2:
            df_freq = df_freq.sort_values(by = 'Word_Count', ascending=False).head(10)
              
                
        # the color gradient will decrease as the count of the word decreases
        scale = alt.Scale(
            domain=[min_count, max_count],            
            scheme='blues',
            type='linear'
        )
        bar_chart = alt.Chart(df_freq , title = "Bar Chart for " + select_topics + " adjectives").mark_bar().encode(                
                                                    alt.X('Word_Count', title='Frequencies', axis = alt.Axis(labels=False)),
                                                    alt.Y('Words', sort = alt.EncodingSortField(field="Word_Count", op="min", order="descending"), title='Adjectives'),
                                                    # text = 'Word_Count',
                                                    color=alt.Color('Word_Count', scale=scale)
                                                                
                                                ) 
        text = bar_chart.mark_text(
                                align='left',
                                baseline='middle',                                
                                dx=3  # Nudges text to right so it doesn't appear on top of the bar
                            ).encode(
                                text='Word_Count'
                            )                                  
        st.altair_chart(bar_chart + text, use_container_width=True)
    else:
        st.error("Please select the topic of your interest to see it's adjectives", icon="🚨")

with tab3:
    # Bar chart for Verbs
    if select_topics != 'All':      
        
        verbs = df_filtered['verbs'].explode().dropna().to_list()
        
        word_freq = Counter(verbs)
        
        
        df_freq = pd.DataFrame(list(word_freq.items()),columns = ['Words', 'Word_Count'])
                
        min_count = df_freq['Word_Count'].min()
        max_count = df_freq['Word_Count'].max()

        col_list = st.columns(5)
        but1 = col_list[1].button('Top 5 Verbs')
        but2 = col_list[2].button('Top 10 Verbs')
        but3 = col_list[3].button('All Verbs')

        if but1:
            df_freq = df_freq.sort_values(by = 'Word_Count', ascending=False).head(5)
        elif but2:
            df_freq = df_freq.sort_values(by = 'Word_Count', ascending=False).head(10)
              
                
        # the color gradient will decrease as the count of the word decreases
        scale = alt.Scale(
            domain=[min_count, max_count],            
            scheme='blues',
            type='linear'
        )
        bar_chart = alt.Chart(df_freq , title = "Bar Chart for " + select_topics + " verbs").mark_bar().encode(                
                                                    alt.X('Word_Count', title='Frequencies', axis = alt.Axis(labels=False)),
                                                    alt.Y('Words', sort = alt.EncodingSortField(field="Word_Count", op="min", order="descending"), title='Verbs'),
                                                    # text = 'Word_Count',
                                                    color=alt.Color('Word_Count', scale=scale)
                                                                
                                                ) 
        text = bar_chart.mark_text(
                                align='left',
                                baseline='middle',                                
                                dx=3  # Nudges text to right so it doesn't appear on top of the bar
                            ).encode(
                                text='Word_Count'
                            )                                  
        st.altair_chart(bar_chart + text, use_container_width=True)
    else:
        st.error("Please select the topic of your interest to see it's verbs", icon="🚨")