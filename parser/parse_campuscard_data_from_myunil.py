# -*- coding: utf-8 -*-
import warnings
warnings.filterwarnings('ignore', '.*the sets module is deprecated.*',DeprecationWarning, 'MySQLdb')
import mechanize
import re
import datetime, time
import HTMLParser

h = HTMLParser.HTMLParser()
br = mechanize.Browser()
br.set_handle_robots(False)
br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]
br.open("https://my.unil.ch/Shibboleth.sso/DS?entityID=https%3A%2F%2Faai.unil.ch%2Fidp%2Fshibboleth&target=http%3A%2F%2Fmy.unil.ch%2Fjahia%2FJahia%2FengineName%2Fshibbolethlogin%2Fsite%2Fmyunil41%2Fpid%2F19")
br.select_form(nr=0)
br["j_username"] = ""
br["j_password"] = ""
r1 = br.submit()
br.select_form(nr=0)
r2 = br.submit()
html = r2.read()
table = re.findall(r"boxcontent_puce\">(.*?</table>)", html, re.DOTALL)[0]
raw_entries = re.findall(r"<tr>(.*?)</tr>", table, re.DOTALL)[1:]
entries = []
for raw_entry in raw_entries:
	cols = re.findall(r">(.*?)</td>", raw_entry, re.DOTALL)
	entry = {}
	entry['type'] = cols[0].strip()
	entry['date'] = datetime.datetime.strptime(cols[1].strip(), "le %d.%m.%Y &#224; %Hh%M")
	entry['lieu'] = h.unescape(cols[2].strip())
	try:
		entry['debit'] = float(cols[3].strip()[4:])
	except ValueError:
		entry['debit'] = 0.0
	try:
		entry['credit'] = float(cols[4].strip()[4:])
	except ValueError:
		entry['credit'] = 0.0
	entries.append(entry)
try:
	solde = float(re.findall(r"Solde.*?CHF (.*?)<", html, re.DOTALL)[0])
except:
	solde = None
card_id = re.findall(r"Card ID.*?;(.*?)<", html, re.DOTALL)[0]


def save_entry(c, entry):
	try:
		c.execute(c.execute("""INSERT INTO  `campusfood`.`campus_card` (
`card_id` ,
`type` ,
`date` ,
`lieu` ,
`debit` ,
`credit`)
VALUES (%s, %s, %s, %s, %s, %s);""",
( card_id, entry['type'], entry['date'].strftime('%Y-%m-%d %H:%M:%S'),
entry['lieu'], entry['debit'], entry['credit'])))
	except:
		pass
			
import MySQLdb
db = MySQLdb.connect(host="localhost",user="campusfood",passwd="",db="campusfood")
db.autocommit(True)
c = db.cursor()

for entry in entries:
	save_entry(c, entry)

c.execute("""SELECT SUM(credit) - SUM(debit) AS solde FROM `campus_card`
WHERE card_id=%s
GROUP BY card_id""" % (card_id))
db_solde = c.fetchone()[0]

entry = {'card_id': card_id, 'type': 'correction', 'date': datetime.datetime.fromtimestamp(time.time()),
	'lieu': 'unil', 'debit': 0.0, 'credit':0.0}
if db_solde < solde:
	entry['credit'] = solde - db_solde
	save_entry(c, entry)
elif db_solde > solde:
	entry['debit'] = db_solde - solde
	save_entry(c, entry)



