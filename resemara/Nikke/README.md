## Requirement

- LDPlayer 9
- Python 3
- Python packages
```
pillow
numpy
opencv-python
google-api-python-client
google-auth-httplib2
google-auth-oauthlib
```

## Installation

1. set your gmail ID, account password, and nickname at `config.py`
2. Follow [this guide](https://developers.google.com/gmail/api/quickstart/python) to enable your GMail API, and get client data json file.
    a. you may need to make new project
3. Rename the json file to `credentials.json`, and place it in the same folder with this file
4. Go to OAuth consent screen tab in the Google Cloud web page, go to Test users section. Press ADD USERS button, and type your gmail address
5. At first run, you will see message: `Please visit this URL to authorize this application: https://accounts.google.com/o/oauth2/auth?response_type=code&client_id=xxxxxxxxxxx-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx.apps.googleusercontent.com&redirect_uri=http%3A%2F%2Flocalhost%3A3755%2F&scope=https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fgmail.readonly&state=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx&access_type=offline`. Go to the link, authorize the app
6. Set your App Player 960 x 540, 240 DPI 
7. Make sure that nikke authentication code mail is not regarded as spam in your GMail

## How to users

Run `main.py`