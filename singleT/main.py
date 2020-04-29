from flask import Flask, render_template, request,session
import os
import mysql.connector

mydb = mysql.connector.connect(host="127.0.0.1",
                                port="3307",
                                user="root",
                                password="",
                                database="tenantapp",
                                auth_plugin='mysql_native_password')
mycursor = mydb.cursor()
app=Flask(__name__)
app.secret_key=os.urandom(24)

@app.route('/',methods = ['POST','GET'])
def home1():
    return render_template("home.html")

@app.route('/toSignup', methods = ['POST','GET'])
def home2():
    return render_template("tenant_signup.html")

@app.route('/toLogin', methods = ['POST','GET'])
def home3():
    return render_template("tenant_login.html") 
curr_user = ""
curr_user_type=""

@app.route('/toSignup_user',methods=['GET','POST'])
def user_signup():
    query="select t_id,tname from tenant"
    mycursor.execute(query)
    tenants=mycursor.fetchall()
    
    return render_template("user_signup.html",len=len(tenants),tenants=tenants)

@app.route('/toLogin_user',methods=['GET','POST'])
def user_login():
    return render_template("user_login.html")

@app.route('/signUp_user', methods = ['POST', 'GET'])
def signUp_user():
    if request.method == 'POST':
       # name = request.form["name"]
        username = request.form["username"]
        password = request.form["password"]
        confirmPassword = request.form["cnfpassword"]
        t_id=request.form["t_id"]

        #print(name, username, password)
        
        myquery = "select exists(select * from users where username=%s)"
        rec_tup = (username,)
        mycursor.execute(myquery, rec_tup)
        if mycursor.fetchone()[0]==1:
            return render_template('Err.html', message="Username already exists")
        elif password!=confirmPassword:
            return render_template('Err.html', message="Passwords Don't Match")
        else:
            mysql_query = "insert into users(t_id,username,password) values(%s, %s, %s)"
            records = (t_id, username, password)
            mycursor.execute(mysql_query, records)
            mydb.commit()
        return render_template("user_login.html")

@app.route('/login_user', methods = ['POST', 'GET'])
def signIn_user():
    global curr_user
    global curr_user_type
    if request.method == 'POST':
    
        if 'user' in session:
                username=session['user']
                query1="select t_id from users where username=%s"
                rec_tup=(username,)
                mycursor.execute(query1,rec_tup)
                tid=mycursor.fetchone()[0]
                query2="select service_type from tenant_service where t_id=%s"
                rec_tup=(tid,)
                mycursor.execute(query2,rec_tup)
                services=mycursor.fetchall()
                return render_template("user_home.html",user=curr_user,tid=tid,services=services)

        username = request.form["username"]
        password = request.form["password"]
        
        myquery = "select exists(select * from users where username=%s)"
        rec_tup = (username,)
        mycursor.execute(myquery, rec_tup)

        if mycursor.fetchone()[0]==1:
            new_query = "select password from users where username=%s"
            mycursor.execute(new_query, rec_tup)
            if mycursor.fetchone()[0]==password:
                session['user']=username
                query1="select t_id from users where username=%s"
                rec_tup=(username,)
                mycursor.execute(query1,rec_tup)
                tid=mycursor.fetchone()[0]
                query2="select service_type from tenant_service where t_id=%s"
                rec_tup=(tid,)
                mycursor.execute(query2,rec_tup)
                services=mycursor.fetchall()
                return render_template("user_home.html",user=curr_user,tid=tid,services=services)
            else:
                print("username password wrong")
                return render_template('Err.html', message="Username/Password Wrong")
        else:
            print("outer error")
            return render_template('Err.html', message="Username/Password Wrong")

@app.route('/login_tenant', methods = ['POST', 'GET'])
def signIn():
    global curr_user
    global curr_user_type
    if request.method == 'POST':
        username = request.form["username"]
        password = request.form["password"]
        
        myquery = "select exists(select * from tenant where userId=%s)"
        rec_tup = (username,)
        mycursor.execute(myquery, rec_tup)
       # return render_template("tenant_home.html",user=mycursor.fetchone())

        if mycursor.fetchone()[0]==1:
            new_query = "select password from tenant where userId=%s"
            mycursor.execute(new_query, rec_tup)
            if mycursor.fetchone()[0]==password:
                curr_user = username
                session['user']=username
                query0="select t_id from tenant where userId=%s"
                rec_tup=(username,)
                mycursor.execute(query0,rec_tup)
                tid=mycursor.fetchone()[0]
                query="select * from users where t_id=%s"
                rec_tup=(tid,)
                mycursor.execute(query,rec_tup)
                users=mycursor.fetchall()
                #services now
                query2="select service_type from tenant_service where t_id=%s"
                mycursor.execute(query2,rec_tup)
                service_list=mycursor.fetchall()
                print(service_list)
                return render_template("tenant_home.html",user=users,services_list=service_list)
            else:
                print("username password wrong")
                return render_template('Err.html', message="Username/Password Wrong")
        else:
            print("outer error")
            return render_template('Err.html', message="Username/Password Wrong")

@app.route('/signUp_tenant', methods = ['POST', 'GET'])
def signUp_tenant():
    if request.method == 'POST':
        name = request.form["name"]
        username = request.form["userId"]
        password = request.form["password"]
        confirmPassword = request.form["cnfpassword"]
        
        service_array=request.form.getlist('service')
        print(name, username, password)
        
        myquery = "select exists(select * from tenant where userId=%s)"
        rec_tup = (username,)
        mycursor.execute(myquery, rec_tup)
        if mycursor.fetchone()[0]==1:
            return render_template('Err.html', message="Username already exists")
        elif password!=confirmPassword:
            return render_template('Err.html', message="Passwords Don't Match")
        else:
            mysql_query = "insert into tenant(tname,userId,password) values(%s, %s, %s)"
            records = (name, username, password)
            mycursor.execute(mysql_query, records)
            mydb.commit()
            query="select t_id from tenant where userId=%s"
            rec_tup=(username,)
            mycursor.execute(query,rec_tup)
            tid=mycursor.fetchone()[0]
            for service in service_array:
                query1="insert into tenant_service(t_id,service_type) values(%s,%s)"
                records=(tid,service)
                mycursor.execute(query1,records)
                mydb.commit()
        return render_template("tenant_login.html")



@app.route('/all_taxi',methods=['GET'])
def alltaxi():
    if 'user' in session:
        query="select * from taxi"
        mycursor.execute(query)
        f=mycursor.fetchall()
        return render_template('all_taxi.html',taxis=f)
    else:
        return render_template('home.html')

@app.route('/all_flight',methods=['GET'])
def allflight():
    if 'user' in session:
        query="select * from flight"
        mycursor.execute(query)
        f=mycursor.fetchall()
        return render_template('all_flight.html',flights=f)
    else:
        return render_template('home.html')


@app.route('/all_train',methods=['GET'])
def alltrain():
    if 'user' in session:
        query="select * from train"
        mycursor.execute(query)
        f=mycursor.fetchall()
        return render_template('all_train.html',trains=f)
    else:
        return render_template('home.html')

@app.route('/all_hotel',methods=['GET'])
def allhotel():
    if 'user' in session:
        query="select * from hotel"
        mycursor.execute(query)
        f=mycursor.fetchall()
        return render_template('all_hotel.html',hotels=f)
    else:
        return render_template('home.html')
#break

@app.route('/all_usertaxi',methods=['GET'])
def allusertaxi():
    if 'user' in session:
        query="select * from user_taxi where username=%s"
        rec_tup=(session['user'],)
        mycursor.execute(query,rec_tup)
        f=mycursor.fetchall()
        return render_template('all_usertaxi.html',taxis=f)
    else:
        return render_template('home.html')

@app.route('/all_usertrain',methods=['GET'])
def allusertrain():
    if 'user' in session:
        query="select * from user_train where username=%s"
        rec_tup=(session['user'],)
        mycursor.execute(query,rec_tup)
        f=mycursor.fetchall()
        return render_template('all_usertrain.html',trains=f)
    else:
        return render_template('home.html')

@app.route('/all_userhotel',methods=['GET'])
def alluserhotel():
    if 'user' in session:
        query="select * from user_hotel where username=%s"
        rec_tup=(session['user'],)
        mycursor.execute(query,rec_tup)
        f=mycursor.fetchall()
        return render_template('all_userhotel.html',hotels=f)
    else:
        return render_template('home.html')

@app.route('/all_userflight',methods=['GET'])
def alluserflight():
    if 'user' in session:
        query="select * from user_flight where username=%s"
        rec_tup=(session['user'],)
        mycursor.execute(query,rec_tup)
        f=mycursor.fetchall()
        return render_template('all_userflight.html',flights=f)
    else:
        return render_template('home.html')

#break

@app.route('/hotel',methods=['GET'])
def hotel():
    if 'user' in session:
        query="select * from hotel"
        mycursor.execute(query)
        f=mycursor.fetchall()
        return render_template('hotel.html',hotels=f)
    else:
        return render_template('home.html')

@app.route('/flight',methods=['GET'])
def flight():
    if 'user' in session:
        query="select * from flight"
        mycursor.execute(query)
        f=mycursor.fetchall()
        return render_template('flight.html',flights=f)
    else:
        return render_template('home.html')


@app.route('/taxi',methods=['GET'])
def taxi():
    if 'user' in session:
        query="select * from taxi"
        mycursor.execute(query)
        f=mycursor.fetchall()
        return render_template('taxi.html',taxis=f)
    else:
        return render_template('home.html')

@app.route('/train',methods=['GET'])
def train():
    if 'user' in session:
        query="select * from train"
        mycursor.execute(query)
        f=mycursor.fetchall()
        return render_template('train.html',trains=f)
    else:
        return render_template('home.html')

@app.route('/book_flight/<string:flightid>',methods=['GET','POST'])
def book_flight(flightid):
    if 'user' in session:
        query="select from_city,to_city,avail_seats from flight where fl_id=%s"
        rec_tup=(flightid,)
        mycursor.execute(query,rec_tup)
        f=mycursor.fetchone()
        fromCity=f[0]
        toCity=f[1]
        availSeats=f[2]
        if availSeats>0:
            availSeats=availSeats-1
            query1="update flight set avail_seats=%s where fl_id=%s"
            rec_tup=(availSeats,flightid)
            mycursor.execute(query1,rec_tup)
            query2="insert into user_flight(username,fl_id,from_city,to_city) values (%s,%s,%s,%s)"
            rec_tup=(session['user'],flightid,fromCity,toCity)
            mycursor.execute(query2,rec_tup)
            mydb.commit()
            query3="select ticket_id from user_flight where username=%s"
            rec_tup1=(session['user'],)
            mycursor.execute(query3,rec_tup1)
            records=mycursor.fetchall()
            length=len(records)
            last_record=records[length-1]
            return render_template('flight_confirm.html',id=last_record[0],other=rec_tup)
        else:
            return 'no seats available'
    else:
        return render_template('home.html')

@app.route('/book_taxi/<string:taxiid>',methods=['GET','POST'])
def book_taxi(taxiid):
    if 'user' in session:
        query="select taxi_number,oper_city,rate_km from taxi where tx_id=%s"
        rec_tup=(taxiid,)
        mycursor.execute(query,rec_tup)
        t=mycursor.fetchone()
        taxi_number=t[0]
        oper_city=t[1]
        rate_km=t[2]
        query2="insert into user_taxi(username,tx_id,taxi_number,oper_city,rate_km) values (%s,%s,%s,%s,%s)"
        rec_tup=(session['user'],taxiid,taxi_number,oper_city,rate_km)
        mycursor.execute(query2,rec_tup)
        mydb.commit()
        query3="select ticket_id from user_taxi where username=%s"
        rec_tup1=(session['user'],)
        mycursor.execute(query3,rec_tup1)
        records=mycursor.fetchall()
        length=len(records)
        last_record=records[length-1]
        return render_template('taxi_confirm.html',id=last_record[0],other=rec_tup)
    else:
        return render_template('home.html')

@app.route('/book_train/<string:trainid>',methods=['GET','POST'])
def book_train(trainid):
    if 'user' in session:
        query="select from_city,to_city,avail_seats,price from train where tr_id=%s"
        rec_tup=(trainid,)
        mycursor.execute(query,rec_tup)
        f=mycursor.fetchone()
        fromCity=f[0]
        toCity=f[1]
        availSeats=f[2]
        price = f[3]
        if availSeats>0:
            availSeats=availSeats-1
            query1="update train set avail_seats=%s where tr_id=%s"
            rec_tup=(availSeats,trainid)
            mycursor.execute(query1,rec_tup)
            query2="insert into user_train(username,tr_id,from_city,to_city) values (%s,%s,%s,%s)"
            rec_tup=(session['user'],trainid,fromCity,toCity)
            mycursor.execute(query2,rec_tup)
            mydb.commit()
            query3="select ticket_id from user_train where username=%s"
            rec_tup1=(session['user'],)
            mycursor.execute(query3,rec_tup1)
            records=mycursor.fetchall()
            length=len(records)
            last_record=records[length-1]
            return render_template('train_confirm.html',id=last_record[0],other=rec_tup)
        else:
            return 'no seats available'
    else:
        return render_template('home.html')


@app.route('/book_hotel/<string:hotelid>',methods=['GET','POST'])
def book_hotel(hotelid):
    if 'user' in session:
        query="select hotel_name,city,avail_rooms,price from hotel where ht_id=%s"
        rec_tup=(hotelid,)
        mycursor.execute(query,rec_tup)
        f=mycursor.fetchone()
        hotelName=f[0]
        city=f[1]
        availrooms=f[2]
        if availrooms>0:
            availrooms=availrooms-1
            query1="update hotel set avail_rooms=%s where ht_id=%s"
            rec_tup=(availrooms,hotelid)
            mycursor.execute(query1,rec_tup)
            query2="insert into user_hotel(username,ht_id,city) values (%s,%s,%s)"
            rec_tup=(session['user'],hotelid,city)
            mycursor.execute(query2,rec_tup)
            mydb.commit()
            query3="select ticket_id from user_hotel where username=%s"
            rec_tup1=(session['user'],)
            mycursor.execute(query3,rec_tup1)
            records=mycursor.fetchall()
            length=len(records)
            last_record=records[length-1]
            return render_template('hotel_confirm.html',id=last_record[0],other=rec_tup)
        else:
            return 'no seats available'
    else:
        return render_template('home.html')

   
@app.route('/logout', methods = ['POST', 'GET'])
def logout():
    session.pop('user',None)
    return render_template('home.html')

if __name__ == "__main__":
    app.run(debug=True)