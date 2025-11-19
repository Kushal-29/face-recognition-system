import face_recognition
import cv2
import os
import glob
import numpy as np

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