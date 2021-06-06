# finance

This app syncs your transactions from your banks accounts into a Google Spreadsheet inside a Google Drive.

Currently only Nubank is synced.

## Getting started

## Prerequisites

This project uses Python 3.9+, make sure you have a valid Python version available.

* [poetry (dependency management)](https://python-poetry.org/docs/)
  ```sh
  curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python3 -
  ```
* Install dependencies
  ```sh
  make install
  ```
  
To run the script:

  ```sh
  poetry run python finance/main.py
  ```

You must define the following environment variables:

```yaml
GOOGLE_SPREADSHEET_KEY: 'CHANGEME'
NUBANK_CPF: 'CHANGEME'
NUBANK_PASSWORD: 'CHANGEME'
GCP_BUCKET_PROJECT: 'CHANGEME'
GCP_BUCKET_NAME: 'CHANGEME'
```

You can run the project with Docker too:

  ```sh
  docker build -t finance .
  docker run --rm -ti -e GOOGLE_SPREADSHEET_KEY='' -e NUBANK_CPF='' \
  -e NUBANK_PASSWORD='' -e GCP_BUCKET_PROJECT='' \
  -e GCP_BUCKET_NAME='' finance

