from flask import Flask, render_template
import pandas as pd
import plotly.express as px
import time
import datetime
import logging
import csv
import requests
import json
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

ftp_host = 'ftp.byethost3.com'
ftp_user = 'b3_35614922'
ftp_password = 'your_ftp_password'
ftp_data_file_path = '/path/to/your/data_file.csv'

def generate_plot():
    data = "./data/data.csv"

    df = pd.read_csv(data, parse_dates=['timestamp'])

    # Use Plotly Express to create an interactive line chart
    fig = px.line(df, x='timestamp', y='amount', color='name', title='Amount Over Time')
    fig.update_layout(xaxis_title='Timestamp', yaxis_title='Amount')

    # Convert the plot to HTML and remove the outer <div>
    plot_html = fig.to_html(full_html=False)

    return plot_html

# Example function to be run periodically
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

def update_csv():
    url = "https://rustoria.co/twitch/api/superlatives/cloth"  # Replace with your actual API URL
    csv_file = "./data/data.csv"  # Replace with your desired CSV file name

    

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
            

            logger.info("Data written to CSV successfully.")

        else:
            logger.info("Failed to get data from the API.")

        # Wait for one minute before making the next request


    except Exception as e:
        logger.info(f"An error occurred: {str(e)}")

# Start the periodic task in a background thread
scheduler = BackgroundScheduler(daemon=True)
scheduler.add_job(update_csv, 'interval', seconds=30)
scheduler.start()


@app.route('/')
def index():
    plot_html = generate_plot()
    return render_template('index.html', plot_html=plot_html)

if __name__ == '__main__':
    app.run(debug=True)