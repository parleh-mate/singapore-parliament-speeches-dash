# Parleh-mate Dash App

Dash App with visuals for speech data and UI for speech and bill summarizers. Currently hosted on [Render](https://parlehmate.onrender.com/).

## Initialisation

Files which are dependencies, but are not synced:

1. `.env`: Environment file which contains the OpenAI and Zilliz API keys
2. `tokens/gcp_token.json`: JSON file with credentials for the GCP service account. Bigquery read permissions on the Google Cloud Project `singapore-parliament-speeches` is required.

## Installation

```shell
pip install -r requirements.txt
```
