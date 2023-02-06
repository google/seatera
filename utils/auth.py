# This file generates a refresh token to use with the Google Ads API, and populates
# it inside config.yaml.

import yaml
import hashlib
import os
import re
import socket
import sys
import webbrowser
from urllib.parse import unquote
from yaml.loader import SafeLoader
from google_auth_oauthlib.flow import Flow

SCOPES = ['https://www.googleapis.com/auth/adwords', 'https://www.googleapis.com/auth/spreadsheets',
          'https://www.googleapis.com/auth/drive.file', 'https://www.googleapis.com/auth/drive']
SERVER = "127.0.0.1"
PORT = 8080
REDIRECT_URI = f"http://{SERVER}:{PORT}"
CONFIG_FILE = './config.yaml'


def main(ga_config=None):
    if not ga_config:
        ga_config = get_config(CONFIG_FILE)
    # If YAML values are not filled out, return and display error
    if None in (ga_config.get('client_id'), ga_config.get('client_secret'), ga_config.get('login_customer_id'), ga_config.get('developer_token')):
        raise Exception(
            "Not all required parameters are configured in config.yaml. Refer to README for instructions.")

    flow = Flow.from_client_config({
        "installed": {
            "client_id": ga_config['client_id'],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_secret": ga_config['client_secret'],
            "redirect_uris": [
                "urn:ietf:wg:oauth:2.0:oob",
                SERVER
            ]
        }
    }, scopes=SCOPES)

    flow.redirect_uri = REDIRECT_URI
    # Create an anti-forgery state token as described here:
    # https://developers.google.com/identity/protocols/OpenIDConnect#createxsrftoken
    passthrough_val = hashlib.sha256(os.urandom(1024)).hexdigest()

    authorization_url, state = flow.authorization_url(
        access_type="offline",
        state=passthrough_val,
        prompt="consent",
    )
    webbrowser.open_new(authorization_url)

    # Retrieves an authorization code by opening a socket to receive the
    # redirect request and parsing the query parameters set in the URL.
    # Then pass the code back into the OAuth module to get a refresh token.
    code = unquote(_get_authorization_code(passthrough_val))
    flow.fetch_token(code=code)

    try:
        # Write refresh token to config.yaml
        ga_config['refresh_token'] = flow.credentials.refresh_token
        with open(CONFIG_FILE, 'w') as f:
            yaml.dump(ga_config, f)
        print("Refresh token updated and saved")
        return flow.credentials.refresh_token
    except Exception as e:
        print("could not write refresh token to google-ads.yaml file")
        print(e)


def _get_authorization_code(passthrough_val):
    """Opens a socket to handle a single HTTP request containing auth tokens.
      Args:
          passthrough_val: an anti-forgery token used to verify the request
            received by the socket.
      Returns:
          a str access token from the Google Auth service.
      """
    # Open a socket at _SERVER:_PORT and listen for a request
    sock = socket.socket()
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((SERVER, PORT))
    sock.listen(1)
    connection, address = sock.accept()
    data = connection.recv(1024)
    # Parse the raw request to retrieve the URL query parameters.
    params = _parse_raw_query_params(data)
    try:
        if not params.get("code"):
            # If no code is present in the query params then there will be an
            # error message with more details.
            error = params.get("error")
            message = f"Failed to retrieve authorization code. Error: {error}"
            raise ValueError(message)
        elif params.get("state") != passthrough_val:
            message = "State token does not match the expected state."
            raise ValueError(message)
        else:
            message = "Authorization code was successfully retrieved."
    except ValueError as error:
        print(error)
        sys.exit(1)
    finally:
        response = ("HTTP/1.1 200 OK\n"
                    "Content-Type: text/html\n\n"
                    f"<b>{message}</b>"
                    "<p>Please go back to your console.</p>\n")
        connection.sendall(response.encode())
        connection.close()
    return params.get("code")


def _parse_raw_query_params(data):
    """Parses a raw HTTP request to extract its query params as a dict.
      Note that this logic is likely irrelevant if you're building OAuth logic
      into a complete web application, where response parsing is handled by a
      framework.
      Args:
          data: raw request data as bytes.
      Returns:
          a dict of query parameter key value pairs.
      """
    # Decode the request into a utf-8 encoded string
    decoded = data.decode("utf-8")
    # Use a regular expression to extract the URL query parameters string
    match = re.search("GET\s\/\?(.*) ", decoded)
    params = match.group(1)
    # Split the parameters to isolate the key/value pairs
    pairs = [pair.split("=") for pair in params.split("&")]
    # Convert pairs to a dict to make it easy to access the values
    return {key: val for key, val in pairs}


def get_config(yaml_path):
    with open(yaml_path, 'r') as f:
        ga_config = yaml.load(f, Loader=yaml.SafeLoader)
    return ga_config
