# !/usr/bin/python
import os
import sys
import MySQLdb
import re
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
mysqlCN = 'host'
mysqlID = 'user'
mysqlPW = 'pw'
mysqlDB = 'db'

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(APP_ROOT, 'static/pictures')
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route("/")
def data():
	error = None
	temperature = 0
	humidity = 0
	db = MySQLdb.connect(mysqlCN, mysqlID, mysqlPW, mysqlDB)
	cursor = db.cursor()
	getRecord = "SELECT * FROM humidor_now WHERE id=1"
	try:
		cursor.execute(getRecord)
		result = cursor.fetchall()
		for row in result:
			temperature = row[1]
			humidity = row[2]
	except (MySQLdb.Error, MySQLdb.Warning) as e:
		print("SQL ERROR - get humidor_now - dataDisplay.html")
		error = "Error Loading SQL Data.  Contact IT if the problem continues."
	db.close()

	print("rendering main")
	return render_template("dataDisplay.html", error=error, temperature=temperature, humidity=humidity)
	

@app.route("/cigars")
def cigars():
	error = None
	ids = []
	name = []
	qty = []
	maker = []
	ring = []
	length = []
	purchased = []
	seller = []
	picture = []
	length2 = 0

	#get the sql data
	db = MySQLdb.connect(mysqlCN, mysqlID, mysqlPW, mysqlDB)
	cursor = db.cursor()
	getAll = "SELECT * FROM cigar;"
	try:
		cursor.execute(getAll)
		result = cursor.fetchall()
		for row in result:
			ids.append(str(row[0]))
			name.append(row[1])
			qty.append(str(row[2]))
			maker.append(row[3])
			ring.append(str(row[4]))
			length.append(str(row[5]))
			purchased.append(str(row[6]))
			seller.append(row[7])
			picture.append(row[8])
			length2 += 1
	except (MySQLdb.Error, MySQLdb.Warning) as e:
		print("SQL ERROR - get humidor_now - dataDisplay.html")
		error = "Error Loading SQL Data.  Contact IT if the problem continues."
	db.close()
	print(picture)
	return render_template("cigars.html", error=error, length2=length2, ids=ids, name=name, qty=qty, maker=maker, ring=ring, length=length, purchased=purchased, seller=seller, picture=picture)
	

@app.route("/addcigar", methods=["GET","POST"])
def addcigar():
	error = None
	#get the data from POST
	if request.method == 'POST':
		print("Adding Cigar")
		filename = ""
		try:
			file = request.files['name-photo']
			filename = secure_filename(file.filename)
		except:
			filename = "defaultcigar.png"
		print(filename)

		try:
			newName = removeSpecial(request.form['name-name'])
			newQty = int(removeSpecial(request.form['name-qty']))
			newMaker = removeSpecial(request.form['name-maker'])
			newRing = int(removeSpecial(request.form['name-ring']))
			newLength = int(removeSpecial(request.form['name-length']))
			newSeller = removeSpecial(request.form['name-seller'])
			newPhoto = filename
			if filename != 'defaultcigar.png' and allowed_file(file.filename):
				print("attempting save")
				print(UPLOAD_FOLDER)
				file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
				print("saved")
				newPhoto = filename
			addSQL = """INSERT INTO cigar VALUES(NULL, '{0}', {1}, '{2}', {3}, {4}, NOW(), '{5}','{6}'); """.format(newName, newQty, newMaker, newRing, newLength, newSeller, newPhoto)
			
			print(addSQL)
			db = MySQLdb.connect(mysqlCN, mysqlID, mysqlPW, mysqlDB)
			cursor = db.cursor()

			try:
				cursor.execute(addSQL)
				db.commit()
			except (MySQLdb.Error, MySQLdb.Warning) as e:
				print("SQL ERROR - insert new cigar - addcigar.html")
				error = "Error inserting SQL Data.  Contact IT if the problem continues."
				return render_template("addcigar.html", error=error)

			db.close()
			return redirect('/cigars')
		except:
			print("Form Data Error - addcigar.html")
			error = "Form Data Error.  Please ensure proper data input."

	return render_template("addcigar.html", error=error)


@app.route("/events")
def events():
	error = None
	ids = []
	entered = []
	location = []
	cigar = []
	cigarName = []
	participant1 = []
	participant2 = []
	pairing = []
	rating = []
	picture = []
	length = 0

	#get the sql data
	db = MySQLdb.connect(mysqlCN, mysqlID, mysqlPW, mysqlDB)
	cursor = db.cursor()
	#get cigar info
	getAll = "SELECT * FROM cigar;"
	try:
		cursor.execute(getAll)
		result = cursor.fetchall()
		for row in result:
			cigarName.append(row[1])
	except (MySQLdb.Error, MySQLdb.Warning) as e:
		print ("SQL ERROR - get cigars - events.html")
		error = "Error getting SQL Data.  Contact IT if the problem continues."
	#get event info
	getAll = "SELECT * FROM event;"
	try:
		cursor.execute(getAll)
		result = cursor.fetchall()
		for row in result:
			ids.append(str(row[0]))
			entered.append(str(row[1]))
			location.append(row[2])
			cigar.append(str(row[3]))
			participant1.append(row[4])
			participant2.append(row[5])
			pairing.append(row[9])
			rating.append(str(row[10]))
			picture.append(row[11])
			length += 1
	except (MySQLdb.Error, MySQLdb.Warning) as e:
		print ("SQL ERROR - get events - events.html")
		error = "Error getting SQL Data.  Contact IT if the problem continues."
	db.close()
	return render_template("event.html", error=error, ids=ids, entered=entered, location=location, cigar=cigar, participant1=participant1, participant2=participant2, pairing=pairing, rating=rating, picture=picture, cigarName=cigarName, length=length)
	
@app.route("/addevent", methods=["GET","POST"])
def addevent():
	error = None
	#get the data from POST
	if request.method == 'POST':
		print("Adding Smoke")
		filename = ""
		try:
			file = request.files['name-photo']
			filename = secure_filename(file.filename)
		except:
			filename = "defaultevent.png"
		print(filename)

		newLocation = removeSpecial(request.form['name-location'])
		newCigar = int(removeSpecial(request.form['name-cigar']))
		newPart1 = removeSpecial(request.form['name-part1'])
		newPart2 = removeSpecial(request.form['name-part2'])
		newPairing = removeSpecial(request.form['name-pairing'])
		newRating = int(removeSpecial(request.form['name-rating']))
		newPhoto = filename
		if filename != 'defaultevent.png' and allowed_file(file.filename):
				print("attempting save")
				print(UPLOAD_FOLDER)
				file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
				print("saved")
				newPhoto = filename
		addSQL = """INSERT INTO event VALUES(NULL, NOW(), '{0}', {1}, '{2}', '{3}', 'none', 'none','none', '{4}', {5}, '{6}'); """.format(newLocation, newCigar, newPart1, newPart2, newPairing, newRating, newPhoto)
		
		print(addSQL)
		db = MySQLdb.connect(mysqlCN, mysqlID, mysqlPW, mysqlDB)
		cursor = db.cursor()

		try:
			cursor.execute(addSQL)
			db.commit()
		except (MySQLdb.Error, MySQLdb.Warning) as e:
			print("SQL ERROR - inserting event - addevent.html")
			error = "Error inserting SQL Data.  Contact IT if the problem continues."
			return render_template("addevent.html", error=error)

		#reduce the quatity of the used cigar by one
		#get the cigar record to get he quantity
		getCigar = """SELECT qty FROM cigar WHERE id = {0};""".format(newCigar)
		cigarQuantity = 0
		try:
			cursor.execute(getCigar)
			result = cursor.fetchall()
			for row in result:
				cigarQuantity = row[0]
				#reduce by one
				cigarQuantity = cigarQuantity - 1
		except (MySQLdb.Error, MySQLdb.Warning) as e:
			print ("SQL ERROR - get cigars - addevent.html")
			error = "Error getting SQL Data.  Contact IT if the problem continues."
			return render_template("addevent.html", error=error)
		#update the record with the new quantity
		setCigar = """UPDATE cigar SET qty={0} WHERE id={1};""".format(cigarQuantity, newCigar)
		try:
			cursor.execute(setCigar)
			db.commit()
		except(MySQLdb.Error, MySQLdb.Warning) as e:
			print ("SQL ERROR - update cigar qty - addevent.html")
			error = "Error updating SQL Data.  Contact IT if the problem continues."
			return render_template("addevent.html", error=error)

		db.close()
		return redirect('/events')

	#get data to populate cigar drop down
	ids = []
	name = []
	qty = []
	length = 0
	#get the sql data
	db = MySQLdb.connect(mysqlCN, mysqlID, mysqlPW, mysqlDB)
	cursor = db.cursor()
	getAll = "SELECT * FROM cigar;"
	try:
		cursor.execute(getAll)
		result = cursor.fetchall()
		for row in result:
			ids.append(str(row[0]))
			name.append(row[1])
			qty.append(str(row[2]))
			length += 1
	except (MySQLdb.Error, MySQLdb.Warning) as e:
		print ("SQL ERROR - get cigars - addevent.html")
		error = "Error getting SQL Data.  Contact IT if the problem continues."
		return render_template("addevent.html", error=error)
	db.close()	

	return render_template("addevent.html", error=error,  ids=ids, name=name, length=length, qty=qty)


@app.route("/stats")
def stats():
	error = None
	humidorH = []
	humidorT = []
	date = []
	time = []
	lastID = 0 
	length = 0                                                                                                                                                   
	db = MySQLdb.connect(mysqlCN, mysqlID, mysqlPW, mysqlDB)
	cursor = db.cursor()                                                                                                                                          
	sqlGetLast = "SELECT * FROM humidor_entry ORDER BY id DESC LIMIT 1"                                                                                                   
	try:                                                                                                                                                          
		cursor.execute(sqlGetLast)                                                                                                                            
		result = cursor.fetchall()                                                                                                                           
		for row in result:
			lastID = row[0]
			tempDate = str(row[5])
			humidorT.append(row[1])
			humidorH.append(row[2])
			date.append(tempDate)    

	except (MySQLdb.Error, MySQLdb.Warning) as e:                                                                                                                                      
		print ("SQL ERROR - get humidor_entry lastID - stats.html")
		error = "Error getting SQL Data.  Contact IT if the problem continues."
		return render_template("stats.html", error=error)                                                                                                                     
                                                                                                                                                                  
	length = lastID + 1                                                                                                                                                 
	i = 0
	while (lastID > 0 and i < 96):                                                                                                                                                                                                                                                                                       
		sqlGetPrevious = "SELECT * FROM humidor_entry WHERE id = {0}".format(lastID)                                                                                  
		try:                                                                                                                                                
			cursor.execute(sqlGetPrevious)                                                                                                              
			result = cursor.fetchall()                                                                                                                 	
			for row in result:
				tempDate = str(row[5])
				humidorT.append(row[1])
				humidorH.append(row[2])
				date.append(tempDate)								
		except (MySQLdb.Error, MySQLdb.Warning) as e:                                                                                                                                               
			print ("SQL ERROR - get humidor_entry previous - stats.html")
			error = "Error getting SQL Data.  Contact IT if the problem continues."
			return render_template("stats.html", error=error)
				   

		lastID = lastID - 1
		i += 1
				                                                                                                                                                  
	db.close() 

	#print(length)
	#print(humidorH)
	#print(humidorT)
	#print(date)
	print("rendering stats")
	return render_template("stats.html", error=error, humidorH=humidorH, humidorT=humidorT, date=date, length=i)

@app.route("/removeCigar", methods=["GET","POST"])
def removeCigar():
	if request.method == 'POST':
		removeid = removeSpecial(request.form['cigarid'])
		#open the database
		db = MySQLdb.connect(mysqlCN, mysqlID, mysqlPW, mysqlDB)
		cursor = db.cursor()
		removeQuery = """DELETE FROM cigar WHERE id={0}""".format(removeid)
		try:
			cursor.execute(removeQuery)
			db.commit()
		except:
			print("error removing cigar " + removeid)
		return redirect("/cigars")

@app.route("/removeEvent", methods=["GET", "POST"])
def removeEvent():
	if request.method == 'POST':
		removeid = removeSpecial(request.form['eventid'])
		cigarid = removeSpecial(request.form['cigarid'])
		#open the database
		db = MySQLdb.connect(mysqlCN, mysqlID, mysqlPW, mysqlDB)
		cursor = db.cursor()
		#get the current cigar quantity
		getQuery = """SELECT qty FROM cigar WHERE id={0} """.format(cigarid)
		cigarQuantity = 0
		try:
			cursor.execute(getQuery)
			result = cursor.fetchall()
			for row in result:
				cigarQuantity = row[0]
		except (MySQLdb.Error, MySQLdb.Warning) as e:
			print ("event error")
		cigarQuantity += 1
		#reset cigar quantity + 1 for event removal
		updateQuery = """UPDATE cigar SET qty={0} WHERE id={1}""".format(cigarQuantity, cigarid)
		try:
			cursor.execute(updateQuery)
			db.commit()
		except:
			print("error updating cigar qty from event removal" + cigarid)

		#remove the event
		removeQuery = """DELETE FROM event WHERE id={0}""".format(removeid)
		try:
			cursor.execute(removeQuery)
			db.commit()
		except:
			print("error removing event " + removeid)
		return redirect("/events")


# below are methods used in several places.
# do not place web page functions here.
def allowed_file(filename):
	print("check filename")
	return '.' in filename and \
		filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def removeSpecial(cigarForm):
	newString = re.sub('[^a-zA-Z0-9 ]', '', cigarForm)
	print(newString)
	return newString


if __name__ == "__main__":
    app.run(host='1.2.3.4', port=1234, debug=True)
