<b>To view the Streamlit application and have fun, [Click Here!!](https://sakshi1989-elonmusk-tweets-nlp.streamlit.app/)</b>

<hr>

### _**Introduction**_
This project's intention was to analyze the world's richest man, Elon Musk (at the time of writing he was at the top position - [Forbe's Real Time Billionaires List](https://www.forbes.com/real-time-billionaires/#6589f38a3d78)) opinions about various topics, and how people react to it. 

For this purpose data was picked from **[Kaggle](https://www.kaggle.com/code/rajkumarpandey02/elon-musk-s-tweets-sentiment-analysis/data?select=cleandata.csv)** which contains tweets fron Jan-2022 to Oct-2022.

### _**Preparation**_
The following operations were performed on the data to prepare for the visualization.

**_Pre-Processing Steps:_**
- The tweets text were cleaned by performing below steps:

    a. Removing non-ASCII characters
    
    b. Fixing the quotes

    c. Expanding the contracted texts using - [pycontractions](https://pypi.org/project/pycontractions/)

    d. Removed the punctuations ignoring the digit separators using - _using regex negative lookahead pattern_ 
    
    `text = re.sub(r'[^\w\s%](?!\d)', ' ', text, flags=re.MULTILINE)`

    e. Removed stopwords

    f. Performed language detection and translation of non-english tweets using Google Cloud Translation API (more details below)

    g. Removed tweets with less than 2 words

### _**Processing**_

**_Emotions Classification:_**
- The Hugging Face :hugging_face: transformer was used to instantiate an open-source pre-trained model [Emanuel/bertweet-emotion-base](https://huggingface.co/Emanuel/bertweet-emotion-base) and tokenizer

- The transformer pipeline was used to classify the text into emotions - sadness, joy, love, anger , fear, surprise. [Demo Link](https://huggingface.co/spaces/Emanuel/twitter-emotions-demo)


**_Topic Extraction:_**
- Noun keyphrases were extracted using KeyBert
- Candidates key phrases were prepared using [CountVectorizer](https://maartengr.github.io/KeyBERT/guides/countvectorizer.html) and POS pattern `<NNP.*>+`
- Top 5 keyphrases were extracted for each tweet

**_Verbs and Adjectives extraction Steps :_**
- [flair](https://pypi.org/project/flair/0.11.3/) library was used to extract the verbs and adjectives part-of-speech from text 
- Before extracting different pos, verbs and adjectives were only extracted if the score was above 0.75

Finally the file was saved in the parquet file to be used by the streamlit application.

## Glossary

### Cloud Translation API setup

* Google Cloud Translation API must be enabled in the Google Cloud
* Create a Service Account in the "IAM and admin"
* Create a JSON key for the account and save it in a secure place
![Service Account Key](./images/gcloud-service-key.png)
* Install the following python package to use the Google Translate API

```pip install google-cloud-translate```

* Set the environment variable `GOOGLE_APPLICATION_CREDENTIALS` as the location of the key file. For example, in a Jupyter Notebook Code cell, add following:

```
%env GOOGLE_APPLICATION_CREDENTIALS=C:\key.json
```
* Now the Translation client can be instantiated as follows:
```
# Google client object
client = translate.Client()
```
<hr>
<h3><i><b>Reproducing the Report</b></i></h3>
To run the Streamlit app locally instead of just using the link perform the folowing steps:-
<ol>
<li>Download all the folder and notebook - 
    <ol type="a">
    <li><i> '.streamlit' --> contains streamlit configuration file to change the aesthetics of the application  </i></li>
    <li><i>'data' --> holds the initial data and the data after the processing based on the steps mentioned above</i></li>
    <li><i>'images' --> holds all the images of elon musk emotions and twitter shape to hold the tweets. This also contains the video clip for the main page of the application.</i></li>
    <li><i>'elonmusk_tweets' --> This is the main Streamlit application package. It contains "util.py" that has two functions - a. load the data b. wordcloud creation. "Home.py" is the landing page of the application. The other two pages "Summary" and "Detailed" is in the pages folder.</i></li>
    <li><i>'elonmusk.ipynb' --> notebook for the preparation of the data. </i></li>
    </ol>
</li>
<li>Install all the packages mentioned in the "requirements.txt" file

```
pip install -r requirements.txt
```
</li>
</ol> 