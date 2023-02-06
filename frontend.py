import streamlit as st
from utils.config import Config
import utils.auth as auth
from time import sleep

OAUTH_HELP = """Refer to
        [Create OAuth2 Credentials](https://developers.google.com/google-ads/api/docs/client-libs/python/oauth-web#create_oauth2_credentials)
        for more information"""


def validate_config(config):
    if config.refresh_token:
        st.session_state.valid_config = True
    else:
        st.session_state.valid_config = False

def initialize_session_state():
    if "valid_config" not in st.session_state:
        st.session_state.valid_config = False
    if "validating_config_wip" not in st.session_state:
        st.session_state.validating_config_wip = False
    if "config" not in st.session_state:
        st.session_state.config = Config()

def authenticate(config_params):
    config = st.session_state.config
    config.refresh_token = auth.main(config_params)
    config.save_to_file()
    st.session_state.config = config

def reset_config():
    st.session_state.valid_confog=False
    st.session_state.config.refresh_token = ''

def run_tool():
    sleep(8)
    st.success(f'Search term analysis completed successfully. [Open in Google Sheets]()', icon="✅")

# The Page UI starts here
st.set_page_config(
    page_title="SeaTerA",
    layout="centered"
)

customized_button = st.markdown("""
        <style >
            div.stButton {text-align:center}
        </style>""", unsafe_allow_html=True)

st.header("SeaTerA")

initialize_session_state()
config = st.session_state.config
validate_config(config)

with st.expander("**Authentication**", expanded=not st.session_state.valid_config):
    if not st.session_state.valid_config:
        st.info(f"Credentials are not set. {OAUTH_HELP}", icon="⚠️")
        client_id = st.text_input("Client ID", value=config.client_id)
        client_secret = st.text_input("Client Secret", value=config.client_secret)
        developer_token = st.text_input("Developer Token", value=config.developer_token)
        mcc_id = st.text_input("MCC ID", value=config.login_customer_id)
        login_btn = st.button("Log In", type='primary',on_click=authenticate, args=[{
            'client_id': client_id,
            'client_secret': client_secret,
            'developer_token': developer_token,
            'login_customer_id': mcc_id
        }])
    else:
        st.success(f'Credentials succesfully set ', icon="✅")
        st.text_input("Client ID", value=config.client_id, disabled= True)
        st.text_input("Client Secret", value=config.client_secret, disabled= True)
        st.text_input("Developer Token", value=config.developer_token, disabled= True)
        st.text_input("MCC ID", value=config.login_customer_id, disabled= True)
        edit = st.button("Edit Credentials", on_click=reset_config)
    # bal = st.balloons()

with st.expander("**Run Settings**", expanded=st.session_state.valid_config and ("run_btn_clicked" not in st.session_state or not st.session_state.run_btn_clicked)):
    start_date, end_date = st.columns(2)
    start_date.date_input("Start Date", key="start_date")
    end_date.date_input("End Date", key="end_date")
    clicks, impressions, ctr = st.columns(3)
    clicks.number_input("Clicks", min_value=0, key="clicks")
    impressions.number_input("Impressions", min_value=0, key="impressions")
    ctr.number_input("CTR", min_value=0, key="ctr")
    cost, conversions = st.columns(2)
    cost.number_input("Cost", min_value=0, key="cost")
    conversions.number_input("Conversions", min_value=0, key="conversions")
    st.session_state.run_btn_clicked = st.button("**Run**",type='primary', disabled=not st.session_state.valid_config)

if st.session_state.run_btn_clicked:
    with st.spinner(text='Creating search term analysis... This may take a few minutes'):
        run_tool()