import streamlit as st
import pandas as pd
from collections import Counter
from wordcloud import WordCloud
import altair as alt
from datetime import datetime
from PIL import Image
from util import load_data

# Layout of the page
st.set_page_config(layout="wide")

# Read the dataframe
if 'dataframe' in st.session_state:
    data = st.session_state['dataframe']
else:
    data = load_data()
    # Add the dataframe into the session to access it in the "Detailed" page
    st.session_state['dataframe'] = data


emotion_image = Image.open('images/main_page_image.png')
st.columns(5)[2].image(emotion_image)

# Heading of the page
st.markdown("<h2 style='text-align: center; color: #984ea3;'>Elon Musk Tweets Overall Information</h2>",
            unsafe_allow_html=True)

data = load_data()

# Add the dataframe into the session to access it in the "Detailed" page
if 'dataframe' not in st.session_state:
    st.session_state['dataframe'] = data


# Add the space between the heading and the tabs
st.markdown('#')
# Add the spaces between the tabs
whitespace = 9
tab1, tab2 = st.tabs([s.center(whitespace, "\u2001")
                     for s in ['Posts', 'Posts Engagement']])

with tab1:
#-------------------------------------- Word Cloud on Elon Musk Topics ------------------------------------
    # Get all the Noun Keyphrases in the list
    keyphrases = data['noun_keyphrases']
    # explode the data into list and remove entries whose noun keyphrases were not available
    keyphrases = keyphrases.explode().dropna().to_list()

    # Count the key-phrases based on the frequency of their occurrence
    word_could_dict = Counter(keyphrases)

    cloud = WordCloud(background_color="white",
                      width=800,
                      height=500,
                      random_state=42)
    wc = cloud.generate_from_frequencies(word_could_dict)

    st.markdown('#')

    st.markdown('<div style="text-align: center; font-size:20px; color : #000000;">\
                <b><i><u>What Elon Musk has been talking about in his tweets? \
                                </u></i></b></div>', unsafe_allow_html=True)
    st.markdown('##')

    col1, col2, col3 = st.columns([1, 6, 1])
    col2.image(wc.to_array())

    st.markdown('#')
    st.markdown('#')
#---------------------------------- Elon Musk Tweets bifurcation based on days and hour of the day------------------------------
    
    st.markdown('<div style="text-align: center;font-size:20px; color : #000000;">\
                    <b><i><u>Elon Musk total tweets bifurcation based \
                    on days and the hour of day</u></i></b></div>', unsafe_allow_html=True)
    st.markdown('#')
    
    # Define the function to create the day-wise and hour-wise graphs
    def create_count_charts(groupby_var, main_title_word):
        chart_data = data.groupby(groupby_var)[
            'tweets'].size().reset_index(name='count')

        main_chart_title = f'{main_title_word} on which Elon Musk post most tweets'
        x_title = f'{main_title_word} of the Week'
        col = groupby_var + ':O'
        if groupby_var == 'weekday':
            sort = ['Monday', 'Tuesday', 'Wednesday',
                    'Thursday', 'Friday', 'Saturday', 'Sunday']
            color = 'purple'
        else:
            sort = 'ascending'
            color = 'orange'

        base = alt.Chart(chart_data, title=[main_chart_title, " "])\
            .encode(alt.X(col,
                          sort=sort,
                          title=x_title))

        bar_chart = base.mark_bar(color=color)\
                        .encode(
            alt.Y('count', title='Total Tweets Posted'),
            tooltip=alt.Tooltip('count')
        ).properties(width=500)


        if groupby_var == 'weekday':            
            col1.altair_chart(bar_chart, use_container_width=False)
        else:
            line = base.mark_line(color='red').encode(y='count')            
            col2.altair_chart((bar_chart + line), use_container_width=False)

    col1, col2 = st.columns(2)

    # Create the chart for the total posts based on days
    create_count_charts('weekday', f"Day's 📅")
    # Create the chart for the total posts based on the hour of the day
    create_count_charts('hour', f"Hour ⏰")

#------------------------------------- Daily Frequency Tweets Chart -------------------------------------------------------
    st.markdown("#")
    # graph about tweets posted per day. Instead of adding date part column in dataframe, the
    # value is calculated in the groupby function itself
    day_tweets = data.groupby(data.date.dt.date)['tweets'].count(
    ).reset_index().rename(columns={'tweets': 'count'})

    # Altair parse the date in UTC which was making the dates to be displayed in altair as date - 1
    day_tweets['date'] = pd.to_datetime(
        day_tweets['date']).dt.tz_localize('US/Eastern')

    top_2_dates = day_tweets.sort_values(
        by=['count'], ascending=False).head(2).reset_index(drop=True)
    date1 = top_2_dates.loc[0, 'date']
    date1 = datetime.strftime(date1, '%b %d, %Y')
    count1 = top_2_dates.loc[0, 'count']

    date2 = top_2_dates.loc[1, 'date']
    date2 = datetime.strftime(date2, '%b %d, %Y')
    count2 = top_2_dates.loc[1, 'count']

    daily_line_chart = alt.Chart(day_tweets, title=["Daily Frequency of Elon Musk Tweets", " "," "]).mark_line(color='green')\
        .encode(alt.X('date',
                      title='Date'),
                alt.Y('count', title='Total Tweets Posted'),
                tooltip=alt.Tooltip(['date', 'count'])
                )
    text = daily_line_chart.mark_text(align='center', baseline='middle', dx=5, dy=-4, color='#000').encode(
        text=alt.condition(alt.datum.count == count1,
                           alt.value(date1), alt.value(""))
    )
    text1 = daily_line_chart.mark_text(align='center', baseline='middle', dx=5, dy=-4, color='#000').encode(
        text=alt.condition(alt.datum.count == count2,
                           alt.value(date2), alt.value(""))
    )

    st.altair_chart(alt.layer(daily_line_chart, text, text1),
                    use_container_width=True)

with tab2:

    def humanize_interval(input):
        num = input.right.item()
        if num < 1000000:
            return '{:.1f}K'.format(num / 1000)
        elif num < 1000000000:
            return '{:.1f}M'.format(num / 1000000)
        else:
            return '{:.1f}B'.format(num / 1000000000)

# ------------ graph about number of tweets liked by the followers (binning done on the number of likes)---------------------------
    # Define the size of the bin
    like_binsize = (data['likes'].max() + 1000) // 20
    # create the bins
    like_bins = range(0, data['likes'].max() + 1000, like_binsize)

    # segment the data based on the bins created
    likes_tweets = data.groupby(pd.cut(data['likes'], bins=like_bins))[
        'tweets'].size().reset_index(name='count')
    # convert the likes value into more readable format
    likes_tweets['likes'] = likes_tweets['likes'].apply(humanize_interval)

    # Create Area Chart
    area_chart_likes = alt.Chart(likes_tweets, title=['Distribution of Tweets with respect to Likes', " "]).mark_area(color='#beaed4')\
        .encode(
                    alt.X("likes:O",
                        sort=None,
                        title='Likes (Bins)'
                        ),
                    alt.Y('count', title='No. of Tweets'),
                    alt.Tooltip(['likes', 'count'])
                )
    st.altair_chart(area_chart_likes, use_container_width=True)

#------------- graph about number of tweets retweeted by the followers (binning done on the number of retweets)-------------------
    retweet_binsize = (data['retweets'].max() + 1000) // 20
    # create the bins
    retweets_bins = range(0, data['retweets'].max() + 1000, retweet_binsize)

    # segment the data based on the bins created
    retweets_tweets = data.groupby(pd.cut(data['retweets'], bins=retweets_bins))[
        'tweets'].size().reset_index(name='count')
    # convert the retweets value into more readable format
    retweets_tweets['retweets'] = retweets_tweets['retweets'].apply(
        humanize_interval)
    # create the area chart
    area_chart_retweets = alt.Chart(retweets_tweets, title=['Distribution of Tweets with respect to Retweets'," "]).mark_area(color='#9467bd')\
        .encode(
                    alt.X("retweets:O", sort=None,
                        title='Retweets (Bins)'
                        ),
                    alt.Y('count', title='No. of Tweets'),
                    alt.Tooltip(['retweets', 'count'])
                )
    st.altair_chart(area_chart_retweets, use_container_width=True)
