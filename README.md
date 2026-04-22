# Smart-CCTV-Surveillance-Using-YOLO-and-Deep-Learning-for-Crime-Prevention

A comprehensive web-based application built with **Flask**, **YOLOv11**, and **OpenCV** designed to detect criminal faces and identify dangerous actions (like holding weapons) in real-time. The system uses a MySQL database to log entries and manage registered individuals.

## 🚀 Features

- **Real-Time Detection:** Live webcam feed analysis using OpenCV.
- **Dangerous Action/Weapon Detection:** Utilizes customized YOLOv11 models to spot weapons and dangerous actions.
- **Face Recognition:** Identifies known individuals (using a specialized face SDK) and logs their presence.
- **Web Interface:** A user-friendly dashboard built with Flask, HTML, and CSS to manage users, view logs, and configure the system.
- **Database Integration:** Seamlessly connects to a MySQL database (via XAMPP) to store registration details (`regtb`) and entry logs (`entrytb`).

## 🛠️ Tech Stack

- **Backend:** Python, Flask
- **Computer Vision:** OpenCV, Ultralytics YOLOv11, PyTorch
- **Frontend:** HTML5, CSS3, Jinja2 Templates
- **Database:** MySQL (XAMPP)

## 📂 Dataset

The dataset used for training the YOLO model is stored externally due to its large size.

🔗 **Dataset Link:**  
https://universe.roboflow.com/dangerous-and-suspicious-action-detection-ayjbl/dangerous-action-detection

This dataset contains CCTV images and videos used for training crime detection and weapon detection models.

## 📋 Prerequisites

Before running the application, ensure you have the following installed:
1. **Python 3.8+**
2. **XAMPP** (for the MySQL database)
3. A working webcam

## ⚙️ Installation & Setup

1. **Clone the repository** (or navigate to the project directory):
   ```bash
   cd DangerousActionCrimeFacePy
   ```

2. **Set up the Database:**
   - Open XAMPP Control Panel and start the **Apache** and **MySQL** modules.
   - Open phpMyAdmin (`http://localhost/phpmyadmin`).
   - Create a new database named: `1smartcrimenalyolopy(new)`
   - Import the provided SQL file (`1smartcrimenalyolopy(new).sql`) into this database to create the necessary tables (`regtb` and `entrytb`).

3. **Install Python Dependencies:**
   It is recommended to use a virtual environment. If you don't have one, create it and install the requirements:
   ```bash
   # Create virtual environment (optional but recommended)
   python -m venv venv
   
   # Activate it (Windows)
   venv\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   ```

## ▶️ Running the Application

Once the database is running and dependencies are installed, you can start the Flask web server:

```bash
python App.py
```

The application will typically be accessible in your web browser at `http://127.0.0.1:5000/`.

## 🧠 Model Training (Optional)
If you wish to retrain the YOLO model on a custom dataset, you can use the commands located in `run.txt`. Example:
```bash
yolo train model=yolo11n.pt data=datasets/data.yaml epochs=20 imgsz=640 device=0 batch=2 amp=True
```

## 📂 Project Structure

- `App.py` - Main Flask application entry point.
- `LiveRecognition.py` / `LiveRecognition2.py` / `DangerousPy.py` - Core scripts for handling webcam feeds and running YOLO/Face recognition models.
- `templates/` - HTML files for the web interface.
- `static/` - CSS, images, and other static web assets.
- `datasets/` - Training data for custom YOLO models.
- `runs/` - Output directory for YOLO inference and training logs.
- `requirements.txt` - Python package dependencies.
- `1smartcrimenalyolopy(new).sql` - Database schema file.
