import pandas as pd
import streamlit as st
from collections import Counter
from wordcloud import WordCloud, STOPWORDS
import altair as alt
from datetime import timedelta
from PIL import Image
from millify import millify
import numpy as np
import util

# Layout of the page
st.set_page_config(layout="wide")

# Read the dataframe
if 'dataframe' in st.session_state:
    df = st.session_state['dataframe']
else:
    df = util.load_data()

st.sidebar.header("Detailed info on Elon Musk tweets")

# Define controls
SELECT_EMOTIONS_KEY = 'select_emotions'
SELECT_TOPICS_KEY = 'select_topics'

#----------------------------------------------------- Date Slider --------------------------------------------------------------
# Create the slider for the date to select
min_date = df['date'].dt.date.min()
max_date = df['date'].dt.date.max()
# Initial value to set the date on the slider
selected_date = (min_date + timedelta(days=30), max_date)
slider_date = st.sidebar.slider(
                'Select date', min_value=min_date, max_value=max_date, value=selected_date)

# Filter the dataframe based on the date range slider
df_date_filtered = df[df['date'].dt.date.between(slider_date[0], slider_date[1])]               

#----------------------------------------------------- Emotions Dropdown --------------------------------------------------------------
# Callback function when emotion is selected by the user
def on_select_emotions_change():   
    # Set the key value to all
    st.session_state[SELECT_TOPICS_KEY] = 'All'

# Get the first record of the dataframe for the column "emotion_scores" to retrive emotions text
emotions_list = list(set(df_date_filtered['emotion1']))

select_emotions = st.sidebar.selectbox(
    'Select Elon Musk emotions', ['All'] + emotions_list, key=SELECT_EMOTIONS_KEY, on_change=on_select_emotions_change)

st.sidebar.markdown('<center><b>OR</b></center>', unsafe_allow_html=True)

#----------------------------------------------------- Topics Dropdown --------------------------------------------------------------

# Retrieve the topics from the dataframe based on the date selected
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
    # If topic selected, individual emotion cannot be selected
    st.session_state[SELECT_EMOTIONS_KEY] = 'All'


# create dropdown for the user to select the topics
topics_list = ['All'] + list(topics_dict.keys())
select_topics = st.sidebar.selectbox(
    'Select Topics', options=topics_list, key=SELECT_TOPICS_KEY, format_func=concatenate, on_change=on_select_topics_change)

#----------------------------------- Filter records based on emotions/topics ---------------------------------------------- 
# filter records based on the selected values
def filter_records(record):
    result = True

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

# st.write(df_filtered)

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
   
# Select the image based on the emotion
emotion_image = Image.open('images/' + max_emotion + '.png')
st.columns(5)[2].image(emotion_image)

st.markdown("#")

# Create the tabs
whitespace = 9
tab1, tab2, tab3,tab4 = st.tabs([s.center(whitespace, "\u2001")
                     for s in ['Topics','Most Popular Tweets','Topics Adjectives', 'Topics Verbs']])

st.markdown("#")

with tab1:
    # Total number calculations
    col1, col2, col3 = st.columns(3)
    col1.metric(label= '**Total Likes :+1:**', value=millify(df_filtered['likes'].sum()))
    col2.metric(label = "**Total Retweets :repeat:**", value = millify(df_filtered['retweets'].sum()))
    col3.metric(label = "**Count of Tweets :1234:**", value =  str(df_filtered.shape[0]))

    st.markdown("#")
    # st.markdown("#")

#-------------------------------------- Word Cloud on Filtered Data ---------------------------------------------------------
    if select_emotions == 'All' and select_topics == 'All':
        st.markdown(f'<div style="text-align: center;font-size:20px;color : #000000;">\
                    <b><i><u>What Elon is saying in the period \
                    "{slider_date[0]}" to "{slider_date[1]}" </u></i></b></div>', unsafe_allow_html=True)
    elif select_emotions != 'All' and select_topics == 'All':
        st.markdown(f'<div style="text-align: center;font-size:20px;color : #000000;">\
                        <b><i><u>What does Elon write when he is in \
                        "{select_emotions}" mood </u></i></b></div>', unsafe_allow_html=True)  
    elif select_emotions == 'All' and select_topics != 'All':
        topic_val = select_topics.split('-')[0]
        st.markdown(f'<div style="text-align: center;font-size:20px;color : #000000;">\
                    <b><i><u>What Elon is writing about  \
                    "{topic_val}"</u></i></b></div>', unsafe_allow_html=True)                                                                            
                                                
        
    st.markdown("#")

    # stopwords = set(STOPWORDS)
    # stopwords.update(['us', 'one', 'will', 'said', 'now', 'well', 'man', 'may',
    #                 'little', 'say', 'must', 'way', 'long', 'yet', 'mean',
    #                 'put', 'seem', 'asked', 'made', 'half', 'much',
    #                 'certainly', 'might', 'came', 'true', 'ago', 'really',
    #                 'rather', 'using', 'many', 'sure', 'lot', 'vs', 'run',
    #                 'top', 'wait', 'every', 'everything', 'whoever','yes','lmk','gets','9s','60b',
    #                 'let','want','anyone','come','making','done','soon','twice','bs','go','gave','make','etc'])
    # cloud = WordCloud(background_color="white",
    #                 width=800,
    #                 height=500,
    #                 stopwords=stopwords,
    #                 random_state=42)
    # wc = cloud.generate(' '.join(df_filtered['cleaned_tweets'].str.lower().to_list()))
    # mask = np.array(Image.open("images/wordcloud_twitter.png"))
    wc = util.create_wordcloud(df_filtered, 800, 500)

    col1, col2, col3 = st.columns([1, 6, 1])
    col2.image(wc.to_array())
    st.markdown('#')
    st.markdown('#')
#------------------------------------ Daily Tweets based on Filters ------------------------------------------------
    # Graph about tweets posted per day. 
    day_tweets = df_filtered.groupby(df_filtered['date'].dt.date)[
        'tweets'].size().reset_index(name='count')
    # Altair parse the date in UTC which was making the dates to be displayed in altair as date - 1
    day_tweets['date'] = pd.to_datetime(day_tweets['date']).dt.tz_localize('US/Eastern')

    # If the dataframe has data for greater than 30 days show line chart, else show bar chart
    # line chart else show bar chart
    if len(set(day_tweets.date)) > 30:

        posting_chart = alt.Chart(day_tweets,\
                 title=["Daily Frequency of Elon Musk Tweets for date range " + '"' + str(slider_date[0]) + '"'\
                        + " to " + '"' + str(slider_date[1]) + '"'," "]).mark_line(color='green')\
            .encode(alt.X('date',
                        sort='ascending',
                        title='Date'),
                    alt.Y('count', title='Total Tweets Posted'),
                    tooltip=alt.Tooltip(['date','count'])
                    )
    else:
        posting_chart = alt.Chart(day_tweets,\
             title=["Daily Frequency of Elon Musk Tweets for date range " + '"' + str(slider_date[0]) + '"'\
                        + " to " + '"' + str(slider_date[1]) + '"'," "]).mark_bar(color='green', size = 15)\
            .encode(alt.X('date',
                        sort='ascending',
                        title='Date'),
                    alt.Y('count', title='Total Tweets Posted'),
                    tooltip=alt.Tooltip(['date','count'])
                    )

    st.altair_chart(posting_chart, use_container_width=True)

    st.markdown('#')
    st.markdown('#')

    st.markdown(f'<div style="text-align: center;font-size:20px;color : #000000;">\
                    <b><i><u>Elon Musk fan following during   \
                    "{slider_date[0]}" to "{slider_date[1]}"</u></i></b></div>', unsafe_allow_html=True
                    )
    # graph about number of tweets liked by the followers (binning done on the number of likes)
    def humanize_interval(input):
        num = input.right.item()
        if num < 1000000:
            return '{:.1f}K'.format(num / 1000)
        elif num < 1000000000:
            return '{:.1f}M'.format(num / 1000000)
        else:
            return '{:.1f}B'.format(num / 1000000000)

    like_binsize = (df_filtered['likes'].max() + 1000) // 20
    like_bins = range(0, df_filtered['likes'].max() + 1000, like_binsize)

    likes_tweets = df_filtered.groupby(pd.cut(df_filtered['likes'], bins=like_bins))[
        'tweets'].size().reset_index(name='count')
    likes_tweets['likes'] = likes_tweets['likes'].apply(humanize_interval)

    area_chart_likes = alt.Chart(likes_tweets, title=['Distribution of Tweets with respect to Likes'," "])\
                        .mark_area(color='#beaed4')\
                        .encode(
                                    alt.X("likes:O",
                                        sort=None,
                                        title='Likes (Bins)'
                                        ),
                                    alt.Y('count', title='No. of Tweets'),
                                    alt.Tooltip(['likes', 'count'])
                                )
    st.markdown('#')
    st.markdown('#')
    st.altair_chart(area_chart_likes, use_container_width=True)

    # graph about number of tweets retweeted by the followers (binning done on the number of retweets)
    retweet_binsize = (df_filtered['retweets'].max() + 1000) // 20
    retweets_bins = range(0, df_filtered['retweets'].max() + 1000, retweet_binsize)

    retweets_tweets = df_filtered.groupby(pd.cut(df_filtered['retweets'], bins=retweets_bins))[
        'tweets'].size().reset_index(name='count')
    retweets_tweets['retweets'] = retweets_tweets['retweets'].apply(humanize_interval)
    area_chart_retweets = alt.Chart(retweets_tweets, title=['Distribution of Tweets with respect to Retweets'," "])\
                            .mark_area(color='#9467bd')\
                            .encode(
                                        alt.X("retweets:O", sort=None,
                                            title='Retweets (Bins)'
                                            ),
                                        alt.Y('count', title='No. of Tweets'),
                                        alt.Tooltip(['retweets', 'count'])
                                    )
    st.markdown('#')
    st.markdown('#')
    st.altair_chart(area_chart_retweets, use_container_width=True)

with tab2:
    
    # Find the outliers of the likes & retweets, to get the most popular tweets
    def most_popular_tweets(data,colname):
        Q3 = np.quantile(data[colname], 0.75)
        Q1 = np.quantile(data[colname], 0.25)
        IQR = Q3 - Q1
        upper_range = Q3 + (1.5 * IQR)
        data = data[data[colname] >= upper_range]
        if data.shape[0] > 1:        
            mask = np.array(Image.open("images/wordcloud_twitter.png"))
            # Call the word cloud function from the custom util package
            wc = util.create_wordcloud(data , 600, 400, mask)
            return wc       


    for i in ['likes','retweets']:
        wc = most_popular_tweets(df_filtered, i) 
        if wc is not None:
            st.markdown(f'<div style="text-align: center; font-size:20px; color : #000000;">\
                    <b><i><u>Most popular Tweets based on {str.capitalize(i)} \
                                    </u></i></b></div>', unsafe_allow_html=True)
            st.markdown("#")                                       
            col1, col2, col3 = st.columns([1, 6, 1])
            
            col2.image(wc.to_array())  
            st.markdown("#") 
        else:
            st.error(f'No popular Tweet found based on {str.capitalize(i)}', icon="🚨")

        
#--------------------------------------------------------------------------------------------------------------------------
with tab3:

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

with tab4:
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