import os
import cv2
import face_recognition
import numpy as np
import pandas as pd
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
from PIL import Image, ImageTk

class StudentAttendanceSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Student Attendance System")
        self.root.geometry("1100x750")
        
        # Setup directories first
        self.setup_directories()
        
        # Initialize face data
        self.known_face_encodings = []
        self.known_face_data = []  # Will store dictionaries with student data
        
        # GUI setup must come before loading faces
        self.setup_gui()
        
        # Now load known faces
        self.load_known_faces()
        
        # Camera setup
        self.video_capture = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # Added CAP_DSHOW for better camera handling
        self.video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.current_frame = None
        self.is_running = False
        self.last_frame_time = datetime.now()
        
        # Start video feed
        self.update_video_feed()
    
    def setup_directories(self):
        """Create necessary directories if they don't exist"""
        os.makedirs("attendance_db", exist_ok=True)
        os.makedirs("known_faces", exist_ok=True)
        os.makedirs("student_data", exist_ok=True)
    
    def setup_gui(self):
        """Setup the user interface with enhanced controls"""
        # Main frames
        main_frame = tk.Frame(self.root, bg="#f0f0f0")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left panel - Video feed
        left_frame = tk.Frame(main_frame, bg="#f0f0f0")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.video_frame = tk.LabelFrame(left_frame, text="Camera Feed", bg="#f0f0f0")
        self.video_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.video_label = tk.Label(self.video_frame)
        self.video_label.pack()
        
        # Right panel - Controls
        right_frame = tk.Frame(main_frame, bg="#f0f0f0", width=300)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=5, pady=5)
        
        # Student info display
        info_frame = tk.LabelFrame(right_frame, text="Student Info", bg="#f0f0f0")
        info_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.info_text = tk.Text(info_frame, height=5, width=30)
        self.info_text.pack(fill=tk.X)
        self.info_text.config(state=tk.DISABLED)
        
        # Control buttons
        control_frame = tk.LabelFrame(right_frame, text="Controls", bg="#f0f0f0")
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.start_btn = tk.Button(control_frame, text="Start Attendance", 
                                 command=self.start_attendance, width=20)
        self.start_btn.pack(pady=5)
        
        self.stop_btn = tk.Button(control_frame, text="Stop Attendance", 
                                command=self.stop_attendance, width=20, state=tk.DISABLED)
        self.stop_btn.pack(pady=5)
        
        self.add_user_btn = tk.Button(control_frame, text="Register New Student", 
                                    command=self.register_student, width=20)
        self.add_user_btn.pack(pady=5)
        
        self.report_btn = tk.Button(control_frame, text="View Today's Report", 
                                  command=self.view_report, width=20)
        self.report_btn.pack(pady=5)
        
        # Status label
        self.status_label = tk.Label(right_frame, text="Status: Ready", bg="#f0f0f0", fg="blue")
        self.status_label.pack(pady=5)
        
        # Attendance log
        log_frame = tk.LabelFrame(right_frame, text="Attendance Log", bg="#f0f0f0")
        log_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.log_text = tk.Text(log_frame, height=12, width=30)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        self.log_text.config(state=tk.DISABLED)
    
    def load_known_faces(self):
        """Load known faces from the known_faces directory and student data"""
        self.known_face_encodings = []
        self.known_face_data = []
        
        try:
            # Load student data from CSV
            student_data_file = "student_data/students.csv"
            if os.path.exists(student_data_file):
                df = pd.read_csv(student_data_file)
                
                for _, row in df.iterrows():
                    image_path = os.path.join("known_faces", f"{row['roll_no']}.jpg")
                    if os.path.exists(image_path):
                        image = face_recognition.load_image_file(image_path)
                        encodings = face_recognition.face_encodings(image)
                        
                        if len(encodings) > 0:
                            self.known_face_encodings.append(encodings[0])
                            self.known_face_data.append({
                                'roll_no': str(row['roll_no']),  # Ensure roll_no is string
                                'name': row['name'],
                                'course': row['course'],
                                'image_path': image_path
                            })
            
            self.log_message(f"Loaded {len(self.known_face_data)} student records")
        except Exception as e:
            self.log_message(f"Error loading student data: {str(e)}")
    
    def register_student(self):
        """Register a new student with additional details"""
        if self.is_running:
            messagebox.showwarning("System Running", "Please stop the system first")
            return
        
        # Create registration window
        reg_window = tk.Toplevel(self.root)
        reg_window.title("Register New Student")
        reg_window.geometry("400x500")
        
        # Form fields
        tk.Label(reg_window, text="Roll Number:").pack(pady=(10, 0))
        roll_no_entry = tk.Entry(reg_window)
        roll_no_entry.pack()
        
        tk.Label(reg_window, text="Full Name:").pack(pady=(10, 0))
        name_entry = tk.Entry(reg_window)
        name_entry.pack()
        
        tk.Label(reg_window, text="Course:").pack(pady=(10, 0))
        course_entry = tk.Entry(reg_window)
        course_entry.pack()
        
        # Image preview
        preview_frame = tk.Frame(reg_window)
        preview_frame.pack(pady=10)
        
        preview_label = tk.Label(preview_frame)
        preview_label.pack()
        
        # Capture button
        def capture_student():
            roll_no = roll_no_entry.get().strip()
            name = name_entry.get().strip()
            course = course_entry.get().strip()
            
            if not all([roll_no, name, course]):
                messagebox.showwarning("Missing Information", "Please fill all fields")
                return
            
            # Capture image
            ret, frame = self.video_capture.read()
            if ret:
                # Check if face is detected
                rgb_frame = frame[:, :, ::-1]
                face_locations = face_recognition.face_locations(rgb_frame)
                
                if not face_locations:
                    messagebox.showwarning("No Face", "No face detected in the image")
                    return
                
                # Save student data to CSV
                student_data_file = "student_data/students.csv"
                new_data = pd.DataFrame([{
                    'roll_no': roll_no,
                    'name': name,
                    'course': course
                }])
                
                if os.path.exists(student_data_file):
                    existing_data = pd.read_csv(student_data_file)
                    if roll_no in existing_data['roll_no'].values:
                        messagebox.showwarning("Duplicate", "Roll number already exists")
                        return
                    combined_data = pd.concat([existing_data, new_data])
                else:
                    combined_data = new_data
                
                combined_data.to_csv(student_data_file, index=False)
                
                # Save the image (use roll number as filename)
                image_path = os.path.join("known_faces", f"{roll_no}.jpg")
                cv2.imwrite(image_path, frame)
                
                # Reload known faces
                self.load_known_faces()
                
                messagebox.showinfo("Success", "Student registered successfully!")
                reg_window.destroy()
        
        tk.Button(reg_window, text="Capture and Register", 
                 command=capture_student).pack(pady=10)
        
        # Update preview
        def update_preview():
            ret, frame = self.video_capture.read()
            if ret:
                # Resize for preview
                preview_frame = cv2.resize(frame, (300, 300))
                preview_frame = cv2.cvtColor(preview_frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(preview_frame)
                imgtk = ImageTk.PhotoImage(image=img)
                
                preview_label.imgtk = imgtk
                preview_label.configure(image=imgtk)
            
            reg_window.after(50, update_preview)
        
        update_preview()
    
    def update_video_feed(self):
        """Update the video feed in the GUI with camera stability fixes"""
        try:
            if self.is_running:
                current_time = datetime.now()
                time_diff = (current_time - self.last_frame_time).total_seconds()
                
                # Skip frame processing if we're getting frames too fast
                if time_diff < 0.033:  # About 30fps
                    self.root.after(10, self.update_video_feed)
                    return
                
                self.last_frame_time = current_time
                
                # Release and reopen camera if it's stuck
                if not self.video_capture.isOpened():
                    self.video_capture.release()
                    self.video_capture = cv2.VideoCapture(0, cv2.CAP_DSHOW)
                    self.video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                    self.video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                
                ret, frame = self.video_capture.read()
                if not ret:
                    self.log_message("Camera error: Could not read frame")
                    self.root.after(100, self.update_video_feed)
                    return
                
                # Process every other frame to reduce CPU load
                small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
                rgb_small_frame = small_frame[:, :, ::-1]
                
                # Find all faces in the frame
                face_locations = face_recognition.face_locations(rgb_small_frame)
                face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
                
                for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
                    # Compare with known faces
                    matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding)
                    name = "Unknown"
                    roll_no = ""
                    course = ""
                    
                    # Use the known face with the smallest distance
                    face_distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)
                    best_match_index = np.argmin(face_distances)
                    
                    if matches[best_match_index] and face_distances[best_match_index] < 0.6:
                        student = self.known_face_data[best_match_index]
                        name = student['name']
                        roll_no = student['roll_no']
                        course = student['course']
                        self.mark_attendance(roll_no, name, course)
                    
                    # Draw rectangle and label on the frame
                    top *= 4
                    right *= 4
                    bottom *= 4
                    left *= 4
                    cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                    cv2.putText(frame, f"{name} ({roll_no})", (left + 6, bottom - 6), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                
                # Display the frame
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame)
                imgtk = ImageTk.PhotoImage(image=img)
                
                self.video_label.imgtk = imgtk
                self.video_label.configure(image=imgtk)
            
            self.root.after(10, self.update_video_feed)
        except Exception as e:
            self.log_message(f"Video feed error: {str(e)}")
            self.root.after(100, self.update_video_feed)
    
    def mark_attendance(self, roll_no, name, course):
        """Record attendance for a recognized student with proper CSV handling"""
        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%H:%M:%S")
        
        # Save to CSV file
        file_path = f"attendance_db/attendance_{date_str}.csv"
        
        try:
            # Check if already marked today
            marked_today = False
            if os.path.exists(file_path):
                try:
                    df = pd.read_csv(file_path)
                    if not df.empty and str(roll_no) in df['Roll No'].astype(str).values:
                        marked_today = True
                except:
                    # If CSV is corrupted, create a new one
                    with open(file_path, 'w') as f:
                        f.write("Roll No,Name,Course,Time\n")
            
            if not marked_today:
                # Record attendance
                with open(file_path, 'a') as f:
                    if os.stat(file_path).st_size == 0:
                        f.write("Roll No,Name,Course,Time\n")
                    f.write(f"{roll_no},{name},{course},{time_str}\n")
                
                # Update student info display
                self.info_text.config(state=tk.NORMAL)
                self.info_text.delete(1.0, tk.END)
                self.info_text.insert(tk.END, f"Roll No: {roll_no}\nName: {name}\nCourse: {course}\nTime: {time_str}")
                self.info_text.config(state=tk.DISABLED)
                
                self.log_message(f"{name} ({roll_no}) marked present")
        except Exception as e:
            self.log_message(f"Error saving attendance: {str(e)}")
    
    def view_report(self):
        """View today's attendance report with proper error handling"""
        date_str = datetime.now().strftime("%Y-%m-%d")
        file_path = f"attendance_db/attendance_{date_str}.csv"
        
        if not os.path.exists(file_path):
            messagebox.showinfo("No Data", "No attendance data for today")
            return
            
        try:
            # Read CSV with proper error handling
            df = pd.read_csv(file_path)
            
            # Create report window
            report_window = tk.Toplevel(self.root)
            report_window.title(f"Attendance Report - {date_str}")
            report_window.geometry("700x400")
            
            # Create treeview for tabular display
            tree = ttk.Treeview(report_window, columns=("Roll No", "Name", "Course", "Time"), show="headings")
            tree.heading("Roll No", text="Roll No")
            tree.heading("Name", text="Name")
            tree.heading("Course", text="Course")
            tree.heading("Time", text="Time")
            
            tree.column("Roll No", width=100, anchor='center')
            tree.column("Name", width=200, anchor='center')
            tree.column("Course", width=200, anchor='center')
            tree.column("Time", width=100, anchor='center')
            
            # Add data
            for _, row in df.iterrows():
                tree.insert("", tk.END, values=(
                    str(row.get('Roll No', '')),
                    str(row.get('Name', '')),
                    str(row.get('Course', '')),
                    str(row.get('Time', ''))
                ))
            
            tree.pack(fill=tk.BOTH, expand=True)
            
            # Add scrollbar
            scrollbar = ttk.Scrollbar(report_window, orient=tk.VERTICAL, command=tree.yview)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            tree.configure(yscrollcommand=scrollbar.set)
            
            # Add export button
            def export_to_csv():
                save_path = filedialog.asksaveasfilename(
                    defaultextension=".csv",
                    filetypes=[("CSV files", "*.csv")],
                    title="Save report as CSV"
                )
                if save_path:
                    try:
                        df.to_csv(save_path, index=False)
                        messagebox.showinfo("Success", f"Report saved to {save_path}")
                    except Exception as e:
                        messagebox.showerror("Error", f"Failed to save: {str(e)}")
            
            export_btn = tk.Button(report_window, text="Export to CSV", command=export_to_csv)
            export_btn.pack(pady=5)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load report: {str(e)}")
    
    def log_message(self, message):
        """Add a message to the log"""
        if hasattr(self, 'log_text'):
            self.log_text.config(state=tk.NORMAL)
            self.log_text.insert(tk.END, f"{datetime.now().strftime('%H:%M:%S')} - {message}\n")
            self.log_text.config(state=tk.DISABLED)
            self.log_text.see(tk.END)
    
    def start_attendance(self):
        """Start the attendance system"""
        if not self.known_face_data:
            messagebox.showwarning("No Students", "Please register students first")
            return
            
        self.is_running = True
        self.status_label.config(text="Status: Running", fg="green")
        self.log_message("Attendance system started")
        
        # Enable/disable buttons
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
    
    def stop_attendance(self):
        """Stop the attendance system"""
        self.is_running = False
        self.status_label.config(text="Status: Ready", fg="blue")
        self.log_message("Attendance system stopped")
        
        # Enable/disable buttons
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
    
    def on_closing(self):
        """Cleanup when closing the application"""
        if self.video_capture.isOpened():
            self.video_capture.release()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = StudentAttendanceSystem(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()