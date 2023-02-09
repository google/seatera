import streamlit as st
from utils.config import Config
import utils.auth as auth
from time import sleep
from main import run_from_ui, get_accounts_for_ui
from datetime import datetime

OAUTH_HELP = """Refer to
        [Create OAuth2 Credentials](https://developers.google.com/google-ads/api/docs/client-libs/python/oauth-web#create_oauth2_credentials)
        for more information"""


def validate_config(config):
    if config.valid_config:
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
    if "accounts_for_ui" not in st.session_state:
        st.session_state.accounts_for_ui = []

def authenticate(config_params):
    st.session_state.config.client_id = config_params['client_id']
    st.session_state.config.client_secret = config_params['client_secret']
    st.session_state.config.refresh_token = config_params['refresh_token']
    st.session_state.config.developer_token = config_params['developer_token']
    st.session_state.config.login_customer_id = config_params['login_customer_id']
   
    st.session_state.config.check_valid_config()
    st.session_state.valid_config = True 
    st.session_state.config.save_to_file()

def reset_config():
    st.session_state.valid_config=False
    st.session_state.config.valid_config = False

def update_btn_state():
    # Needed to cloes settings expander before starting to process
    st.session_state.run_btn_clicked = True 

def get_accounts_list():
    st.session_state.accounts_for_ui = get_accounts_for_ui()

def value_placeholder(value):
    if value: return value
    else: return ''

def run_tool():
    parameters = {
            'start_date': str(st.session_state.start_date),
            'end_date': str(st.session_state.end_date),
            'clicks': st.session_state.clicks,
            'impressions': st.session_state.impressions,
            'ctr': st.session_state.ctr,
            'cost': st.session_state.cost,
            'conversions': st.session_state.conversions,
            'accounts': st.session_state.accounts_selected
        }

    run_from_ui(parameters, st.session_state.config)
    results_url = config.spreadsheet_url
    st.success(f'Search term analysis completed successfully. [Open in Google Sheets]({results_url})', icon="✅")

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
        client_id = st.text_input("Client ID", value=value_placeholder(config.client_id))
        client_secret = st.text_input("Client Secret", value=value_placeholder(config.client_secret))
        refresh_token = st.text_input("Refresh Token", value=value_placeholder(config.refresh_token))
        developer_token = st.text_input("Developer Token", value=value_placeholder(config.developer_token))
        mcc_id = st.text_input("MCC ID", value=value_placeholder(config.login_customer_id))
        login_btn = st.button("Save", type='primary',on_click=authenticate, args=[{
            'client_id': client_id,
            'client_secret': client_secret,
            'refresh_token': refresh_token,
            'developer_token': developer_token,
            'login_customer_id': mcc_id
        }])
    else:
        st.success(f'Credentials succesfully set ', icon="✅")
        st.text_input("Client ID", value=config.client_id, disabled= True)
        st.text_input("Client Secret", value=config.client_secret, disabled= True)
        st.text_input("Refresh Token", value=config.refresh_token, disabled=True)
        st.text_input("Developer Token", value=config.developer_token, disabled= True)
        st.text_input("MCC ID", value=config.login_customer_id, disabled= True)
        edit = st.button("Edit Credentials", on_click=reset_config)
    # bal = st.balloons()


with st.expander("**Run Settings**", expanded=st.session_state.valid_config and ("run_btn_clicked" not in st.session_state or not st.session_state.run_btn_clicked)):
   
    # Accounts picker
    st.radio("Run on all accounts under MCC or selecet specific accounts",["All Accounts", "Selected Accounts"], index=0, key="all_accounts", label_visibility="visible")
    if st.session_state.all_accounts == 'Selected Accounts':
        if "accounts_for_ui" not in st.session_state or st.session_state.accounts_for_ui == []:
            get_accounts_list()
        
        accounts_selected_explicit = st.multiselect("Choose Accounts", st.session_state.accounts_for_ui)
    
        st.session_state.accounts_selected = [x.split(' - ')[0] for x in accounts_selected_explicit]

    # Dates picker
    start_date, end_date = st.columns(2)
    start_date.date_input("Start Date", key="start_date")
    end_date.date_input("End Date", key="end_date")


    # Thresholds pickers
    clicks, impressions, ctr, cost, conversions = st.columns(5)
    clicks.number_input("Clicks", min_value=0, key="clicks")
    impressions.number_input("Impressions", min_value=0, key="impressions")
    ctr.number_input("CTR", min_value=0, key="ctr")
    cost.number_input("Cost", min_value=0, key="cost")
    conversions.number_input("Conversions", min_value=0, key="conversions")

st.session_state.run_btn_clicked = st.button("**Run**",type='primary', disabled=not st.session_state.valid_config, on_click=update_btn_state)

if st.session_state.run_btn_clicked:
    with st.spinner(text='Creating search term analysis... This may take a few minutes'):
        run_tool()