import streamlit as st
from streamlit_extras.switch_page_button import switch_page
import base64
from pathlib import Path

def img_to_bytes(img_path):
    img_bytes = Path(img_path).read_bytes()
    encoded = base64.b64encode(img_bytes).decode()
    return encoded

def image_encoded(img_path):
    img_html = "data:image/png;base64,{}".format(
      img_to_bytes(img_path)
    )
    return img_html

st.set_page_config(layout = 'centered',initial_sidebar_state='collapsed')

st.markdown("<h2 style='text-align: center; color: #984ea3;'>Let the 'Elon Musk Tweets Analysis' sink in!!!</h2>",
            unsafe_allow_html=True)

st.video('https://video.twimg.com/ext_tw_video/1585341912877146112/pu/vid/1280x720/cwj11yOgYZ05R_sY.mp4?tag=14')

m = st.markdown("""
<style>
div.stButton > button:first-child {
    color: #00ACEE;
}
</style>""", unsafe_allow_html=True)

main_page_1 = st.columns(3)[1].button("Take me to the Exciting Stuff!!!")

with open('Home.md', 'r') as f:
    content = f.read()
    content = content.replace('./images/gcloud-service-key.png', image_encoded('images/gcloud-service-key.png'))
    st.markdown(content, unsafe_allow_html=True)


main_page_2 = st.columns(3)[1].button("Let's check the Real Stuff!!!")

if main_page_1 or main_page_2:
    switch_page("Summary")

