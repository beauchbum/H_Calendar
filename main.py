from flask import Flask, request, redirect, g, render_template, make_response, url_for, session, flash, jsonify
import csv
import os
import numpy as np
import MySQLdb
from datetime import datetime, timedelta

### Running in local environment or deployed with Google App Engine
if os.getenv('SERVER_SOFTWARE', '').startswith('Google App Engine/'):
    pass
else:
    PORT = 8000

app = Flask(__name__)
app.config.update(
    SEND_FILE_MAX_AGE_DEFAULT=3600
)

### Global variables - Used to hold values sent back to server from JavaScript
dates_dict = {}
intervals = []
departure_date = ""
all_dates = []


### Connection specs for CloudSQL database
host = '35.202.134.73'
pw = "hopper_pw"
port = 3306
user = 'root'
name = 'hopper'
CLOUDSQL_PROJECT = "hopper-182321"
CLOUDSQL_INSTANCE = "hopper-182321:us-central1:hopper-sql"

### Function to create SQL connection
def sql_connect():
    conn = MySQLdb.connect(unix_socket='/cloudsql/{}:{}'.format(CLOUDSQL_PROJECT, CLOUDSQL_INSTANCE), user=user,
                           host=host, passwd=pw, db=name)
    return conn


### Main route - handles heavy lifting of grabbing data from SQL and initializing calendar
@app.route("/", methods=["POST", "GET"])
def index():
    ### Holds the pricing intervals for coloring dates [Price1, Price2, Price3, Price4]
    global intervals

    ### Main array to be passed to client when rendering Index.html
    calendar_data = []

    ### Used to map date to month - ex. 2016-10-24 == 'OCT'
    month_dict = {1: "JAN", 2: "FEB", 3: "MAR", 4: "APR", 5: "MAY", 6: "JUN", 7: "JUL", 8: "AUG", 9: "SEP", 10: "OCT",
                  11: "NOV", 12: "DEC"}


    ### Array to hold departure data from SQL
    imported_data = []

    ### Find today's date and then use Python datetime to go back one year
    last_year_date = datetime.now().replace(year=datetime.now().year - 1)

    ### Set calendar bounds - hard coded to Oct. 1 2016 and Sept. 30 2017
    first_date = datetime.strptime("2016-10-01", '%Y-%m-%d').date()
    last_date = datetime.strptime("2017-09-30", '%Y-%m-%d').date()

    ### Create array of all dates in between and including the calendar bounds
    dd = [first_date + timedelta(days=x) for x in range((last_date - first_date).days + 1)]

    ### Connect to CloudSQL and then query to get relevant departure dates and minimum price via group by
    conn = sql_connect()
    cursor = conn.cursor()
    query = "select departure_odate, min(total_usd) from flights where departure_odate>=%s and departure_odate<=%s and received_date<=%s group by departure_odate"
    param = [last_year_date, last_date, last_year_date]
    cursor.execute(query, param)
    sql_departure = cursor.fetchall()

    ### Create combination values of all dates between first/end bounds (dd) then add prices from sql_departure
    i = 0
    j = 0
    while i < len(dd):
        if j < len(sql_departure):
            if dd[i]== sql_departure[j][0]:
                imported_data.append((str(dd[i]), dd[i].weekday(), int(sql_departure[j][1])))
                j += 1
            else:
                imported_data.append((str(dd[i]), dd[i].weekday(), ""))
        else:
            imported_data.append((str(dd[i]), dd[i].weekday(), ""))
        i += 1

    ### Create a list of lists of lists [months[weeks[days]]] that will represent the calendar
    month_list = []
    departure_prices = []
    for i in imported_data:
        dates_dict[i[0]] = []
        all_dates.append(i[0])
        date_split = i[0].split("-")
        if i[-1] != "":
            departure_prices.append(float(i[-1]))
        if date_split[2] == '01':
            if len(month_list) > 0:
                chunks = [month_list[x:x + 7] for x in xrange(0, len(month_list), 7)]
                if len(chunks[-1]) != 7:
                    temp = len(chunks[-1])
                    for j in range(7 - temp):
                        chunks[-1].append("BLANK")
                calendar_data.append(chunks)
            month = int(date_split[1])
            month_list = []

            ### Python's Date.weekday() goes M,T,W,T,F,S,S while calendar is S,M,T,W,T,F,S
            dow = int(i[1])
            if dow == 6:
                dow = 0
            else:
                dow+=1

            ### Insert blanks when necessary to correctly align month start/end dates
            for k in range(0, 7):
                if k == dow:
                    month_list.append(month_dict[month])
                else:
                    month_list.append("")
            for l in range(0, dow):
                month_list.append("BLANK")

        ### If departing flight exists for that date, append price, otherwise append blank
        if i[-1] != "":
            month_list.append((i[0],str(int(date_split[2])),float(i[-1])))
        else:
            month_list.append((i[0],str(int(date_split[2])), i[-1]))

    ### Need to add in the last month as the loop above ends before
    chunks = [month_list[x:x + 7] for x in xrange(0, len(month_list), 7)]
    if len(chunks[-1]) != 7:
        temp = len(chunks[-1])
        for j in range(7 - temp):
            chunks[-1].append("BLANK")
    calendar_data.append(chunks)

    ### Create a dictionary of departure/return flights. Dict[Departure Date] = [(ReturnDate1, Price1), (ReturnDate2, Price2), etc...]
    query = "select departure_odate, return_odate, min(total_usd) from flights where departure_odate>=%s and departure_odate<=%s and received_date<=%s group by departure_odate, return_odate"
    param = [last_year_date, last_date, last_year_date]
    cursor.execute(query, param)
    for row in [(str(x[0]), str(x[1]), int(x[2])) for x in cursor.fetchall()]:
        dates_dict[row[0]].append((row[1], row[2]))

    ### Create the price distribuion. Find the min price as lower bound, then add created interval to get the others
    min = np.min(departure_prices)
    rounded_min = min - (min % 10)
    step = round((np.percentile(departure_prices,75) - min)/4,-1)
    intervals = [int(x*step+rounded_min) for x in range(4)]

    return render_template("index.html", calendar=calendar_data, intervals = intervals)


### Route to handle selecting a departure
### Sets the global "departue_date" for use later
### Finds all possible return dates with the "dates_dict"
@app.route("/selectDeparture", methods=["GET"])
def selectDeparture():
    global departure_date
    date = request.args['date']
    departure_date = date
    return_dates = dates_dict[date]
    return jsonify(return_dates = return_dates)


### Route to handle selecting a return
### Find the dates in between so they can be shaded light blue
@app.route("/selectReturn", methods=["GET"])
def selectReturn():
    return_date = request.args['date']
    start_index = all_dates.index(departure_date)
    end_index = all_dates.index(return_date)
    middle_dates = all_dates[start_index:end_index]

    return jsonify(middle_dates=middle_dates, departure_date=departure_date)


if __name__ == "__main__":
    app.run(debug=True, port=PORT)