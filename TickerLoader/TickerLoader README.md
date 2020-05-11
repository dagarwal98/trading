# Introduction

The ticker loader program fetches daily stock price data from Alpha Vantage website and saves them to MySQL database. The following sections show you how to setup the program and other related tools on Windows.

# Components Used
* Python
* Anaconda
* MySQL Database
* Alpha Vantage data provider

# Installation Steps
1. Python
Download and install Python 3 from https://www.python.org/downloads/. The version I have used is 3.6.4. You may try any version 3.

2. Anaconda
Download and install Anaconda from https://www.anaconda.com/products/individual.

3. MySQL database
Download and install MySQL from https://downloads.mysql.com/archives/installer/. I am using version 5.7.21. You may try newer versions.

4. Alpha Vantage
Alpha Vantage is a free online provider of realtime and historic stock data. You need to get a free API key from the site: https://www.alphavantage.co/support/#api-key.

5. Create Anaconda environment
conda create -n tickerloader python=3.6
conda activate tickerloader

    You may use any environment name of your choice.

6. Install python modules
conda install jupyter

    pip install --user --requirement requirements.txt

    requirements.txt has the list of modules required by this program.

7. Configure Database
   - Connect to MySQL:
      <br/>mysql -u username -p

      CREATE DATABASE TradingDB;

   - Launch MySQL Workbench
    - Connect to TradingDB
    - Execute script: sp_createTable
    - Create a user that will be used from Python program to connect to mysql
    - Grant privileges: SELECT, INSERT, UPDATE, DELETE, EXECUTE, DROP

8. Setup environment variables
   - ALPHA_VANTAGE_KEY
   - mysql_user
   - mysql_user_password

9.  Copy file ticker_load_to_mysql.ipynb in a folder.

10. Edit file tickers.csv and add stock tickers of your choice.

11. Launch Jupyter: jupyter notebook

12. You can run the program and make any change you may want.

# Schedule Ticker loader
You can use windows task scheduler to run the program every day at a certain time to download stock data and update database with the latest information.

1. Copy ticker_load_to_mysql_utility.py file into the folder. This file has the same information as in the ipynb file but organized differently so that it can be run on its own.

2.  Create a task to run every day in the evening after trading hours to get the stock data for the day.
   - There are several videos on youtube to guide you how to create a scheduler. One video I found useful is: https://www.youtube.com/watch?v=n2Cr_YRQk7o

Hope the above information helps you in running the program. If you need my help, please email: rajagarwal@hotmail.com.
 
