import cv2
import time
from ultralytics import YOLO
from tkinter import *
from tkinter import filedialog
import winsound

model = YOLO('runs/detect/weapon/weights/best.pt')

MOBILE_STREAM = "http://192.168.1.28:8080/stream.mjpeg"



def run_mobile_yolo(url):
    cap = cv2.VideoCapture(url)

    time.sleep(1)

    if not cap.isOpened():
        print("Error: Cannot open mobile stream")
        return

    dd1 = 0


    cv2.namedWindow("Mobile YOLO Detection", cv2.WINDOW_AUTOSIZE)

    while True:
        ret, frame = cap.read()
        if not ret or frame is None:
            print("Waiting for mobile stream...")
            continue


        results = model(frame, conf=0.4)

        for result in results:
            if result.boxes:
                box = result.boxes[0]
                class_id = int(box.cls)
                object_name = model.names[class_id]
                print(object_name)

                if object_name != "person":
                    dd1 += 1

                if dd1 == 30:
                    dd1 = 0
                    annotated = results[0].plot()
                    #winsound.PlaySound("alert.wav", winsound.SND_FILENAME)
                    cv2.imwrite("alert.jpg", annotated)
                    send_email_alert()

        annotated_frame = results[0].plot()


        cv2.imshow("Mobile YOLO Detection", annotated_frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()

def send_email_alert():
    import smtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    from email.mime.base import MIMEBase
    from email import encoders

    fromaddr = "projectmailm@gmail.com"
    toaddr = "fantasypythonprojects@gmail.com"

    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = toaddr
    msg['Subject'] = "Alert"

    body = "Danger Action Detected"
    msg.attach(MIMEText(body, 'plain'))

    filename = "alert.jpg"
    attachment = open("alert.jpg", "rb")

    p = MIMEBase('application', 'octet-stream')
    p.set_payload((attachment).read())
    encoders.encode_base64(p)
    p.add_header('Content-Disposition', "attachment; filename= %s" % filename)
    msg.attach(p)

    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.starttls()
    s.login(fromaddr, "tdyr kebi hnyr yzyh")
    text = msg.as_string()
    s.sendmail(fromaddr, toaddr, text)
    s.quit()




def run_yolo(video_path):
    cap = cv2.VideoCapture(video_path)
    dd1 = 0

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break

        results = model(frame, conf=0.4)

        for result in results:
            if result.boxes:
                box = result.boxes[0]
                class_id = int(box.cls)
                object_name = model.names[class_id]

                if object_name == 'person':
                    dd1 += 1

                if dd1 == 30:
                    dd1 = 0
                    annotated_frame = results[0].plot()
                    #winsound.PlaySound("alert.wav", winsound.SND_FILENAME)
                    cv2.imwrite("alert.jpg", annotated_frame)
                    send_email_alert()

        annotated_frame = results[0].plot()
        display_frame = cv2.resize(annotated_frame, (960, 540))
        cv2.imshow("YOLO Video Detection", display_frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()



def Camera1():
    run_mobile_yolo(MOBILE_STREAM)


def UploadVideo():
    file_path = filedialog.askopenfilename(
        title="Select Video File",
        filetypes=[("Video Files", "*.mp4 *.avi *.mov *.mkv")]
    )
    if file_path:
        run_yolo(file_path)



def main_account_screen():
    global main_screen
    main_screen = Tk()
    width = 600
    height = 600
    screen_width = main_screen.winfo_screenwidth()
    screen_height = main_screen.winfo_screenheight()
    x = (screen_width / 2) - (width / 2)
    y = (screen_height / 2) - (height / 2)
    main_screen.geometry("%dx%d+%d+%d" % (width, height, x, y))
    main_screen.resizable(0, 0)
    main_screen.title("Danger Action Detection")

    Label(text="Danger Action Detection", width="300", height="5",
          font=("Calibri", 16)).pack()

    Label(text="").pack()

    Button(text="Mobile Camera Detection", font=('Verdana', 15),
           height="2", width="30", command=Camera1).pack()



    main_screen.mainloop()


main_account_screen()

