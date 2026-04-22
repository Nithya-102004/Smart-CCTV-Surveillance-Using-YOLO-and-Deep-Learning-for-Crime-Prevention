from flask import Flask, render_template, flash, request, session
import sys, fsdk, math, ctypes, time, threading, winsound
from fsdk import FSDK
import mysql.connector
import datetime
import random
import os



license_key = "fVrFCzYC5wOtEVspKM/zfLWVcSIZA4RNqx74s+QngdvRiCC7z7MHlSf2w3+OUyAZkTFeD4kSpfVPcRVIqAKWUZzJG975b/P4HNNzpl11edXGIyGrTO/DImoZksDSRs6wktvgr8lnNCB5IukIPV5j/jBKlgL5aqiwSfyCR8UdC9s="

if not fsdk.windows:
	print('The program is for Microsoft Windows.'); exit(1)
import win

need_to_exit = False
camera = None
fsdkTracker = None
vfmt = None
hwnd = None
trackers = {}
inpBox = None
surfGr = None
graphics = None
backsurf = None

# Initialize FSDK once at module level
_fsdk_initialized = False
def init_fsdk():
    global _fsdk_initialized
    if not _fsdk_initialized:
        try:
            print("Initializing FSDK library... ", end='')
            FSDK.ActivateLibrary(license_key)
            FSDK.Initialize()
            try:
                FSDK.InitializeCapturing()
            except Exception as e:
                print(f"Capturing init warning: {e}")
            print("OK")
            _fsdk_initialized = True
        except Exception as e:
            print(f"FSDK init error: {e}")

def WndProc(hWnd, message, wParam, lParam):
	global capturedFace
	if message == win.WM_CTLCOLOREDIT:
		fsdkTracker.SetName(capturedFace, win.GetWindowText(inpBox))
	if message == win.WM_DESTROY:
		global need_to_exit
		need_to_exit = True
	else:
		if message == win.WM_MOUSEMOVE:
			updateActiveFace()
			return 1
		if message == win.WM_LBUTTONDOWN:
			if activeFace and capturedFace != activeFace:
				capturedFace = activeFace
				win.SetWindowText(inpBox, fsdkTracker.GetName(capturedFace))
				win.ShowWindow(inpBox, win.SW_SHOW)
				win.SetFocus(inpBox)
			else:
				capturedFace = None
				win.ShowWindow(inpBox, win.SW_HIDE)
			return 1
	return win.DefWindowProc(hWnd, message, win.WPARAM(wParam), win.LPARAM(lParam))


def dot_center(dots): # calc geometric center of dots
	return sum(p.x for p in dots)/len(dots), sum(p.y for p in dots)/len(dots)












class LowPassFilter: # low pass filter to stabilize frame size
	def __init__(self, a = 0.35): self.a, self.y = a, None
	def __call__(self, x): self.y = self.a * x + (1-self.a)*(self.y or x); return self.y

class FaceLocator:
	def __init__(self, fid):
		self.lpf = None
		self.center = self.angle = self.frame = None
		self.fid = fid
		self.is_suspicious = False
	def isIntersect(self, state):
		(x1,y1,x2,y2), (xx1,yy1,xx2,yy2) = self.frame, state.frame
		return not(x1 >= xx2 or x2 < xx1 or y1 >= yy2 or y2 < yy1)
	def isActive(self): return self.lpf is not None
	def is_inside(self, x, y):
		x -= self.center[0]; y -= self.center[1]
		a = self.angle * math.pi / 180
		x, y = x*math.cos(a) + y*math.sin(a), x*math.sin(a) - y*math.cos(a)
		return (x/self.frame[0])**2 + (y/self.frame[1])**2 <= 1
	def draw_shape(self, surf):
		container = surf.beginContainer()
		if getattr(self, 'is_suspicious', False):
			surf.translateTransform(*self.center).rotateTransform(self.angle).rectangle(faceCapturedPen, *self.frame)
		else:
			surf.translateTransform(*self.center).rotateTransform(self.angle).ellipse(facePen, *self.frame) # draw frame
			if activeFace == self.fid:
				surf.ellipse(faceActivePen, *self.frame) # draw active frame
			if capturedFace == self.fid:
				surf.ellipse(faceCapturedPen, *self.frame) # draw captured frame
		surf.endContainer(container)

	def draw(self, surf, path, face_id=None):
		if face_id is not None:
			ff = fsdkTracker.GetFacialFeatures(0, face_id)
			if self.lpf is None: self.lpf = LowPassFilter()
			xl, yl = dot_center([ff[k] for k in FSDK.FSDKP_LEFT_EYE_SET])
			xr, yr = dot_center([ff[k] for k in FSDK.FSDKP_RIGHT_EYE_SET])
			w = self.lpf((xr - xl)*2.8)
			h = w*1.4
			self.center = (xr + xl)/2, (yr + yl)/2 + w*0.05
			self.angle = math.atan2(yr-yl, xr-xl)*180/math.pi
			self.frame = -w/2, -h/2, w/2, h/2

			self.draw_shape(surf)

			name = fsdkTracker.GetName(self.fid)
			if getattr(self, 'is_suspicious', False):
				name = "Suspicious"
			#print(name)
			surf.drawString(name, font, self.center[0]-w/2+2, self.center[1]-h/2+2, text_shadow)
			surf.drawString(name, font, self.center[0]-w/2, self.center[1]-h/2, text_color)
		else:
			if self.lpf is not None: self.lpf, self.countdown = None, 35
			self.countdown -= 1
			if self.countdown <= 8:
				self.frame = [v * 0.95 for v in self.frame]
			else:
				self.draw_shape(surf)


		path.ellipse(*self.frame) # frame background
		return self.lpf or self.countdown > 0

activeFace = capturedFace = None
def updateActiveFace():
	global activeFace
	p = win.ScreenToClient(hwnd, win.GetCursorPos() )
	for fid, tr in trackers.items():
		if tr.is_inside(p.x, p.y):
			activeFace = fid
			break
	else: activeFace = None

trackers = {}
# Graphics setup moved to att()
def sendmsg(targetno, message):
    import requests
    try:
        requests.post(
            "http://sms.creativepoint.in/api/push.json?apikey=6555c521622c1&route=transsms&sender=FSSMSS&mobileno=" + targetno + "&text=Dear customer your msg is " + message + "  Sent By FSMSG FSSMSS")
    except Exception as e:
        print(f"Error sending SMS: {e}")

def send_alert_email(ss, date, timeStamp, outFileName):
    import smtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    from email.mime.base import MIMEBase
    from email import encoders

    try:
        fromaddr = "studentmailsend@gmail.com"
        toaddr = "karthikanithy1510@gmail.com"
        msg = MIMEMultipart()
        msg['From'] = fromaddr
        msg['To'] = toaddr
        msg['Subject'] = f"Alert: Criminal Found - {ss}"
        body = f"Criminal Face Found Name : {ss} Date : {date} Time : {timeStamp}"
        msg.attach(MIMEText(body, 'plain'))

        with open(outFileName, "rb") as attachment:
            p = MIMEBase('application', 'octet-stream')
            p.set_payload(attachment.read())
            encoders.encode_base64(p)
            p.add_header('Content-Disposition', f"attachment; filename= {os.path.basename(outFileName)}")
            msg.attach(p)

        s = smtplib.SMTP('smtp.gmail.com', 587)
        s.starttls()
        s.login(fromaddr, "jfrj aazz krww zkoh")
        s.sendmail(fromaddr, toaddr, msg.as_string())
        s.quit()
    except Exception as e:
        print(f"Error sending email: {e}")

def att():
    global activeFace, capturedFace, trackers, sampleNum, camera, img, surfGr, graphics, backsurf, fsdkTracker, need_to_exit, vfmt, hwnd, inpBox
    
    init_fsdk()
    
    print('Looking for video cameras... ', end = '')
    camList = FSDK.ListCameraNames()
    if not camList:
        print("Please attach a camera.")
        return
    
    camera_name = camList[0]
    formatList = FSDK.ListVideoFormats(camera_name)
    vfmt = formatList[0]
    FSDK.SetVideoFormat(camera_name, vfmt)
    
    camera = FSDK.OpenVideoCamera(camera_name)
    print("Opened camera:", camera_name)
    
    trackerMemoryFile = "tracker70.dat"
    try:
        fsdkTracker = FSDK.Tracker.FromFile(trackerMemoryFile)
    except:
        fsdkTracker = FSDK.Tracker()
    
    fsdkTracker.SetParameters(
        RecognizeFaces=True, DetectFacialFeatures=True,
        HandleArbitraryRotations=True, DetermineFaceRotationAngle=False,
        InternalResizeWidth=256, FaceDetectionThreshold=5
    )
    
    # Window setup
    try:
        wcex = win.WNDCLASSEX(cbSize=ctypes.sizeof(win.WNDCLASSEX), style=0, lpfnWndProc=win.WNDPROC(WndProc),
                              cbClsExtra=0, cbWndExtra=0, hInstance=0, hIcon=0, hCursor=win.LoadCursor(0, win.IDC_ARROW),
                              hbrBackground=0, lpszMenuName=0, lpszClassName=win.L("My Window Class"), hIconSm=0)
        win.RegisterClassEx(wcex)
    except: # Class might already be registered
        pass

    hwnd = win.CreateWindowEx(win.WS_EX_CLIENTEDGE, win.L("My Window Class"), win.L("Yolov11 response"),
                              win.WS_SYSMENU | win.WS_CAPTION | win.WS_CLIPCHILDREN,
                              100, 100, vfmt.Width, vfmt.Height, *[0] * 4)
    win.ShowWindow(hwnd, win.SW_SHOW)
    
    inpBox = win.CreateWindow(win.L("EDIT"), win.L(""), win.SS_CENTER | win.WS_CHILD, 0, 0, 0, 0, hwnd, 0, 0, 0)
    myFont = win.CreateFont(30, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, win.L("Microsoft Sans Serif"))
    win.SendMessage(inpBox, win.WM_SETFONT, myFont, True)
    win.SetWindowPos(inpBox, 0, 0, vfmt.Height - 80, vfmt.Width, 80, win.SWP_NOZORDER)
    win.UpdateWindow(hwnd)
    
    # Graphics setup
    gdiplus = win.GDIPlus()
    graphics = win.Graphics(hwnd=hwnd)
    backsurf = win.Bitmap.FromGraphics(vfmt.Width, vfmt.Height, graphics)
    surfGr = win.Graphics(bmp=backsurf).setSmoothing(True)
    
    global facePen, featurePen, brush, faceActivePen, faceCapturedPen, font, text_color, text_shadow
    facePen, featurePen, brush = win.Pen(0x60ffffff, 5), win.Pen(0xa060ff60, 1.8), win.Brush(0x28ffffff)
    faceActivePen, faceCapturedPen = win.Pen(0xFF00ff00, 2), win.Pen(0xFFff0000, 3)
    font = win.Font(win.FontFamily("Tahoma"), 30)
    text_color, text_shadow = win.Brush(0xffffffff), win.Brush(0xff808080)

    need_to_exit = False
    sampleNum = 0
    found_criminal = False
    while 1:
        sampleNum = sampleNum + 1
        img = camera.GrabFrame()
        surfGr.resetClip().drawImage(win.Bitmap.FromHBITMAP(img.GetHBitmap())) # fill backsurface with image

        faces = frozenset(fsdkTracker.FeedFrame(0, img)) # recognize all faces in the image
        for face_id in faces.difference(trackers): trackers[face_id] = FaceLocator(face_id) # create new trackers

        missed, gpath = [], win.GraphicsPath()
        for face_id, tracker in trackers.items(): # iterate over current trackers
            ss = fsdkTracker.GetName(face_id)
            # Give it a few frames to stabilize recognition
            if sampleNum > 15 and ss and ss != "Unknown" and not found_criminal:
                ts = time.time()
                date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
                timeStamp = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
                
                try:
                    conn = mysql.connector.connect(user='root', password='', host='localhost', database='1smartcrimenalyolopy(new)')
                    cursor = conn.cursor()
                    # Case-insensitive match for UserName
                    cursor.execute("select * from regtb where LOWER(userName)=LOWER(%s)", (str(ss),))
                    data = cursor.fetchone()
                    
                    if data:
                        print(f"Criminal Face Found: {ss}")
                        found_criminal = True
                        
                        # Play alarm sound
                        winsound.PlaySound('alert.wav', winsound.SND_FILENAME)
                        
                        # Background notification (SMS)
                        threading.Thread(target=sendmsg, args=('9486365535', f"Criminal Face Found! ID: {ss}")).start()
                        
                        # Prepare alert image
                        fnew = random.randint(1111, 9999)
                        outFileName = f'static/upload/{fnew}{ss}.jpg'
                        
                        bmp = win.Bitmap.FromHBITMAP(img.GetHBitmap())
                        
                        # Annotate the bitmap with the "Suspicious" box and label
                        tracker = trackers[face_id]
                        tracker.is_suspicious = True
                        temp_gpath = win.GraphicsPath()
                        temp_graphics = win.Graphics(bmp=bmp).setSmoothing(True)
                        tracker.draw(temp_graphics, temp_gpath, face_id)
                        
                        saimg = FSDK.Image(bmp.GetHBITMAP())
                        saimg.SaveToFile(outFileName, quality=85)

                        # Background email
                        threading.Thread(target=send_alert_email, args=(ss, date, timeStamp, outFileName)).start()

                        # Insert into entrytb
                        cursor.execute(
                            "insert into entrytb values('', %s, %s, %s, %s)",
                            (str(ss), str(date), str(timeStamp), outFileName))
                        conn.commit()
                        print("Entry saved to database.")
                    else:
                        print(f"Recognized face '{ss}' but not found in criminal records.")
                    
                    conn.close()
                except Exception as db_err:
                    print(f"Database error in LiveRecognition2: {db_err}")

            if face_id in faces: tracker.draw(surfGr, gpath, face_id) # draw existing tracker
            else: missed.append(face_id)
        
        for mt in missed: # find and remove trackers that are not active anymore
            st = trackers[mt]
            if any(st.isIntersect(trackers[tr]) for tr in faces) or not st.draw(surfGr, gpath): del trackers[mt]

        if capturedFace not in trackers:
            capturedFace = None
            win.ShowWindow(inpBox, win.SW_HIDE)
        updateActiveFace()

        graphics.drawImage(backsurf, 0, 0) # show backsurface
        
        # Break if we found a criminal OR if we timed out (approx 10-15 seconds)
        if found_criminal or sampleNum > 300:
            break

        msg = win.MSG()
        if win.PeekMessage(win.byref(msg), 0, 0, 0, win.PM_REMOVE):
            win.TranslateMessage(win.byref(msg))
            win.DispatchMessage(win.byref(msg))
            if msg.message == win.WM_KEYDOWN and msg.wParam == win.VK_ESCAPE or need_to_exit: break

    print("Closing session... ", end='', flush=True)
    if fsdkTracker:
        fsdkTracker.SaveToFile(trackerMemoryFile)
        fsdkTracker.Free()
    
    if hwnd:
        try:
            win.ShowWindow(hwnd, win.SW_HIDE)
            win.DestroyWindow(hwnd)
        except:
            pass

    if 'img' in globals() and img:
        try:
            img.Free()
        except:
            pass
        
    if camera:
        try:
            camera.Close()
        except:
            pass
    print("Done")

    # win.ShowWindow(hwnd, win.SW_HIDE) # Keep window visible if needed or hide it




