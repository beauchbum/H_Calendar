# Hopper Homework Assignment - Methods and Assumptions

## Process and Timeline

#### Friday, Oct. 6

Isabella sent me the homework assignment and corresponding data. 

#### Sunday, Oct. 8

I quarantined myself from NFL football and read through the assignment. I then started a Jupyter Notebook so that I could load the data with Pandas and begin some initial exploration. I verified that all the data was Boston to Cancun - round trip and then identified unique values for various columns and found areas of prevelant NA (refundable being one). 

After formulating an initial strategy, I began to create the HTML/CSS skeleton for the calendar. I mostly finished the skeleton by the end of the day. 

#### Monday, Oct. 9

Made the decision that I would stick to data from Oct. 1 2016 to Sept. 30 2017 as it was much more dense than the data for queries 2017-2018. I used Pandas to peform various GroupBys and min() aggregations to find the cheapest possible flight for each relevant departure date.

Wrote the results to a static .csv file that was then used as an input to the Python code for manipulation. The manipulation created the list of lists of lists that would outline the calendar and be passed to the HTML skeleton. 


#### Tuesday, Oct. 10

Did not have much time to work on the assignment, but I did some tweaks to the styling/layout of the skeleton. Created custom Bootstrap buttons for orange/red and also worked on element padding to avoid being cut off on phones. 


#### Wednesday, Oct. 11

Created .csv file that would outline the possible return dates given a departure date. Worked on pulling that into the python enviornment and building logic to pass data back and forth between Server and Client. 


#### Thursday, Oct. 12


Scrapped the static .csv files and instead uploaded a modified version of the original dataset (kept only relevant columns) to a Google CloudSQL database. Altered the Python logic to query from SQL rather than read in .csv. 


## Design Decisions

#### Price Intervals

Created the intervals by subtracting the minimum price from the 75th percentile price and then dividing by four. There was no mathematical basis for this, but it was the result of some tinkering to arrive at intervals that I believed were in line with Hopper's design.

Note - Intervals do not update after selecting departure date. This may have been useful for more granularity in comparing return dates, but I also thought it would add confusion. 

#### CSV vs SQL

Quickly found out that the file was too big to be loaded each time the prototype was started. For that reason I gravitated towards creating compacted CSV files and presenting it as "This is a static calender as if it is Oct. 8, 2016". However, I had some extra time on Thursday to upload to SQL and realized I could make the calendar dynamic by doing Group Bys in the query rather than in Python. 

#### Round Trip vs. One Way

Did not attempt to tease out any one way prices based on the various round trip flights. While this is probably not true to real life, I operated under the assumption that flights could only be purchased as a package. This limited the possible return dates given a selected departure date. 

#### 2016-2017 Data

As mentioned above, I found the 2016-2017 data to have much more information and thought it would lend itself better to filling in the calendar. The application takes today's date and subtracts a year so that it operates in 2016. 

#### Received Date

When determining departure/return prices, the application filters out any information with a received_date in the future. For example if it is Oct. 12, the app will not consider any rows with received_date of Oct. 13 or more. 

I did not take into consideration the received_ms even though in production this would be a constraint. 

#### Booking Flights

I added a popup box to display the price of the flight. Ideally, this would have other features included in Hopper such as the selling airline, the # of stops, checked bags cost, and the prediction of future flight price. However, I chose not to include any of this as the data was eitehr unavailable or I thought it would add too much complexity given time constraints. 


