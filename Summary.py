import streamlit as st
import pandas as pd
from collections import Counter
from wordcloud import WordCloud
import altair as alt
from datetime import datetime

# Layout of the page
st.set_page_config(layout = "wide")

# Heading of the page
st.markdown("<h2 style='text-align: center; color: #000000;'>Elon Musk Tweets Overall Information</h2>", unsafe_allow_html=True)

@st.cache(allow_output_mutation=True)
def load_data():
    data = pd.read_parquet('./data/processed_data.parquet')
    lowercase = lambda x: str(x).lower()
    data.rename(lowercase, axis='columns', inplace=True)  
    # Add the names of the weekday
    data['weekday'] = data.date.dt.day_name()  
    # Convert the UTC timezone in EST and extract the hour part from it
    data['hour'] = data.date.dt.tz_localize('UTC').dt.tz_convert('US/Eastern').dt.hour     
    return data

data = load_data()

# Add the dataframe into the session to access it in the "Detailed" page
if 'dataframe' not in st.session_state:
    st.session_state['dataframe'] = data

# Add the space between the heading and the tabs
st.markdown('#')
# Add the spaces between the tabs
whitespace = 9
tab1, tab2 = st.tabs([s.center(whitespace,"\u2001") for s in ['Posts','Posts Engagement']]) 

with tab1:

    # Get all the Noun Keyphrases in the list  
    keyphrases = data['noun_keyphrases']
    # explode the data into list and remove entries whose noun keyphrases were not available
    keyphrases = keyphrases.explode().dropna().to_list()

    # Count the key-phrases based on the frequency of their occurrence
    word_could_dict = Counter(keyphrases)

    cloud = WordCloud(background_color = "white", 
                    width = 800,
                    height = 500,
                    random_state=42)
    wc = cloud.generate_from_frequencies(word_could_dict)


    st.markdown('#')

    st.markdown('<div style="text-align: center; color : #000000;"><b><i><u>What Elon Musk has been talking about in his tweets? \
                                </u></i></b></div>', unsafe_allow_html=True)
    st.markdown('##')                             

    st.image(wc.to_array())

    st.markdown('#')
    st.markdown('#')

    st.markdown('<div style="text-align: center; color : #000000;"><b><i><u>Elon Musk total tweets bifurcation based \
                                on days and the hour of day</u></i></b></div>', unsafe_allow_html=True)
    st.markdown('##')  

    # Define the function to create the day-wise and hour-wise graphs
    def create_count_charts(groupby_var, main_title_word):
        chart_data =  data.groupby(groupby_var)['tweets'].size().reset_index(name = 'count')

        main_chart_title = main_title_word + ' on which Elon Musk post most tweets'
        x_title = main_title_word + ' of the Week'
        col = groupby_var + ':O'
        if groupby_var == 'weekday':
            sort=['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
            color = 'purple'
        else:
            sort='ascending'
            color = 'orange'

        base = alt.Chart(chart_data, title = main_chart_title)\
                                .encode(alt.X(col , 
                                            sort=sort,
                                            title = x_title))  

        bar_chart = base.mark_bar(color = color)\
                        .encode(                            
                                alt.Y('count' , title= 'Total Tweets Posted'),
                                tooltip = alt.Tooltip('count')              
                                ).properties(width = 500) 

        if groupby_var == 'weekday':
            col1.altair_chart(bar_chart, use_container_width=True)
        else :             
            line =  base.mark_line(color='red').encode(y='count')  
            col2.altair_chart((bar_chart + line), use_container_width=True)                                                                                              

    col1, col2 = st.columns(2)

    # Create the chart for the total posts based on days
    create_count_charts('weekday', "Day's")
    # Create the chart for the total posts based on th hour of the day
    create_count_charts('hour', "Hour")        

    st.markdown("#")
    # graph about tweets posted per day. Instead of adding date part column in dataframe, the
    # value is calculated in the groupby function itself
    day_tweets = data.groupby(data.date.dt.date)['tweets'].count().reset_index().rename(columns = {'tweets': 'count'})

    # Altair parse the date in UTC which was making the dates to be displayed in altair as date - 1
    day_tweets['date'] = pd.to_datetime(day_tweets['date']).dt.tz_localize('US/Eastern')

    top_2_dates = day_tweets.sort_values(by=['count'],ascending=False).head(2).reset_index(drop=True)
    date1 = top_2_dates.loc[0,'date']
    date1 = datetime.strftime(date1 , '%b %d, %Y')
    date2 = top_2_dates.loc[1,'date']
    date2 = datetime.strftime(date2 , '%b %d, %Y')
    
    
    daily_line_chart = alt.Chart(day_tweets, title = "Daily Frequency of Elon Musk Tweets").mark_line(color='green')\
                        .encode(alt.X('date' ,                                         
                                       title = 'Date'),
                                alt.Y('count' , title= 'Total Tweets Posted'),
                                tooltip = alt.Tooltip(['date','count']) 
                                )
    text = daily_line_chart.mark_text(align='center',baseline = 'middle', dx=5, dy=-4).encode(
                            text = alt.condition(alt.datum.count == 30 , alt.value(date1) , alt.value(""))
                        )   
    text1 = daily_line_chart.mark_text(align='center',baseline = 'middle', dx=5, dy=-4).encode(
                            text = alt.condition(alt.datum.count == 29 , alt.value(date2) , alt.value(""))
                        )                                                     

    st.altair_chart(alt.layer(daily_line_chart,text,text1), use_container_width=True)

with tab2:

    # graph about number of tweets liked by the followers (binning done on the number of likes)
    likes_tweets = data.groupby('likes')['tweets'].size().reset_index(name='count')
    hist_chart = alt.Chart(likes_tweets).mark_bar().encode(
                                                            alt.X("likes:O", bin=alt.Bin(maxbins=100,
                                                                    anchor= data.likes.min()),
                                                                    title = 'Bins of the Likes'
                                                                ),
                                                            alt.Y('count', title = 'Number of tweets lying in bin'),
                                                            alt.Tooltip(['likes','count'])
                                                        )
    st.altair_chart(hist_chart, use_container_width=True)  
                                                    

    # graph about number of tweets retweeted by the followers (binning done on the number of retweets)
    retweets_tweets = data.groupby('retweets')['tweets'].size().reset_index(name='count')
    hist_chart1 = alt.Chart(retweets_tweets, title = 'Number of retweets on Elon Musk tweets').mark_bar().encode(
                                                            alt.X("retweets:O", bin=alt.Bin(maxbins=100,
                                                                    anchor= data.retweets.min()),
                                                                    title = 'Bins of the Retweets'
                                                                ),
                                                            alt.Y('count', title = 'Retweets Count'),
                                                            alt.Tooltip(['retweets','count'])
                                                        )
    st.altair_chart(hist_chart1, use_container_width=True)


# listTabs = [
#     "A tab",
#     "🦈",
#     "More tabs",
#     "A long loooooong tab",
#     "🎨",
#     "x²"
# ]

# st.header("Tab alignment")
# st.subheader("No fill:")
# tabs = st.tabs(listTabs)

# st.markdown("----")

# whitespace = 9
# st.markdown("#### 💡 Center fill with whitespace (em-space):")
# ## Fills and centers each tab label with em-spaces
# tabs = st.tabs([s.center(whitespace,"\u2001") for s in listTabs])

# st.markdown("#### 🤔 Center fill with visible character")
# tabs = st.tabs([s.center(whitespace,"-") for s in listTabs])

# st.markdown("#### ❌ Regular spaces are stripped down by streamlit")
# tabs = st.tabs([s.center(whitespace," ") for s in listTabs])