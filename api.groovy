import groovy.sql.Sql
import groovy.json.JsonBuilder
import java.text.DecimalFormat
java.util.Locale.setDefault(new Locale('fr','CH'))

Properties props = new Properties()
props.setProperty('user', 'campuscard')
props.setProperty('password', '')
props.setProperty('ssl', 'true')
db = Sql.newInstance('jdbc:mysql://localhost/campusfood', props , 'com.mysql.jdbc.Driver')

def rows = db.rows("""SELECT type, date, lieu, debit, credit
FROM `campus_card`
WHERE type <> 'correction'""")

def action = params['action'] ?: 'index'

println new JsonBuilder(rows)