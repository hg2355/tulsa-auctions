import os
import json
import csv
import requests
import pandas as pd
from dagster import op, job
from google.cloud import storage
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "key.json"


@op
def auction_data():
    # get the data
    json_object = json.dumps(requests.get(
        "https://www.tinstar.io/api/cases").json())
    with open("input_file.json", "w") as input_file:
        input_file.write(json_object)

    # turn data to csv file
    with open("input_file.json") as input:
        df = pd.read_json(input)

    csv_file = df.to_csv('csvfile.csv', encoding='utf-8', index=False)
    with open('csvfile.csv') as csvfile:
        reader = csv.DictReader(csvfile)
        for i, row in enumerate(reader):
            print(row)
            if(i >= 1):
                break

    # upload file to google cloud storage
    storage_client = storage.Client()
    bucket = storage_client.get_bucket("tulsa-auction-data")
    blob = bucket.blob("data-from-tinstar.io/api/cases")
    blob.upload_from_filename("csvfile.csv")


@ job
def get_data():
    auction_data()
