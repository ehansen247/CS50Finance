# Eric Hansen
# Credit to https://stackoverflow.com/questions/13890935/does-pythons-time-time-return-the-local-or-utc-timestamp
# for supplying code to print the current timestamp

import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
import datetime
from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""

    # Gets the current, logged-in user's id
    user_id = session["user_id"]

    # Returns the current user as a list of elements
    user = db.execute("SELECT * FROM users WHERE id == :user_id", user_id=user_id)
    cash = usd(user[0]["cash"])

    # Returns the shares (symbol, name, and number) of the current user
    shares = db.execute("SELECT * FROM shares WHERE user_id == :user_id", user_id=user_id)

    # Creates a list of dictionaries that will form rows in homepage table
    # Each dictionary contains the stock symbol, stock name, stock price, number of shares, and total cost
    portfolio = []
    total = user[0]['cash']
    for share in shares:

        # Finds the price of the given stock given the symbol
        price = lookup(share["symbol"])['price']

        # Calculates total cost of the shares
        shareCost = price * share['number']

        # Incrememnts the total value of the user's portfolio
        total += shareCost

        # Formats these values into US dollars
        f_shareCost = usd(shareCost)
        f_price = usd(price)

        # Adds the dictionary to the portfolio list
        portfolio.append({'price': f_price, 'shareCost': f_shareCost, 'number': share['number'],
                          'symbol': share['symbol'], 'name': share['name']})

    # Formats the total value into US dollars
    total = usd(total)

    # Renders the homepage
    return render_template("index.html", cash=cash, portfolio=portfolio, total=total)


@app.route("/add", methods=["GET", "POST"])
@login_required
def add():
    """Add cash to user's account"""

    # Renders the add page if a GET request
    if request.method == "GET":
        return render_template("add.html")

    # Current logged-in user
    user = session['user_id']

    # Retrieves the added cash
    add = request.form.get("added-cash")

    # Ensures a valid number was inputted
    if not add.isdigit():
        return apology("Invalid cash amount")

    # Converts add to a float, ensures it does not exceed maximum of 1000
    add = float(add)
    if add > 1000:
        return apology("Invalid cash amount")

    # Updates the user's current cash
    cash = db.execute("SELECT cash FROM users WHERE id == :user", user=user)
    new_cash = cash[0]['cash'] + add
    db.execute("UPDATE users SET cash = :new_cash WHERE id == :user", new_cash=new_cash, user=user)

    # Redirects user to homepage
    return redirect("/")


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""

    # Renders buy page if GET request
    if request.method == "GET":
        return render_template("buy.html")

    # If the user's input was not a valid stock abbreviation, redirects to an error page
    quote = lookup(request.form.get('symbol'))
    if quote == None:
        return apology("Invalid Symbol")

    # Initializes variables using data from post form request and the lookup function
    price = quote['price']
    f_price = usd(price)
    num = request.form.get('shares')
    user = session["user_id"]
    symbol = quote["symbol"]

    # Checks if a positive number has been submitted
    if not num.isdigit():
        return apology("Invalid number of shares")
    num = float(num)

    # Retrieves the current cash and calculates the user's cash after the transaction
    cash = db.execute("SELECT cash FROM users WHERE id == :user", user=user)
    new_cash = cash[0]['cash'] - (quote["price"] * num)

    # If there isn't enough cash for the purchase, redirects to an error page
    if new_cash < 0:
        return apology("Insufficient funds for this transaction")

    # Updates the shares table to reflect new purchase
    rows = db.execute("SELECT * FROM shares WHERE user_id == :user AND symbol == :symbol", user=user, symbol=symbol)
    if len(rows) == 0:
        db.execute("INSERT into shares (user_id, symbol, name, number) VALUES(:user, :symbol, :name, :num)",
                   user=user, symbol=symbol, name=quote["name"], num=num)
    else:
        new_num = rows[0]["number"] + num
        db.execute("UPDATE shares SET number = :new_num", new_num=new_num)

    # Updates the users table to reflect cash after purchase
    db.execute("UPDATE users SET cash = :new_cash WHERE id == :user", new_cash=new_cash, user=user)

    # Updates the transaction history table
    timestamp = str(datetime.datetime.now()).split('.')[0]
    db.execute("INSERT INTO history (user_id, symbol, number, price, timestamp) VALUES(:user_id, :symbol, :number, :price, :timestamp)",
               user_id=user, symbol=symbol, number=num, price=f_price, timestamp=timestamp)

    # Redirects user to homepage
    return redirect("/")


# Checks for a valid username
@app.route("/check", methods=["GET"])
def check():
    """Return true if username available, else false, in JSON format"""

    # Retrieves the inputted username from the register form
    username = request.args.get("username")

    # If user name available returns true
    if len(username) >= 1 and len(db.execute("SELECT * FROM users WHERE username = :username", username=username)) == 0:
        return jsonify(True)

    # Otherwise, returns false
    return jsonify(False)


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""

    # Acceses the history database
    history = db.execute("SELECT * FROM history")

    # Renders the history page
    return render_template("history.html", history=history)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""

    # Renders the quote page if a GET request
    if request.method == "GET":
        return render_template("quote.html")

    # Checks if the stock symbol exists
    quote = lookup(request.form.get("symbol"))
    if quote == None:
        return apology("Invalid Symbol")

    # Retrieves and formats the price of the stock
    price = usd(quote['price'])

    # Renders the quoted page
    return render_template("quoted.html", name=quote['name'], price=price, symbol=quote['symbol'])


@app.route("/register", methods=["GET", "POST"])
def register():
    """Registers new users"""

    # Renders the register page if GET request
    if request.method == "GET":
        return render_template("register.html")

    # Checks if the user inputted a username
    username = request.form.get("username")
    if not username:
        return apology("Please enter a username")

    # Checks if the username already exists
    if len(db.execute("SELECT * FROM users WHERE username = :username", username=username)) != 0:
        return apology("That username already exists. Please enter a different username")

    # Checks if the passwords are the same and if the passwords were inputted
    password = request.form.get("password")
    confirmation = request.form.get("confirmation")
    if not password or not confirmation:
        return apology("Please enter both passwords")
    if password != confirmation:
        return apology("Please enter passwords that match")

    # Hashes the password
    phash = generate_password_hash(password)

    # Stores the new user in the user database
    db.execute("INSERT INTO users (username, hash) VALUES(:username, :phash)", username=username, phash=phash)

    # Renders the success page
    return render_template("success.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sells shares of owned stocks"""

    # Current, logged-in user
    user_id = session['user_id']

    # If a get request, renders the sell form
    if request.method == "GET":
        stocks = db.execute("SELECT symbol FROM shares WHERE user_id == :user_id", user_id=user_id)
        return render_template("sell.html", stocks=stocks)

    # Initializes variables with data from the form request and from the shares table
    symbol = request.form.get('symbol')
    sell_num = request.form.get('shares')
    cur_num = db.execute("SELECT number FROM shares WHERE user_id == :user_id AND symbol == :symbol",
                         user_id=user_id, symbol=symbol)[0]['number']

    # Ensures a valid number was inputted
    if not sell_num.isdigit():
        return apology("Invalid number of shares")
    sell_num = float(sell_num)

    # New number of shares
    new_num = cur_num - sell_num

    # Checks if the user has enough shares to make the transaction
    if sell_num > cur_num:
        return apology("You do not have that many shares of that stock")
    if sell_num <= 0:
        return apology("Please enter a positive number")

    # Retrieves the current cash of the user
    cash = db.execute("SELECT cash FROM users WHERE id == :user_id", user_id=user_id)[0]['cash']

    # Retrieves and formats the price of the stock
    price = lookup(symbol)['price']
    f_price = usd(price)

    # Calculates the new cash amount in the user's account and updates the user database
    new_cash = cash + sell_num * price
    db.execute("UPDATE users SET cash = :new_cash WHERE id == :user_id", new_cash=new_cash, user_id=user_id)

    # Updates the shares table to reflect sold shares
    if sell_num == cur_num:
        db.execute("DELETE FROM shares WHERE user_id == :user_id AND symbol == :symbol", user_id=user_id, symbol=symbol)
    else:
        db.execute("UPDATE shares SET number = :num WHERE user_id == :user_id AND symbol == :symbol",
                   num=new_num, user_id=user_id, symbol=symbol)

    # Updates the transaction history table
    timestamp = str(datetime.datetime.now()).split('.')[0]
    db.execute("INSERT INTO history (user_id, symbol, number, price, timestamp) VALUES(:user_id, :symbol, :number, :price, :timestamp)",
               user_id=user_id, symbol=symbol, number=-sell_num, price=f_price, timestamp=timestamp)

    # Redirects user to homepage
    return redirect("/")


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
