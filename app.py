from flask import Flask, render_template, request, redirect, url_for, session,g,flash
from flask_mysqldb import MySQL,MySQLdb
#import bcrypt
from datetime import date
today = date.today()
#from flaskext.mysql import MySQL


app = Flask(__name__)


app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'admin'
app.config['MYSQL_DB'] = 'flaskdb'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
mysql = MySQL(app)
#Database

# NEW
@app.route("/view_patients", methods=['POST','GET'])
def view_patients():
    if request.method=="GET" and g.user:
        curl = mysql.connection.cursor(MySQLdb.cursors.DictCursor) #creating a dictionary cursor
        curl.execute("SELECT * FROM patients;")
        user = curl.fetchall()
        if user:
            curl.close()
            return render_template("view_patients.html",data=user)
        curl.close()
        return render_template("view_patients.html",data=user)
    return redirect(url_for('login'))

    
@app.route("/view_patient", methods=['POST', 'GET'])
def view_patient():
    if request.method=="POST":
        if request.form.get('get'):
            pid=request.form.get('ssnid')
            session['patient']=True
            session['pid']=pid
            curl = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            curl.execute("SELECT * FROM patients WHERE pid=%s",(pid,))
            user = curl.fetchone()
            if user:
                flash(u"Patient Found successfully.",'information')
                curl.close()
                return render_template("view_patient.html",data=user)
            flash(u'Invalid ID or Check Patient status','error')
            curl.close()
            return render_template("view_patient.html")
    if g.user:
        return render_template('view_patient.html', user=session['name'])
    return redirect(url_for('login'))
    # return render_template("view_patient.html")

@app.route("/all", methods=["POST","GET"])
def all():
    if request.method=='POST':
        mname=request.form.get('mname')
        quan=request.form.get('quan')
        price=request.form.get('price')
        pid=session['pid']
        curl = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        curl.execute("insert into medicines values(%s,%s,%s,%s)",(pid,mname, quan, price))
        mysql.connection.commit()
        curl.execute("SELECT * FROM medicines where pid=%s;",(pid,))
        user = curl.fetchall()
        if user:
            curl.close()
            return render_template("all.html",data=user)
        curl.close()
        #print(data)
        
        #return render_template('all.html', user=session['name'], data=data)
    if g.user:
        if 'patient' in session and session['patient']==True:
            pid=session['pid']
            # print("hree")
            curl = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            curl.execute("SELECT * FROM medicines where pid=%s;",(pid,))
            user = curl.fetchall()
            if user:
                curl.close()
                return render_template("all.html",data=user)
            curl.close()
            return render_template('all.html', user=session['name'], data=user)
        else:
            return redirect(url_for('view_patient'))
    return redirect(url_for('login'))
    
#starting pages  
@app.route("/create_patient",methods=["POST","GET"])
def create_patient():
    if request.method=='POST':
        p_id=request.form.get('pid')
        pname=request.form.get('pname')
        age=request.form.get('age')
        add=request.form.get('address')
        state=request.form.get('state')
        city=request.form.get('city')
        doj=request.form.get('date')
        bedtype=request.form.get('bedtype')
        
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO patients (pid, p_name, age, address, state,  city, doj, bedtype ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",(p_id,pname,age,add,state,city,doj,bedtype))
        mysql.connection.commit()
        session['patient']=True
        session['pid']=p_id
        return redirect(url_for('home'))
    else:
        if g.user:
            return render_template('create_patient.html', user=session['name'])
        return redirect(url_for('login'))
    
@app.route("/delete_patient", methods=["POST", "GET"])
def delete_patient():
    if request.method=="POST":
        if request.form.get('get'):
            pid=request.form.get('ssnid')
            curl = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            curl.execute("SELECT * FROM patients WHERE pid=%s",(pid,))
            user = curl.fetchone()
            if user:
                curl.close()
                flash(u"Patient Found successfully.You can delete the patient.",'information')
                session['pid']=False
                return render_template("delete_patient.html",data=user)
            flash(u"Invalid ID or Check Patient status",'error')
            return render_template("delete_patient.html")
        if request.form.get('delete'):
            pid=request.form.get('ssnid')
            #print("HEREEEE::",pid)
            curl = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            curl.execute("DELETE FROM medicines WHERE pid=%s",(pid,))
            curl.execute("DELETE FROM diagnosis WHERE pid=%s",(pid,))
            curl.execute("DELETE FROM patients WHERE pid=%s",(pid,))
            mysql.connection.commit()
            curl.close()
            flash(u"Patient Deleted Successfully",'information')
            return render_template("delete_patient.html")
        
    if g.user:
        return render_template('delete_patient.html', user=session['name'])
    return redirect(url_for('login'))
    
@app.route("/update_patient",methods=['POST','GET'])
def update_patient():
    # print("here")
    if request.method=="POST":
        if request.form.get('get'):
            pid=request.form.get('ssnid')
            curl = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            curl.execute("SELECT * FROM patients WHERE pid=%s",(pid,))
            user = curl.fetchone()
            if user:
                flash(u"Patient Found successfully.Now you can Update the changes.",'information')
                curl.close()
                return render_template("update_patient.html",data=user)
            flash(u"Invalid ID or Check Patient status",'error')
            curl.close()
            return render_template("update_patient.html")  
        
        if request.form.get('update'):
            pid=request.form.get('ssnid')
            pname=request.form.get('pname')
            age=request.form.get('age')
            doj=request.form.get('date')
            bedtype=request.form.get('bedtype')
            address=request.form.get('address')
            state=request.form.get('state')
            city=request.form.get('city')
            flash(u"Patient Updated successfully",'information')
            curl = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            curl.execute("UPDATE patients SET p_name=%s, age=%s, doj=%s, bedtype=%s, address=%s, state=%s, city=%s WHERE pid=%s",(pname,age,doj,bedtype,address,state,city,pid,))
            mysql.connection.commit()
            # print(curl.rowcount)
            curl.close()
            
            return render_template("update_patient.html")
    else:
        if g.user:
            return render_template('update_patient.html', user=session['name'])
        return redirect(url_for('login'))
    # return render_template("update_patient.html")
# NEW END

@app.route('/')
def home():
    return render_template("home.html")

@app.route('/login',methods=["GET","POST"])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        curl = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        curl.execute("SELECT * FROM users WHERE email=%s",(email,))
        user = curl.fetchone()
        curl.close()

        if user is not None:
            if(user["password"] == password):
                session['name'] = user['name']
                session['email'] = user['email']
                return render_template("home.html")
            else:
                return "Error password and email not match"
        else:
            return "Error user not found"
    else:
        return render_template("login.html")

@app.route('/logout', methods=["GET", "POST"])
def logout():
    session.clear()
    return render_template("home.html")

@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == 'GET':
        return render_template("register.html")
    else:
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        # password = request.form['password'].encode('utf-8')
        # hash_password = bcrypt.hashpw(password, bcrypt.gensalt())

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users (name, email, password) VALUES (%s,%s,%s)",(name,email,password,))
        mysql.connection.commit()
        session['name'] = request.form['name']
        session['email'] = request.form['email']
        return redirect(url_for('home'))



@app.route("/diag",methods=['POST','GET'])         #daigonistics page(US008)
def diag():
    if request.method=='POST':
        pid=session['pid']
        tname=request.form.get('tname')
        cost=request.form.get('cost')
        curl = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        curl.execute("insert into diagnosis values(%s,%s,%s)",(session['pid'],tname, cost))
        mysql.connection.commit()
        curl.execute("SELECT * FROM diagnosis where pid=%s;",(pid,))
        user = curl.fetchall()
        if user:
            curl.close()
            return render_template("diag.html",data=user)
        curl.close()
        #print(data)
        
       # return render_template('diag.html', user=session['name'], data=data)
    if g.user:
        if 'patient' in session:
            pid=session['pid']
            curl = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            curl.execute("SELECT * FROM diagnosis where pid=%s;",(pid,))
            user = curl.fetchall()
            if user:
                curl.close()
                return render_template("diag.html",data=user)
            curl.close()
            return render_template('diag.html', user=session['name'], data=user)
        else:
            return redirect(url_for('view_patient'))
    return redirect(url_for('login'))


@app.route("/final")       #final page(US009)
def final():
    if g.user:
        if 'patient' in session:
            pid=session['pid']
            curl = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            curl.execute("SELECT * FROM medicines where pid=%s;",(pid,))
            meds = curl.fetchall()
            curl.execute("SELECT * FROM diagnosis where pid=%s;",(pid,))
            diags = curl.fetchall()
            curl.execute("SELECT * FROM patients where pid=%s;",(pid,))
            user = curl.fetchall()
            mtotal,dtotal,atotal=0,0,0
            print(meds)
            for i in meds:
                print(i)
                mtotal+=int(i['price'])
            for i in diags:
                dtotal+=int(i['cost'])
            for i in user:
                if(i['bedtype']=="General Ward"):
                    atotal=1500
                elif(i['bedtype']=="Semi Sharing"):
                    atotal=2500
                else:
                    atotal=5000
                days=today-i['doj']
                print('days',days.days)
                # print(type(days))
                    
            return render_template("final.html",meds=meds,diags=diags,user=user,mtotal=mtotal,dtotal=dtotal,atotal=atotal,days=days.days)
        else:
            return redirect(url_for('view_patient'))
    return redirect(url_for('login'))


@app.before_request
def before_request():
    g.user=None
    # print("here",session)
    if 'name' in session:
        g.user=session['name']
        # print("yes")

if __name__ == '__main__':
    app.secret_key = "^A%DJAJU^JJ123"
    #app.run(host='127.0.0.1',port='5000',debug="True")
    app.run(host='127.0.0.1',port='7000',debug="True")
    #127.0.0.1:7000