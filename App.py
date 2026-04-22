from flask import Flask, render_template, request, session, flash, redirect
import threading
import mysql.connector
import base64, os, sys, datetime
from fsdk_utils import train_fsdk

app = Flask(__name__)
app.config['SECRET_KEY'] = 'aaa'


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/AdminLogin')
def AdminLogin():
    return render_template('AdminLogin.html')


@app.route('/NewUser')
def NewUser():
    return render_template('NewUserOptions.html')

@app.route('/LiveRecognitionCapture')
def LiveRecognitionCapture():
    import LiveRecognition  as liv
    liv.att()
    return render_template('NewUser.html', manual_mode=False)

@app.route('/ManualCapture')
def ManualCapture():
    return render_template('NewUser.html', manual_mode=True)


@app.route("/adminlogin", methods=['GET', 'POST'])
def adminlogin():
    error = None
    if request.method == 'POST':
        if request.form['uname'] == 'admin' and request.form['password'] == 'admin':

            conn = mysql.connector.connect(user='root', password='', host='localhost', database='1smartcrimenalyolopy(new)')
            cur = conn.cursor()
            cur.execute("SELECT * FROM regtb ")
            data = cur.fetchall()
            flash("you are successfully Login")
            return render_template('AdminHome.html', data=data)

        else:
            flash("UserName or Password Incorrect!")
            return render_template('AdminLogin.html')


@app.route("/EntryInfo")
def EntryInfo():
    conn = mysql.connector.connect(user='root', password='', host='localhost', database='1smartcrimenalyolopy(new)')
    cur = conn.cursor()
    cur.execute("SELECT * FROM entrytb  ")
    data = cur.fetchall()
    return render_template('EntryInfo.html', data=data)


@app.route("/AdminHome")
def AdminHome():
    conn = mysql.connector.connect(user='root', password='', host='localhost', database='1smartcrimenalyolopy(new)')
    cur = conn.cursor()
    cur.execute("SELECT * FROM regtb  ")
    data = cur.fetchall()
    return render_template('AdminHome.html', data=data)

@app.route("/Remove")
def Remove():
    id = request.args.get('lid')

    conn = mysql.connector.connect(user='root', password='', host='localhost', database='1smartcrimenalyolopy(new)')
    cursor = conn.cursor()
    cursor.execute("Delete  from  regtb  where id='" + id + "' ")
    conn.commit()
    conn.close()

    conn = mysql.connector.connect(user='root', password='', host='localhost', database='1smartcrimenalyolopy(new)')
    cur = conn.cursor()
    cur.execute("SELECT * FROM regtb  ")
    data = cur.fetchall()
    return render_template('AdminHome.html', data=data)


@app.route("/newuser", methods=['GET', 'POST'])
def newuser():
    if request.method == 'POST':
        name = request.form['name']
        mobile = request.form['mobile']

        address = request.form['address']
        username = request.form['uname']
        cinfo = request.form['cinfo']
        cid = request.form['cid']

        outFileName = 'static/user/' + username + '.jpg'

        if 'file' in request.files and request.files['file'].filename != '':
            file = request.files['file']
            file.save(outFileName)
            # Train FSDK tracker with the new image
            train_fsdk(outFileName, username)

        conn = mysql.connector.connect(user='root', password='', host='localhost', database='1smartcrimenalyolopy(new)')
        cursor = conn.cursor()
        cursor.execute(
            "insert into regtb values('','" + name + "','" + mobile + "','" + address + "','" + username + "','"+ cid +"','"+
          cinfo  +"','"+ outFileName +"')")
        conn.commit()
        conn.close()
        flash("Record Saved!")

    return render_template('NewUser.html', manual_mode=False)

@app.route("/Verify")
def Verify():
    import LiveRecognition2 as liv
    liv.att()

    conn = mysql.connector.connect(user='root', password='', host='localhost', database='1smartcrimenalyolopy(new)')
    cur = conn.cursor()
    cur.execute("select *from entrytb ORDER BY id DESC LIMIT 1 ")
    data = cur.fetchall()
    return render_template('Userentryinfo.html', data=data)


@app.route("/EditUser")
def EditUser():
    id = request.args.get('lid')
    conn = mysql.connector.connect(user='root', password='', host='localhost', database='1smartcrimenalyolopy(new)')
    cur = conn.cursor()
    cur.execute("SELECT * FROM regtb WHERE id='" + id + "'")
    data = cur.fetchone()
    return render_template('EditUser.html', data=data)

@app.route("/UpdateUser", methods=['POST'])
def UpdateUser():
    if request.method == 'POST':
        id = request.form['id']
        name = request.form['name']
        mobile = request.form['mobile']
        address = request.form['address']
        username = request.form['uname']
        cinfo = request.form['cinfo']
        cid = request.form['cid']

        conn = mysql.connector.connect(user='root', password='', host='localhost', database='1smartcrimenalyolopy(new)')
        cursor = conn.cursor()
        
        if 'file' in request.files and request.files['file'].filename != '':
            file = request.files['file']
            outFileName = 'static/user/' + username + '.jpg'
            file.save(outFileName)
            # Train FSDK tracker with the updated image
            train_fsdk(outFileName, username)
            cursor.execute("UPDATE regtb SET Name='" + name + "', Mobile='" + mobile + "', Address='" + address + "', UserName='" + username + "', CrimeID='" + cid + "', CrimeInfo='" + cinfo + "', Image='" + outFileName + "' WHERE id='" + id + "'")
        else:
            cursor.execute("UPDATE regtb SET Name='" + name + "', Mobile='" + mobile + "', Address='" + address + "', UserName='" + username + "', CrimeID='" + cid + "', CrimeInfo='" + cinfo + "' WHERE id='" + id + "'")
            
        conn.commit()
        conn.close()
        flash("Record Updated Successfully!")
    return redirect('/AdminHome')

@app.route("/NewEntry")
def NewEntry():
    return render_template('NewEntry.html')

@app.route("/AddEntryInfo", methods=['POST'])
def AddEntryInfo():
    if request.method == 'POST':
        username = request.form['uname']
        date = request.form['date']
        time = request.form['time']
        
        outFileName = "0"
        if 'file' in request.files and request.files['file'].filename != '':
            import random
            fnew = random.randint(1111, 9999)
            file = request.files['file']
            outFileName = 'static/upload/' + str(fnew) + username + '.jpg'
            file.save(outFileName)

        conn = mysql.connector.connect(user='root', password='', host='localhost', database='1smartcrimenalyolopy(new)')
        cursor = conn.cursor()
        cursor.execute("insert into entrytb values('','" + username + "','" + date + "','" + time + "','" + outFileName + "')")
        conn.commit()
        conn.close()
        flash("Entry Saved Successfully!")
    return redirect('/EntryInfo')


@app.route("/DeleteEntryInfo")
def DeleteEntryInfo():
    id = request.args.get('lid')
    conn = mysql.connector.connect(user='root', password='', host='localhost', database='1smartcrimenalyolopy(new)')
    cursor = conn.cursor()
    cursor.execute("Delete from entrytb where id='" + id + "'")
    conn.commit()
    conn.close()
    flash("Entry Deleted Successfully!")
    return redirect('/EntryInfo')

@app.route("/DangerousAction")
def DangerousAction():
    import cv2
    from ultralytics import YOLO

    # Load the Yolov11 model

    # Open the video file
    # video_path = "path/to/your/video/file.mp4"
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        flash("Could not open camera.",'error')
        return render_template('index.html')

    dd1 = 0
    model = YOLO('runs/detect/weapon/weights/best.pt')
    # Loop through the video frames
    while cap.isOpened():
        # Read a frame from the video
        success, frame = cap.read()

        if success:
            # Run Yolov11 inference on the frame
            results = model(frame, conf=0.4)
            for result in results:
                if result.boxes:
                    # Identify the "best" object to name (Prioritize weapons over 'suspicious')
                    weapon_classes = ['gun', 'knife', 'pistol', 'scissor', 'crow']
                    best_box = None
                    best_name = None
                    
                    # Try to find a weapon first
                    for box in result.boxes:
                        class_id = int(box.cls)
                        name = model.names[class_id]
                        if name in weapon_classes:
                            best_name = name
                            best_box = box
                            break 

                    if not best_name:
                        # Fallback to 'suspicious' if nothing else is found but a box exists
                        for box in result.boxes:
                            class_id = int(box.cls)
                            name = model.names[class_id]
                            if name == 'suspicious':
                                best_name = name
                                best_box = box
                                break
                    
                    if not best_name:
                        # Absolute fallback to first box
                        best_box = result.boxes[0]
                        best_name = model.names[int(best_box.cls)]

                    object_name = best_name
                    subject = f"Alert: {object_name.capitalize()}"

                    if object_name != 'person':
                        dd1 += 1

                    if dd1 == 20:
                        dd1 = 0
                        import winsound

                        filename = 'alert.wav'
                        winsound.PlaySound(filename, winsound.SND_FILENAME)

                        annotated_frame = results[0].plot()

                        # Save alert image to a subfolder to avoid triggering Flask reloader in root
                        if not os.path.exists('static/temp'):
                            os.makedirs('static/temp')
                        alert_path = "static/temp/alert.jpg"
                        cv2.imwrite(alert_path, annotated_frame)
                        
                        # Run slow notification tasks in background threads
                        threading.Thread(target=sendmail, args=(alert_path, object_name)).start()
                        threading.Thread(target=sendmsg, args=("9087259509", "Prediction Name:" + object_name)).start()

                        cap.release()
                        cv2.destroyAllWindows()
                        import time
                        time.sleep(1.0) # Give hardware time to release

                        import LiveRecognition2 as liv
                        liv.att()

                        data = []
                        try:
                            conn = mysql.connector.connect(user='root', password='', host='localhost',
                                                           database='1smartcrimenalyolopy(new)')
                            cur = conn.cursor()
                            cur.execute("select *from entrytb ORDER BY id DESC LIMIT 1 ")
                            data = cur.fetchall()
                        except Exception as e:
                            print(f"Database error: {e}")
                        return render_template('Userentryinfo.html', data=data)



            # Visualize the results on the frame
            annotated_frame = results[0].plot()

            # Display the annotated frame
            cv2.imshow("Yolov11 Inference", annotated_frame)

            # Break the loop if 'q' is pressed
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
        else:
            break
    # Release the video capture object and close the display window
    cap.release()
    cv2.destroyAllWindows()


def sendmsg(targetno, message):
    import requests
    requests.post(
        "http://sms.creativepoint.in/api/push.json?apikey=6555c521622c1&route=transsms&sender=FSSMSS&mobileno=" + targetno + "&text=Dear customer your msg is " + message + "  Sent By FSMSG FSSMSS")


def sendmail(alert_file="static/temp/alert.jpg", object_name="Unknown"):
    import smtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    from email.mime.base import MIMEBase
    from email import encoders
    import datetime

    fromaddr = "studentmailsend@gmail.com"
    toaddr = "karthikanithy1510@gmail.com"

    # instance of MIMEMultipart
    msg = MIMEMultipart()

    # storing the senders email address
    msg['From'] = fromaddr

    # storing the receivers email address
    msg['To'] = toaddr

    # storing the subject
    msg['Subject'] = "Alert: " + object_name

    # current time
    now = datetime.datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")

    # string to store the body of the mail
    body = f"Dangerous Action Detected: {object_name}\nTime: {dt_string}"

    # attach the body with the msg instance
    msg.attach(MIMEText(body, 'plain'))

    # open the file to be sent
    filename = os.path.basename(alert_file)
    attachment = open(alert_file, "rb")

    # instance of MIMEBase and named as p
    p = MIMEBase('application', 'octet-stream')

    # To change the payload into encoded form
    p.set_payload((attachment).read())

    # encode into base64
    encoders.encode_base64(p)

    p.add_header('Content-Disposition', "attachment; filename= %s" % filename)

    # attach the instance 'p' to instance 'msg'
    msg.attach(p)

    # creates SMTP session
    s = smtplib.SMTP('smtp.gmail.com', 587)

    # start TLS for security
    s.starttls()

    # Authentication
    s.login(fromaddr, "jfrj aazz krww zkoh")

    # Converts the Multipart msg into a string
    text = msg.as_string()

    # sending the mail
    s.sendmail(fromaddr, toaddr, text)

    # terminating the session
    s.quit()

if __name__ == '__main__':
    app.run(debug=True, use_reloader=True, reloader_type='stat')
