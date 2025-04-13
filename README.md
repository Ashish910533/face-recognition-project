Facial Recognition Attendance System
📌 Overview
This project is a Python-based Facial Recognition Attendance System that automates student attendance using real-time face detection and recognition. It captures student faces during registration and marks attendance when recognized.

🔹 Key Features
✅ Student Registration (Name, Roll No, Course, Face Capture)
✅ Real-time Attendance Marking
✅ Daily Attendance Reports (CSV Export)
✅ User-friendly GUI (Tkinter)
✅ Camera Stability Fixes (Prevents freezing)

🚀 Installation & Setup
1. Prerequisites
Python 3.8+

pip (Python package manager)

2. Install Required Libraries
Run the following command to install dependencies:

bash
Copy
pip install opencv-python face-recognition numpy pandas pillow tkcalendar datetime playsound
3. Clone the Repository
bash
Copy
git clone https://github.com/yourusername/facial-recognition-attendance.git
cd facial-recognition-attendance
4. Run the Program
bash
Copy
python AttendanceProject.py
🖥️ How to Use
1. Register Students
Click "Register New Student"

Enter Roll No, Name, and Course

Position the student in front of the camera and click "Capture and Register"

2. Take Attendance
Click "Start Attendance"

The system will automatically detect and mark attendance for recognized students

Click "Stop Attendance" when done

3. View Reports
Click "View Today's Report" to see attendance records

Export reports to CSV for further analysis

⚠️ Common Issues & Fixes
Issue	Solution
Camera not opening	Ensure no other app is using the camera. Try cv2.CAP_DSHOW
Face not detected	Ensure proper lighting and face alignment
CSV file errors	Delete corrupted files in attendance_db/
Slow performance	Reduce camera resolution (CAP_PROP_FRAME_WIDTH/HEIGHT)
Duplicate entries	System prevents duplicate roll numbers
📂 Project Structure
Copy
facial-recognition-attendance/  
├── attendance_db/          # Attendance records (CSV)  
├── known_faces/            # Registered student faces  
├── student_data/           # Student details (CSV)  
├── AttendanceProject.py     # Main Python script  
└── README.md               # This file  
📜 License
This project is licensed under MIT License.

📧 Contact
For any issues or suggestions, feel free to reach out:
📩 Email: your-email@example.com
🔗 GitHub: github.com/yourusername

🎉 Happy Coding! 🚀
🔹 Additional Notes
Tested on Windows 10/11 with Python 3.10

Works best with well-lit environments

For Linux/Mac, remove cv2.CAP_DSHOW

Would you like any modifications or additional details? 😊
