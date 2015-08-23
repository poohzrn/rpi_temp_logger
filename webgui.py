#!/usr/bin/env python

import sqlite3
import sys
import cgi
import cgitb


# global variables
speriod=(15*60)-1
dbname='/var/www/tmplog/tempdb2.db'



# print the HTTP header
def printHTTPheader():
    print "Content-type: text/html\n\n"

# print the HTML head section
# arguments are the page title and the table for the chart
def printHTMLHead(title, table):
    print "<head>"
    print "    <title>"
    print title
    print "    </title>"

    print_graph_script(table)

    print "</head>"


# get data from the database
# if an interval is passed, 
# return a list of records from the database
def get_data(interval):
    conn=sqlite3.connect(dbname)
    curs=conn.cursor()
    if interval == None:
        curs.execute("SELECT sensor.sensor_id, timestamp, value FROM sensor,sensor_data")
    else:
         curs.execute("SELECT sensor.sensor_id, timestamp, value FROM sensor,sensor_data WHERE timestamp>datetime('now','-%s hours')" % interval)

    rows=curs.fetchall()
    conn.close()
    return rows
#Get the number of sensors
def getSensorCount():
    conn=sqlite3.connect(dbname)
    curs=conn.cursor()
    curs.execute("select count(DISTINCT sensor.sensor_id) from sensor;")
    rows=curs.fetchone()
    conn.close()
    return int(format((rows[0])))

#get Sensor timestamp and value based on device ID 
def getSensorData(deviceId):
    conn=sqlite3.connect(dbname)
    curs=conn.cursor()
    curs.execute("SELECT timestamp, value FROM sensor_data WHERE sensor_data.sensor_id ='%s'" % deviceId)
    rows=curs.fetchall()
    conn.close()
    devicedata =[]
    for row in rows:
        rowdata =[]
        rowdata.append(str(row[0]))
        rowdata.append(str(row[1]))
        devicedata.append(rowdata)
    return devicedata

#return a list of sensorIds
def getSensorIds():
    conn=sqlite3.connect(dbname)
    curs=conn.cursor()
    sensorIdRow=curs.execute("select DISTINCT sensor.sensor_id from sensor;")
    rows=curs.fetchall()
    conn.close()
    table =[]
    for device in rows:
        table.append(format(str(device[0])))
    return table

#Creates the first item in data array based on #sensors
def getBaseTable(sensorCount):
    baseTable = "['Time',"
    for sensor in range(0,sensorCount-1):
        rowstr="'Sensor{0}',".format(str(sensor+1))
        baseTable += rowstr
    baseTable+="'Sensor{0}'],\n".format(str(sensor+2))
    return baseTable

def createMultiTable():
    sensorCount = getSensorCount()
    basetable=getBaseTable(sensorCount)
    devicedata = []
    for device in getSensorIds():
        devicedata.append(getSensorData(device))

    for d1, d2 in zip(devicedata[0],devicedata[1]):
        basetable+="['{0}',{1},{2}],\n".format(str(d1[0]),str(d1[1]),str(d2[1]))

    basetable+="['{0}',{1},{2}]\n".format(str(d1[0]),str(d1[1]),str(d2[1]))
    print basetable
    return basetable
# convert rows from database into a javascript table
def create_table(rows):
    chart_table=""
    for row in rows[:-1]:
        rowstr="['{0}', {1}],\n".format(str(row[1]),str(row[2]))
        chart_table+=rowstr
    return chart_table

# print the javascript to generate the chart
# pass the table generated from the database info
def print_graph_script(table):

    # google chart snippet
    chart_code="""
    <script type="text/javascript" src="https://www.google.com/jsapi"></script>
    <script type="text/javascript">
      google.load("visualization", "1", {packages:["corechart"]});
      google.setOnLoadCallback(drawChart);
      function drawChart() {
        var data = google.visualization.arrayToDataTable([
          %s
        ]);

        var options = {
          title: 'Temperature'
        };

        var chart = new google.visualization.LineChart(document.getElementById('chart_div'));
        chart.draw(data, options);
      }
    </script>"""
    print chart_code % (table)

# print the div that contains the graph
def show_graph():
    print "<h2>Temperature Chart</h2>"
    print '<div id="chart_div" style="width: 900px; height: 500px;"></div>'


# connect to the db and show some stats
# argument option is the number of hours
def show_stats(interval):
    conn=sqlite3.connect(dbname)
    curs=conn.cursor()

    if not interval:
        interval = str(24)

    curs.execute("SELECT timestamp,max(value) FROM sensor_data WHERE timestamp>datetime('now','-%s hour') AND timestamp<=datetime('now')" % interval)
    rowmax=curs.fetchone()
    rowstrmax="{0}&nbsp&nbsp&nbsp{1}C".format(str(rowmax[0]),str(rowmax[1]))

    curs.execute("SELECT timestamp,min(value) FROM sensor_data WHERE timestamp>datetime('2013-09-19 21:30:02','-%s hour') AND timestamp<=datetime('2013-09-19 21:31:02')" % interval)
    rowmin=curs.fetchone()
    rowstrmin="{0}&nbsp&nbsp&nbsp{1}C".format(str(rowmin[0]),str(rowmin[1]))

    curs.execute("SELECT avg(value) FROM sensor_data WHERE timestamp>datetime('now','-%s hour') AND timestamp<=datetime('now')" % interval)
    rowavg=curs.fetchone()


    print "<hr>"
    print "<h2>Minumum temperature&nbsp</h2>"
    print rowstrmin
    print "<h2>Maximum temperature</h2>"
    print rowstrmax
    print "<h2>Average temperature</h2>"
    print "%.3f" % rowavg+"C"

    print "<hr>"

    print "<h2>In the last hour:</h2>"
    print "<table>"
    print "<tr><td><strong>Date/Time</strong></td><td><strong>Temperature</strong></td></tr>"

    rows=curs.execute("SELECT * FROM sensor_data WHERE timestamp>datetime('new','-1 hour') AND timestamp<=datetime('new')")
    for row in rows:
        rowstr="<tr><td>{0}&emsp;&emsp;</td><td>{1}C</td></tr>".format(str(row[0]),str(row[1]))
        print rowstr
        print "hest"
    print "</table>"

    print "<hr>"

    conn.close()

def print_time_selector(option):

    print """<form action="" method="POST">
        Show the temperature logs for  
        <select name="timeinterval">"""


    if option is not None:

        if option == "6":
            print "<option value=\"6\" selected=\"selected\">the last 6 hours</option>"
        else:
            print "<option value=\"6\">the last 6 hours</option>"

        if option == "12":
            print "<option value=\"12\" selected=\"selected\">the last 12 hours</option>"
        else:
            print "<option value=\"12\">the last 12 hours</option>"

        if option == "24":
            print "<option value=\"24\" selected=\"selected\">the last 24 hours</option>"
        else:
            print "<option value=\"24\">the last 24 hours</option>"

    else:
        print """<option value="6">the last 6 hours</option>
            <option value="12">the last 12 hours</option>
            <option value="24" selected="selected">the last 24 hours</option>"""

    print """        </select>
        <input type="submit" value="Display">
    </form>"""


# check that the option is valid
# and not an SQL injection
def validate_input(option_str):
    # check that the option string represents a number
    if option_str.isalnum():
        # check that the option is within a specific range
        if int(option_str) > 0 and int(option_str) <= 24:
            return option_str
        else:
            return None
    else:
        return None


#return the option passed to the script
def getTimeInterval():
    form=cgi.FieldStorage()
    if "timeinterval" in form:
        option = form["timeinterval"].value
        return validate_input (option)
    else:
        return None

# main function
# This is where the program starts 
def main():

    cgitb.enable()

    # get options that may have been passed to this script
    interval=getTimeInterval()

    if not interval:
        interval= str(24) #24 hour std interval

    # get data from the database
    records=get_data(interval)

    # print the HTTP header
    printHTTPheader()

    if len(records) != 0:
        # convert the data into a table
        table=create_table(records)
    else:
        print "No data found"
        return

    # start printing the page
    print "<html>"
    # print the head section including the table
    # used by the javascript for the chart
    #print createMultiTable()
    printHTMLHead("Raspberry Pi Temperature Logger",createMultiTable())
    #print createMultiTable()
    # print the page body
    print "<body>"
    print "<h1>Raspberry Pi Temperature Logger</h1>"
    print "<hr>"
    print_time_selector(interval)
    show_graph()
    show_stats(interval)
    print "</body>"
    print "</html>"

    sys.stdout.flush()

if __name__=="__main__":
    main()
