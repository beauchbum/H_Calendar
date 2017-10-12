from flask import Flask, request, redirect, g, render_template, make_response, url_for, session, flash, jsonify
import csv
import os
import numpy as np


if os.getenv('SERVER_SOFTWARE', '').startswith('Google App Engine/'):
    pass
else:
    PORT = 8000

app = Flask(__name__)
app.config.update(
    SEND_FILE_MAX_AGE_DEFAULT=3600
)

dates_dict = {}
intervals = []
departure_date = ""
all_dates = []



@app.route("/", methods=["POST", "GET"])
def index():
    global intervals
    calendar_data = []
    month_dict = {1: "JAN", 2: "FEB", 3: "MAR", 4: "APR", 5: "MAY", 6: "JUN", 7: "JUL", 8: "AUG", 9: "SEP", 10: "OCT",
                  11: "NOV", 12: "DEC"}

    imported_data = []
    rt_imported_data = []

    with open('departure_data.csv', 'rb') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
        spamreader.next()
        for row in spamreader:
            imported_data.append(row)


    # Create the calendar with departure prices
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
            dow = int(i[1])

            for k in range(0, 7):
                if (k - 1) == dow:
                    month_list.append(month_dict[month])
                else:
                    month_list.append("")
            for l in range(0, dow + 1):
                month_list.append("BLANK")
        if i[-1] != "":
            month_list.append((i[0],str(int(date_split[2])),float(i[-1])))
        else:
            month_list.append((i[0],str(int(date_split[2])), i[-1]))

    # Need to add in the last month
    chunks = [month_list[x:x + 7] for x in xrange(0, len(month_list), 7)]
    if len(chunks[-1]) != 7:
        temp = len(chunks[-1])
        for j in range(7 - temp):
            chunks[-1].append("BLANK")
    calendar_data.append(chunks)

    with open('round_trip_data.csv', 'rb') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
        spamreader.next()
        for row in spamreader:
            dates_dict[row[0]].append((row[1],row[2]))


    # Create price distribution
    min = np.min(departure_prices)
    rounded_min = min - (min % 10)
    median = np.median(departure_prices)
    max = np.max(departure_prices)
    step = round((np.percentile(departure_prices,75) - min)/4,-1)
    intervals = [int(x*step+rounded_min) for x in range(4)]

    return render_template("index.html", calendar=calendar_data, intervals = intervals)

@app.route("/selectDeparture", methods=["GET"])
def selectDeparture():
    global departure_date
    date = request.args['date']
    departure_date = date
    return_dates = dates_dict[date]
    return jsonify(return_dates = return_dates)

@app.route("/selectReturn", methods=["GET"])
def selectReturn():
    return_date = request.args['date']
    start_index = all_dates.index(departure_date)
    end_index = all_dates.index(return_date)
    middle_dates = all_dates[start_index:end_index]

    return jsonify(middle_dates=middle_dates, departure_date=departure_date)


if __name__ == "__main__":
    app.run(debug=True, port=PORT)