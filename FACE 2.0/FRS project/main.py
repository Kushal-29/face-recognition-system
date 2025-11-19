from flask import Flask, render_template, Response, jsonify
import cv2
import os
import glob
import numpy as np
import threading
import time
import queue
import face_recognition  # ⚠️ THIS WAS MISSING! ⚠️

app = Flask(__name__)

# Global variables
camera = None
is_running = False
latest_frame = None
face_data = []
frame_queue = queue.Queue(maxsize=1)

class SimpleFacerec:
    def __init__(self):
        self.known_face_encodings = []
        self.known_face_names = []
        self.frame_resizing = 0.5

    def load_encoding_images(self, images_path):
        if not os.path.exists(images_path):
            print(f"❌ Directory {images_path} does not exist!")
            return
            
        image_files = glob.glob(os.path.join(images_path, "*.*"))
        image_files = [f for f in image_files if f.lower().endswith(('.jpg', '.jpeg', '.png'))]

        print(f"📁 {len(image_files)} valid image files found in '{images_path}'.")

        for img_path in image_files:
            print(f"🔄 Processing {img_path}...")
            img = cv2.imread(img_path)

            if img is None:
                print(f"⚠️ Warning: Could not load image '{img_path}'. Skipping.")
                continue

            # Resize image for faster processing
            img = cv2.resize(img, (0, 0), fx=0.5, fy=0.5)
            rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

            try:
                # Find face encodings
                face_encodings = face_recognition.face_encodings(rgb_img)
                
                if len(face_encodings) == 0:
                    print(f"⚠️ No face found in image '{img_path}'. Skipping.")
                    continue
                
                # Get the first face encoding
                img_encoding = face_encodings[0]
                
                # Get filename without extension
                basename = os.path.basename(img_path)
                filename = os.path.splitext(basename)[0]

                self.known_face_encodings.append(img_encoding)
                self.known_face_names.append(filename)
                
                print(f"✅ Encoded: {filename}")

            except Exception as e:
                print(f"❌ Error processing {img_path}: {e}")

        print(f"🎉 Encoding completed! Loaded {len(self.known_face_encodings)} faces from '{images_path}'")

    def load_encoding_criminals(self, images_path):
        if not os.path.exists(images_path):
            print(f"❌ Directory {images_path} does not exist!")
            return
            
        image_files = glob.glob(os.path.join(images_path, "*.*"))
        image_files = [f for f in image_files if f.lower().endswith(('.jpg', '.jpeg', '.png'))]

        print(f"📁 {len(image_files)} valid image files found in '{images_path}'.")

        for img_path in image_files:
            print(f"🔄 Processing criminal {img_path}...")
            img = cv2.imread(img_path)

            if img is None:
                print(f"⚠️ Warning: Could not load image '{img_path}'. Skipping.")
                continue

            # Resize image for faster processing
            img = cv2.resize(img, (0, 0), fx=0.5, fy=0.5)
            rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

            try:
                # Find face encodings
                face_encodings = face_recognition.face_encodings(rgb_img)
                
                if len(face_encodings) == 0:
                    print(f"⚠️ No face found in image '{img_path}'. Skipping.")
                    continue
                
                # Get the first face encoding
                img_encoding = face_encodings[0]
                
                # Get filename without extension
                basename = os.path.basename(img_path)
                filename = os.path.splitext(basename)[0]

                self.known_face_encodings.append(img_encoding)
                self.known_face_names.append("Criminal: " + filename)
                
                print(f"✅ Encoded Criminal: {filename}")

            except Exception as e:
                print(f"❌ Error processing {img_path}: {e}")

        print(f"🎉 Criminal encoding completed! Loaded {len([name for name in self.known_face_names if 'Criminal:' in name])} criminals")

    def detect_known_faces(self, frame):
        try:
            # Resize frame for faster processing
            small_frame = cv2.resize(frame, (0, 0), fx=self.frame_resizing, fy=self.frame_resizing)
            rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

            # Find all face locations
            face_locations = face_recognition.face_locations(rgb_small_frame, model="hog")
            
            # If no faces found, return empty
            if not face_locations:
                print("🔍 No faces detected in frame")
                return [], []

            # Get face encodings for detected faces
            face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

            face_names = []
            for face_encoding in face_encodings:
                # Compare with known faces
                matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding, tolerance=0.6)
                name = "Unknown"

                # Find the best match
                face_distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)
                if len(face_distances) > 0:
                    best_match_index = np.argmin(face_distances)
                    if matches[best_match_index]:
                        name = self.known_face_names[best_match_index]

                face_names.append(name)

            # Convert face locations back to original frame size
            face_locations = np.array(face_locations)
            face_locations = (face_locations / self.frame_resizing).astype(int)
            
            print(f"🔍 Detected {len(face_names)} faces: {face_names}")
            
            return face_locations, face_names
            
        except Exception as e:
            print(f"❌ Face detection error: {e}")
            return [], []

# Initialize face recognition
sfr = SimpleFacerec()

class Camera:
    def __init__(self):
        self.cap = None
        self.is_active = False
    
    def start(self):
        if not self.is_active:
            try:
                self.cap = cv2.VideoCapture(0)
                if not self.cap.isOpened():
                    print("❌ Error: Could not open camera!")
                    return False
                    
                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                self.cap.set(cv2.CAP_PROP_FPS, 30)
                self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                self.is_active = True
                print("✅ Camera started successfully!")
                return True
            except Exception as e:
                print(f"❌ Camera start error: {e}")
                return False
    
    def stop(self):
        if self.is_active:
            self.cap.release()
            self.is_active = False
            print("🛑 Camera stopped")
    
    def get_frame(self):
        if self.is_active and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                return frame
        return None

camera = Camera()

def face_detection_worker():
    """Separate thread for face detection to prevent lag"""
    global latest_frame, face_data
    while is_running:
        try:
            frame = frame_queue.get(timeout=1.0)
            if frame is not None:
                print("🔄 Processing frame for face detection...")
                face_locations, face_names = sfr.detect_known_faces(frame)
                
                face_data = [{"name": name, "type": "criminal" if "Criminal:" in name else "known"} 
                            for name in face_names]
                
                # Draw on frame
                for (top, right, bottom, left), name in zip(face_locations, face_names):
                    if "Criminal:" in name:
                        color = (0, 0, 255)  # Red for criminals
                        thickness = 3
                        font_scale = 0.8
                    else:
                        color = (0, 255, 0)  # Green for known
                        thickness = 2
                        font_scale = 0.7
                    
                    cv2.rectangle(frame, (left, top), (right, bottom), color, thickness)
                    cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, font_scale, color, thickness)
                    print(f"🎯 Drawing box for: {name}")
                
                latest_frame = frame
                
        except queue.Empty:
            continue
        except Exception as e:
            print(f"❌ Face detection worker error: {e}")
            continue

def generate_frames():
    """Stream frames with minimal processing"""
    frame_count = 0
    while is_running:
        frame = camera.get_frame()
        if frame is not None:
            # Only process every 3rd frame for face detection (reduces CPU load)
            if frame_count % 3 == 0:  # Process 1 out of 3 frames
                try:
                    # Non-blocking put to queue
                    if not frame_queue.full():
                        frame_queue.put(frame.copy(), block=False)
                except queue.Full:
                    pass  # Skip this frame if queue is full
            
            # Use the latest processed frame if available, otherwise use raw frame
            display_frame = latest_frame if latest_frame is not None else frame
            
            # Encode frame for streaming (lower quality for better performance)
            ret, buffer = cv2.imencode('.jpg', display_frame, [
                cv2.IMWRITE_JPEG_QUALITY, 70  # Lower quality for speed
            ])
            frame_bytes = buffer.tobytes()
            
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            
            frame_count += 1
        else:
            # Send a blank frame if camera fails
            blank_frame = np.zeros((480, 640, 3), dtype=np.uint8)
            ret, buffer = cv2.imencode('.jpg', blank_frame)
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        
        time.sleep(0.033)  # ~30 FPS

# Face detection thread
face_thread = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/start_recognition')
def start_recognition():
    global is_running, face_thread
    if not is_running:
        # Load encodings first time
        if not sfr.known_face_encodings:
            print("🔄 Loading face encodings...")
            sfr.load_encoding_images("images/")
            sfr.load_encoding_criminals("imageB/")
            print("✅ Face encodings loaded!")
        
        if camera.start():
            is_running = True
            face_thread = threading.Thread(target=face_detection_worker, daemon=True)
            face_thread.start()
            return jsonify({"status": "started", "message": "Face recognition started successfully!"})
        else:
            return jsonify({"status": "error", "message": "Failed to start camera!"})
    return jsonify({"status": "already_running", "message": "Recognition is already running!"})

@app.route('/stop_recognition')
def stop_recognition():
    global is_running
    if is_running:
        is_running = False
        camera.stop()
        while not frame_queue.empty():
            try:
                frame_queue.get_nowait()
            except queue.Empty:
                break
        return jsonify({"status": "stopped", "message": "Face recognition stopped!"})
    return jsonify({"status": "already_stopped", "message": "Recognition is not running!"})

@app.route('/get_face_data')
def get_face_data():
    return jsonify({"faces": face_data})

@app.route('/test')
def test():
    return jsonify({"status": "success", "message": "Flask server is working!"})

if __name__ == '__main__':
    print("🚀 Starting Face Recognition Web App...")
    print("📁 Checking directories...")
    
    # Check if directories exist
    if not os.path.exists("images"):
        print("⚠️  'images' directory not found! Creating...")
        os.makedirs("images")
    
    if not os.path.exists("imageB"):
        print("⚠️  'imageB' directory not found! Creating...")
        os.makedirs("imageB")
    
    if not os.path.exists("templates"):
        print("⚠️  'templates' directory not found! Creating...")
        os.makedirs("templates")
    
    if not os.path.exists("static"):
        print("⚠️  'static' directory not found! Creating...")
        os.makedirs("static")
    
    print("✅ All directories checked!")
    print("🌐 Open your browser and go to: http://localhost:5000")
    print("🔧 Test connection: http://localhost:5000/test")
    print("💡 Make sure you have clear face images in 'images/' and 'imageB/' folders!")
    
    try:
        app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)
    except Exception as e:
        print(f"❌ Error starting server: {e}")