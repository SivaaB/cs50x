import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
import datetime
import math

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

# Begin Model-View-Controller Logic
# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

# Make sure API key is set
# export API_KEY=pk_3eb0a1d6b21f468da0d712930549e542
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")

@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    stocks_owned = db.execute("SELECT symbol, SUM(shares) FROM transactions WHERE customer_id == :customer_id GROUP BY symbol",customer_id=session["user_id"])

    print(stocks_owned)

    for i in range(len(stocks_owned)):
        if stocks_owned[i]['SUM(shares)'] == 0:
            del(stocks_owned[i])

    for row in stocks_owned:
        row['name'] = lookup(row['symbol'])['name']
        row['price'] = round(lookup(row['symbol'])['price'], 2)
        row['total'] = round(lookup(row['symbol'])['price'] * row['SUM(shares)'], 2)

    investment_total = 0

    for row in stocks_owned:
        investment_total += row['total']

    investment_total = round(investment_total, 2)

    cash_total = db.execute("SELECT cash FROM users WHERE id == :id", id = session["user_id"] )
    cash = round(float(cash_total[0]['cash']), 2)
    grand_total = round(investment_total + cash, 2)

    return render_template("index.html", stocks_owned=stocks_owned,investment_total=investment_total, cash=cash, grand_total=grand_total)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "GET":
        print(session["user_id"])
        return render_template("buy.html")
    else:
        symbol = request.form.get("symbol")
        if not symbol:
            render_template("apology.html", message="Please enter a stock symbol.")
        get_quote = lookup(symbol)
        if not get_quote:
            return render_template("apology.html", message="No symbol found.")

        shares = request.form.get("shares")
        if not shares:
            return render_template("apology.html", message="Please enter a number of shares.")
        if int(shares) < 0:
            return render_template("apology.html", message="Invalid number of shares.")

        current_price = get_quote["price"]
        amount_due = current_price * int(shares)

        balance = db.execute("SELECT cash FROM users WHERE id == :id", id=session["user_id"])[0]

        if amount_due <= float(balance["cash"]):
            can_buy = True
        else:
            return render_template("apology.html", message="Insufficent funds")

        if can_buy:
            new_cash = float(balance["cash"]) - amount_due
            now = datetime.datetime.now()
            db.execute("UPDATE users SET cash = :cash WHERE id == :id", cash=new_cash, id=session["user_id"])
            db.execute("INSERT INTO transactions (customer_id, date, type, symbol, shares, PPS, Total_Amount) VALUES (:customer_id, :date, :type, :symbol, :shares, :PPS, :Total_Amount)", customer_id=session["user_id"], date=now, type="Buy", symbol=symbol, shares=shares, PPS=current_price, Total_Amount=amount_due)
            return render_template("success.html")


@app.route("/history")
@login_required
def history():
    history = db.execute("SELECT * FROM transactions WHERE customer_id == :customer_id ORDER BY date DESC", customer_id=session["user_id"])
    print(history)
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
    if request.method == "GET":
        return render_template("quote.html")
    else:
        symbol = request.form.get("symbol")
        if not symbol:
            return render_template("apology.html", message="Please enter a stock symbol.")
        get_quote = lookup(symbol)
        if not get_quote:
            return render_template("apology.html", message="No symbol found.")
        name = get_quote["name"]
        price = get_quote["price"]
        return render_template("quoted.html", name=name, symbol=symbol.upper(), price=price)


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "GET":
        return render_template("register.html")
    else:
        username = request.form.get("username")
        password1 = request.form.get("password")
        password2 = request.form.get("confirmation")

        special_symbols = ['!', '#', '$', '%', '.', '_', '&']

        if not username:
            return render_template("apology.html", message="You must provide a username.")

        if not password1:
            return render_template("apology.html", message="You must provide a password.")

        if not password2:
            return render_template("apology.html", message="You must confirm your password.")

        if len(password1) < 8:
            return render_template("apology.html", message="Your password must contain 8 or more characters.")

        if not any(char.isdigit() for char in password1):
            return render_template("apology.html", message="Your password must contain at least 1 number.")

        if not any(char.isupper() for char in password1):
            return render_template("apology.html", message="Your password must contain at least uppercase letter.")

        if not any(char in special_symbols for char in password1):
            return render_template("apology.html", message="Your password must contain at least 1 approved symbol.")

        if password1 == password2:
            password = password1
        else:
            return render_template("apology.html", message="Passwords do not match.")

        p_hash = generate_password_hash(password, method = 'pbkdf2:sha256', salt_length = 8)

        if len(db.execute("SELECT username FROM users WHERE username == :username", username=username)) == 0:
            db.execute("INSERT INTO users (username, hash) VALUES (:username, :hash)", username=username, hash=p_hash)
            return redirect("/")
        else:
            return render_template("apology.html",message="Username already exists. Please enter a new username.")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    if request.method == "GET":
        return render_template("sell.html")
    else:
        symbol = request.form.get("symbol")
        if not symbol:
            render_template("apology.html", message="Please enter a stock symbol.")
        get_quote = lookup(symbol)
        if not get_quote:
            return render_template("apology.html", message="No symbol found.")
        shares = request.form.get("shares")
        if not shares:
            return render_template("apology.html", message="Please enter a number of shares.")
        if int(shares) < 0:
            return render_template("apology.html", message="Invalid number of shares.")

        current_price = get_quote["price"]
        amount_owed = current_price * int(shares)

        stocks_owned = db.execute("SELECT symbol, SUM(shares) FROM transactions WHERE customer_id == :customer_id GROUP BY symbol", customer_id=session["user_id"])
        stocks_dict = {}
        for row in stocks_owned:
            stocks_dict[row['symbol']] = row['SUM(shares)']

        shares_available = stocks_dict[symbol]
        print(shares_available)

        if int(shares) <= int(shares_available):
            balance = db.execute("SELECT cash FROM users WHERE id == :id", id=session["user_id"])[0]
            new_balance = round(balance['cash'] + amount_owed, 2)
            now = datetime.datetime.now()
            db.execute("UPDATE users SET cash = :cash WHERE id == :id", cash=new_balance, id=session["user_id"])
            db.execute("INSERT INTO transactions (customer_id, date, type, symbol, shares, PPS, Total_Amount) VALUES (:customer_id, :date, :type, :symbol, :shares, :PPS, :Total_Amount)", customer_id=session["user_id"], date=now, type="Sell", symbol=symbol, shares = -1 * int(shares), PPS=current_price, Total_Amount= -1 *amount_owed)
            return render_template("success.html")
        else:
            return render_template("apology.html", message="You are attempting to sell more shares than you own.")


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)