import requests
import csv
import time
import datetime
import json

def make_request(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return None

def write_to_csv(data, csv_file):
    with open(csv_file, 'a', newline='') as csvfile:
        fieldnames = data.keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        # Check if it's the first time writing to the CSV
        if csvfile.tell() == 0:
            writer.writeheader()

        writer.writerow(data)

def main():
    url = "https://rustoria.co/twitch/api/superlatives/cloth"  # Replace with your actual API URL
    csv_file = "data.csv"  # Replace with your desired CSV file name

    while True:
        try:
            # Make a request and get JSON data
            json_data = make_request(url)

            if json_data:
                # Extract the information you need from the JSON
                # Replace the following line with your actual data extraction logic
                now = datetime.datetime.now() 

                for player_data in json_data:
                    relevant_info = {'timestamp': now, 'name': player_data["player"]["name"], "team": player_data["player"]["teamName"], "amount": player_data["acquired"]["amount"]}
                    write_to_csv(relevant_info, csv_file)
                # Write the relevant information to the CSV file
                

                print("Data written to CSV successfully.")

            else:
                print("Failed to get data from the API.")

            # Wait for one minute before making the next request
            time.sleep(20)

        except Exception as e:
            print(f"An error occurred: {str(e)}")