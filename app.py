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
#import secret_data
from io import BytesIO
from ftplib import FTP


app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

import os
is_prod = os.environ.get('IS_HEROKU', None)

if is_prod:
    port = int(os.environ.get('PORT', 5000))
    ftp_host = os.environ.get('ftpurl')
    ftp_user = os.environ.get('ftpuser')
    ftp_password = os.environ.get('ftppass')
    ftp_data_file_path = './data/ClothData.csv'


def generate_plot(df):
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


def update_csv():
    url = "https://rustoria.co/twitch/api/superlatives/cloth"  # Replace with your actual API URL

    try:
        # Make a request and get JSON data
        json_data = make_request(url)

        if json_data:
            # Extract the information you need from the JSON
            # Replace the following line with your actual data extraction logic
            try:
                now = datetime.datetime.now() 
                with FTP(ftp_host) as ftp:
                    ftp.login(user=ftp_user, passwd=ftp_password)
                    
                    # Download the data file from the FTP server
                    buffer = BytesIO()
                    ftp.retrbinary('RETR ' + ftp_data_file_path, buffer.write)
                    buffer.seek(0)
                    
                    # Read the data directly from the buffer into a DataFrame
                    df = pd.read_csv(buffer, encoding='utf-8')

                    for player_data in json_data:

                        new_row = {'timestamp': now, 'name': player_data["player"]["name"], "team": player_data["player"]["teamName"], "amount": player_data["acquired"]["amount"]}
                        df.loc[len(df.index)] = new_row
                
                    # Convert the DataFrame back to CSV format
                    updated_data = df.to_csv(index=False)
                    
                    # Upload the updated data back to the FTP server
                    ftp.storbinary('STOR ' + ftp_data_file_path, BytesIO(updated_data.encode("utf-8")))

                    logger.info("Data written to CSV successfully.")


            except Exception as e:
                logger.error(f"Error in periodic_task: {str(e)}")

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
    try:
        with FTP(ftp_host) as ftp:
            ftp.login(user=ftp_user, passwd=ftp_password)
            
            # Download the data file from the FTP server
            buffer = BytesIO()
            ftp.retrbinary('RETR ' + ftp_data_file_path, buffer.write)
            buffer.seek(0)
            
            # Read the data directly from the buffer into a DataFrame
            df = pd.read_csv(buffer, encoding='utf-8')
            plot_html = generate_plot(df)
            
            return render_template('index.html', plot_html=plot_html)

    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == '__main__':
    app.run(debug=False)