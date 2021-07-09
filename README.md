# IoTube-Analytics
Source code for the IoTube Bridge Analytics dashboard by The Misfits for Grants Round 10 Hackathon by Gitcoin and IoTeX 

Access the application [here](https://iotube-dashboard.herokuapp.com/)

### VIDEO WALKTHROUGHS:

For a detailed video explanation with voice-over, click [here]().

### WHAT IT DOES? 

The analytics dashboard provides an interactive way to monitor flow of funds across bridges in addition to basic network-level statistics. For more detailed insights, statistics can be filtered and viewed according to networks and tokens bridges.

### DATA SOURCES

1. Iotex On-chain data powered by [BigQuery](https://medium.com/iotex/iotex-completes-integration-with-google-bigquery-51bf3b8182f2)
2. Open API by [Covalent](https://www.covalenthq.com/)
3. [IoTeX Scan Analytics](https://analytics.iotexscan.io/) (GraphQL)

### TECHNICAL IMPLEMENTATION

The dashboard follows the UI aesthetic of the bridge web application and due to integration of Bootstrap, it is responsive on mobile and smaller devices.

![Technical framework]()

### Requirements

#### Hardware

* Mac, Linux or Windows (MacOS preffered)
* Atleast 4GB of RAM recommended 

#### Software

* Python 3.7+
* Pip Package Manager

#### Instructions

Clone the GitHub repo on your local machine. Navigate to the project folder in the terminal and run ` pip install -r requirements.txt` to install dependencies. Open the workspace in a code editor of choice and run the `app.py` file. Navigate to `http://127.0.0.1:8050/` (or your default location) in your browser to access alocal version of the dashboard or navigate to `https://iotube-dashboard.herokuapp.com/` to access a live version.

Made with 🤘 by [Simran](https://simmsss.github.io/) and [Utkarsh](https://skhiearth.github.io/)

