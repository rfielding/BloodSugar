import io
import time
import re
import math

#An FSM to handle the quotes correctly
def parseLine(f):
  columns = []
  cell = []
  c = f.read(1)
  isQuoting = False
  while True:
    if len(c) == 0:
      return columns
    if isQuoting:
      if c== '\"':
        isQuoting = False
      else:
        columns.append("".join(cell))
    else:
      if c == '\n':
        columns.append("".join(cell))
        cell = []
        return columns
      elif c == ',':
        columns.append("".join(cell))
        cell = []
      elif c == '\"':
        isQuoting = True
      else:
        cell.append(c)
    c = f.read(1)
  
#Ignore the top of the file.  I have no idea what rules they
#use to determine when records start(!), so I use line count 
def headerParse(f):
  cols = parseLine(f)
  cols = parseLine(f)
  cols = parseLine(f)
  cols = parseLine(f)
  cols = parseLine(f)
  cols = parseLine(f)
  cols = parseLine(f)
  cols = parseLine(f)
  cols = parseLine(f)
  cols = parseLine(f)
  parsed["names"] = parseLine(f)
  dateRange = parseLine(f)

#Medtronic dates have 1 digit months and days, so this is simpler
#Generate a lexically sortable date ffs...
def genDate(s):
    m = parsed["re"].match(s).groups()
    ts = ("%02d/%02d/%02d %02d:%02d:%02d") % (int(m[2]), int(m[1]), int(m[0]), int(m[3]), int(m[4]), int(m[5]))
    return ts

def nvPair(ts, col, cols):
  colName = parsed["names"][col]
  colVal  = cols[col]
  print ts + " " + str(col) + ":" + colName+": "+colVal

def handleBolusWizardUsed(ts,col, cols):
    #nvPair(ts, 0, cols)  
    #nvPair(ts, 18, cols)  
    #nvPair(ts, 19, cols)  
    #nvPair(ts, 21, cols)  
    #nvPair(ts, 22, cols)  
    nvPair(ts, 23, cols)  
    nvPair(ts, 24, cols)  
    parsed["lastwiz"] = ts
    parsed["insulin"] = float(cols[18])
    parsed["lastbg"] = int(cols[19])
    parsed["cir"] = int(cols[21])
    parsed["sir"] = int(cols[22])
    parsed["carb"] = int(cols[23])
    parsed["bgw"] = int(cols[24])

def handleMeterReading(ts, col, cols):
    nvPair(ts, 5, cols)
    parsed["bg"] = int(cols[5])
    if "bgw" in parsed and parsed["bgw"] > 0 and "carb" in parsed and parsed["carb"] > 0:
      wrong = parsed["bg"] - parsed["bgw"]
      actual = parsed["cir"] * parsed["insulin"] + parsed["cir"] * (1.0 * wrong) / parsed["sir"]
      actualerrf = float(actual - parsed["carb"])/actual
      actualerr = int( 100 * actualerrf )
      if not ( parsed["sumcount"] in parsed["carberr"]):
        parsed["carberr"][ parsed["sumcount"] ] = 0 
      parsed["carberr"][ parsed["sumcount"] ] = parsed["carberr"][ parsed["sumcount"] ] + actualerrf
      parsed["sumcount"] = parsed["sumcount"] + 1
      print parsed["lastwiz"] + " -1:actualfood: " + str(actual)
      print parsed["lastwiz"] + " -1:actualerr: " + str(actualerr) + "%"
      del(parsed["bgw"])
  
def parseEvent(ts, col, cols, colName, colVal):
  #On a wizard estimate, take note of what it says for all parms
  if col==5:
    handleMeterReading(ts, col, cols)
  if col==18:
    handleBolusWizardUsed(ts, col, cols)
 
#Generate an event for each column type 
def parseRow(f):
  cols = parseLine(f)
  if len(cols) > 2:
    ts = genDate(cols[1] + " " + cols[2])
    col = 0
    while col < len(cols) and col < len(parsed["names"]):
      colName = parsed["names"][col]
      colVal  = cols[col]
      if colVal:
        parseEvent(ts, col, cols, colName, colVal)
      col = col + 1
  return cols

#Parse a medtronic file 
def medtronicParse(inFile):
  f = open(inFile, "r")
  headerParse(f)
  row = parseRow(f)
  while row:
    row = parseRow(f)
  f.close()

#A shaky stand-in until I get better stats ideas
def statsReport():
  C = parsed["sumcount"]
  total = 0.0
  i = 0
  while i < C:
    total = total + parsed["carberr"][i]
    i = i + 1
  mean = total/C
  total = 0
  i = 0
  while i < C:
    d = parsed["carberr"][i] - mean
    total = total + d*d
    i = i + 1
  variance = total/C
  stddev = math.sqrt(variance)
  print "mean   carb pct error: " + str(mean)
  print "stddev carb pct error: " + str(stddev)

parsed = {}
parsed["sumcount"] = 0
parsed["carberr"] = {}
parsed["re"] = re.compile('^(\d{1,2})/(\d{1,2})/(\d{2}) (\d{2}):(\d{2}):(\d{2})')


medtronicParse("data.csv")
statsReport()

