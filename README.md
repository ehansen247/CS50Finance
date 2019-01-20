# CS50Finance
Website Allowing Users to Buy/Sell Virtual Stocks
## Introduction
This project creates a website that allows user's to register an account and then login to an investment account. Users can buy, sell, and quote actual stocks (the money of course is imagined). Users can also add additional funds to their account, see their transaction history, and view how their portfolio is performing. The website utilizes the IEX Stock API to access  stock prices in real time. This project was developed using Python, HTML/CSS, SQLite, and Flask. This project was developed within Harvard's Introduction to Computer Science course, CS50. I made a few changes after completing the project in the course to make it accessible outside of our course's customized IDE. 

## Flask
The project is built off the Flask's lightweight but simple web framework. The requisite Flask files should be downloaded when the project is cloned but if not, follow the instructions to download Flask here: http://flask.pocoo.org/docs/1.0/installation/. 
You will also need to download the requests and flask_session modules, which are not build-in. 

To download requests (use pip3 instead of pip if necessary):
For OSX/Linux: sudo pip install requests
For Windows: pip install requests

To download flask_session:
pip install flask_session


## SQLite
The project utilized SQLite3 to store registered users' information. To view the database, "finance.db," I would suggest downloading "DB Browser for SQLite." The project comes with a few test users in the database. 

## Running the Project:
To run the website on the local host, change into the CS50Finance directory in the command line, then change into the flask directory, then enter "flask run." In the block below, you will see the homepage url, usually http://127.0.0.1:5000/. 

### Common Exceptions:
#### 1. ModuleNotFoundError: No module named 'requests' or No module named 'flask_session'
Requests and flask_session are not built-in modules in Flask. To download them, consult the directions above under the Flask heading.
#### 2. Error: Could not import "some_string".
Make sure you are in the flask directory within CS50Finance.
For OSX/Linux: export FLASK_APP=app.py
For Windows: set FLASK_APP=app.py
More information if still not working: http://flask.pocoo.org/docs/1.0/cli/
#### 3. If you receive a different error, let me know
