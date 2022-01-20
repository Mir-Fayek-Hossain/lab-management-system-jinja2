# FLUSK MINIMAL DOCUMENT ,FOR TEMPLATES, FOR GET POST REQUEST
from flask import Flask, render_template,request,redirect,session
from flask_mysqldb import MySQL
app = Flask(__name__)
# FOR SESSION
app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'
# DATABASE CONFIG
app.config['MYSQL_HOST']="localhost"
app.config['MYSQL_USER']="root"
app.config['MYSQL_PASSWORD']="1234"
app.config['MYSQL_DB']="unix"
mysql= MySQL(app)


# 404 error
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

# SIGNUP
@app.route('/signup', methods = ['GET', 'POST'])
def signup():
    if request.method=="POST":
        studentDetails=request.form
        stdName=studentDetails['stdName']
        stdId=studentDetails['stdId']
        stdPassword=studentDetails['stdPassword']
        cur=mysql.connection.cursor()
        result=cur.execute(f"SELECT * from students where student_id = '{stdId}'")
        if result==0:
            cur.execute("INSERT INTO students(student_name,student_id,student_password) VALUES(%s,%s,%s)",(stdName,stdId,stdPassword))
            mysql.connection.commit()
            cur.close()
            session['upd']="done"
            return redirect('/login')
        else:
            error= "You already have an account."
            goto=f"/login"
            return render_template("error.html",error=error,goto=goto)
# LOGIN
@app.route('/login')
def log():
    return render_template("login.html")

@app.route('/', methods = ['GET', 'POST'])
def login():
    session['upd']=None
    if request.method=="POST":
        studentDetails=request.form
        stdId=studentDetails['stdId']
        stdPassword=studentDetails['stdPassword']
        if stdId=='admin' and stdPassword=='admin':
            return redirect('/admin')
        else:
            cur=mysql.connection.cursor()
            result=cur.execute(f"SELECT * from students where student_id = '{stdId}'")
            if result ==0:
                error= "Incorrrect ID."
                goto="/login"
                mysql.connection.commit()
                cur.close()
                return render_template("error.html",error=error,goto=goto)
            else:
                result=cur.execute(f"SELECT * from students where student_id = '{stdId}' AND student_password = '{stdPassword}'")
                if result !=0:
                    session['id']=stdId
                    cur=mysql.connection.cursor()
                    result=cur.execute("SELECT * from labroutine ORDER BY CASE WHEN day = 'sunday' THEN 1 WHEN day = 'monday' THEN 2 WHEN day = 'tuesday' THEN 3 WHEN day = 'wednesday' THEN 4 WHEN day = 'thursday' THEN 5 WHEN day = 'Saturday' THEN 6 END ASC")
                    if result>0:
                        labDetails=cur.fetchall()
                        mysql.connection.commit()
                        cur.close()
                        return render_template("index.html",stdId=stdId, labDetails=labDetails)
                else: 
                    error= "Incorrect password."
                    goto="/login"
                    mysql.connection.commit()
                    cur.close()
                    return render_template("error.html",error=error,goto=goto)
    else:
        if(session):
            stdId=session['id']
            return render_template("index.html",stdId=stdId)
        else:
            return redirect('/login')
#LOGOUT
@app.route('/logout')
def logout():
        session.clear()
        return redirect('/login')

# INDEX
@app.route('/home', methods = ['GET', 'POST'])
def index():
    
    session['upd']=None
    if(session):
        cur=mysql.connection.cursor()
        result=cur.execute("SELECT * from labroutine ORDER BY CASE WHEN day = 'sunday' THEN 1 WHEN day = 'monday' THEN 2 WHEN day = 'tuesday' THEN 3 WHEN day = 'wednesday' THEN 4 WHEN day = 'thursday' THEN 5 WHEN day = 'Saturday' THEN 6 END ASC")
        if result>0:
            labDetails=cur.fetchall()
            mysql.connection.commit()
            cur.close()
            return render_template("index.html",labDetails=labDetails)
    else:
        return redirect('/login')

#ABOUT
@app.route('/about')
def about():
    
    session['upd']=None
    return render_template("about.html")



  
# PROFILE
@app.route('/profile/<int:id>', methods = ['GET', 'POST'])
def profile(id):
    session['upd']=None
    if('id' in session):
        stdDetails=request.form
        stdId=id
        cur=mysql.connection.cursor()
        result=cur.execute(f"SELECT * from students WHERE student_id ='{stdId}'")
        if result>0:
            details=cur.fetchall()
            mysql.connection.commit()
            cur.close()
            return render_template("profile.html",details=details)
    return redirect('/login')

    
# UPDATE PROFILE
@app.route('/update-profile/<int:id>', methods = ['GET', 'POST'])
def uProfile(id):
    if request.method =="POST":
        stdDetails=request.form
        name=stdDetails['stdName']
        newPassword=stdDetails['newStdPass']
        oldPassword=stdDetails['oldStdPass']
        cur=mysql.connection.cursor()
        result=cur.execute(f"SELECT * from students WHERE student_password ='{oldPassword}'")
        if result==0:
            error="Incorrect password"
            goto=f"/update-profile/{ id }"
            mysql.connection.commit()
            cur.close()
            return render_template("error.html",error=error,goto=goto)
        else:
            if newPassword:
                cur.execute(f"UPDATE students SET student_password='{newPassword}' WHERE student_id = '{id}'")
            else :
                cur.execute(f"UPDATE students SET student_name= '{name}' WHERE student_id = '{id}'")            
            mysql.connection.commit()
            cur.close()
            session['upd']="Done"
            return redirect(f'/update-profile/{id}')
    else:
        stdId=id
        cur=mysql.connection.cursor()
        result=cur.execute(f"SELECT * from students WHERE student_id ='{stdId}'")
        if result>0:
            uDetails=cur.fetchall()
            mysql.connection.commit()
            cur.close()
            return render_template("profile.html",uDetails=uDetails)
        else:
            mysql.connection.commit()
            cur.close()
            return render_template('404.html')
#SEARCH
@app.route('/search', methods = ['GET', 'POST'])
def search():
    if request.method=="POST":
        labDetails=request.form
        name=labDetails['name']
        cur=mysql.connection.cursor()
        result=cur.execute(f"SELECT * from labroutine where courseName LIKE '{name}%'")
        if result>0:
            availableDetails=cur.fetchall()
            mysql.connection.commit()
            cur.close()
            return render_template("index.html",availableDetails=availableDetails)
        else:
            message="Sorry invailid Course name"
            return render_template("index.html",message=message)


# ADMIN
@app.route('/admin', methods = ['GET', 'POST'])
def admin():
    cur=mysql.connection.cursor()
    if request.method=="POST":
        firstp=""
        secondp=""
        thirdp=""
        labDetails=request.form
        day=labDetails['day']
        courseCode=labDetails['courseCode']
        courseTeacher=labDetails['courseTeacher']
        time=labDetails['time']
        if time=='1st':
            firstp="10:00am-11:25am"
            secondp=None
            thirdp=None
        elif time=='2nd':
            firstp=None
            secondp="11:30am-1:00pm"
            thirdp=None
        elif time=='3rd':
            firstp=None
            secondp=None
            thirdp="1:05pm-2:30pm"
        lab=labDetails['lab']
        cur=mysql.connection.cursor()
        cur.execute("INSERT INTO labroutine(day,firstPeriod,secondPeriod,thirdPeriod,room,courseName,courseTeacher) VALUES(%s,%s,%s,%s,%s,%s,%s)",(day,firstp,secondp,thirdp,lab,courseCode,courseTeacher))
        mysql.connection.commit()
        cur.close()
        return redirect('/admin')
    else:
        result=cur.execute("SELECT * from labroutine ORDER BY CASE WHEN day = 'sunday' THEN 1 WHEN day = 'monday' THEN 2 WHEN day = 'tuesday' THEN 3 WHEN day = 'wednesday' THEN 4 WHEN day = 'thursday' THEN 5 WHEN day = 'Saturday' THEN 6 END ASC")
        if result>0:
            labDetails=cur.fetchall()
            mysql.connection.commit()
            cur.close()
            return render_template("admin.html",labDetails=labDetails)
#ADMIN UPDATE
@app.route('/update/<int:id>', methods = ['GET', 'POST'])
def update(id):
    if request.method =="POST":
        labDetails=request.form
        day=labDetails['day']
        courseCode=labDetails['courseCode']
        courseTeacher=labDetails['courseTeacher']
        time=labDetails['time']
        lab=labDetails['lab']
        cur=mysql.connection.cursor()
        if time=='10:00am-11:25am':
            cur.execute(f"UPDATE labroutine SET day= '{day}',firstPeriod= '10:00am-11:25am',secondPeriod= NULL,thirdPeriod= NULL,room= '{lab}',courseName= '{courseCode}',courseTeacher= '{courseTeacher}' WHERE id = {id}")
            mysql.connection.commit()
            cur.close()
            return redirect('/admin')
        elif time=='11:30am-1:00pm':
            cur.execute(f"UPDATE labroutine SET day= '{day}',firstPeriod= NULL,secondPeriod= '11:30am-1:00pm',thirdPeriod=NULL,room= '{lab}',courseName= '{courseCode}',courseTeacher= '{courseTeacher}' WHERE id = {id}")
            mysql.connection.commit()
            cur.close()
            return redirect('/admin')
        elif time=='1:05pm-2:30pm':
            cur.execute(f"UPDATE labroutine SET day= '{day}',firstPeriod= NULL,secondPeriod= NULL,thirdPeriod= '1:05pm-2:30pm',room= '{lab}',courseName= '{courseCode}',courseTeacher= '{courseTeacher}' WHERE id = {id}")
            mysql.connection.commit()
            cur.close()
            return redirect('/admin')
    else:
        cur=mysql.connection.cursor()
        result=cur.execute(f"SELECT * from labroutine where id = {id}")
        if result>0:
            details=cur.fetchall()
            mysql.connection.commit()
            cur.close()
            return render_template("update.html",details=details)

          
# ADMIN DELETE
@app.route('/delete/<int:id>', methods = ['GET', 'POST'])
def delete(id):
    cur=mysql.connection.cursor()
    result=cur.execute(f"DELETE FROM labroutine  WHERE id = {id}")
    mysql.connection.commit()
    cur.close()
    return redirect('/admin')



# it is to check are we running frograms from library
if __name__=="__main__" :
    app.run(debug=True)