# 🎭 Face Recognition System

A real-time face recognition web application built with Flask, OpenCV, and face_recognition library. Features criminal detection, live video streaming, and a modern web interface with animated background.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Flask](https://img.shields.io/badge/Flask-2.3.3-green)
![OpenCV](https://img.shields.io/badge/OpenCV-4.8.1-orange)
![Face Recognition](https://img.shields.io/badge/Face--Recognition-1.3.0-red)

## ✨ Features

- **🔍 Real-time Face Detection** - Live camera feed with continuous face recognition
- **🚨 Criminal Identification** - Separate database for criminal faces with alert system
- **🎨 Modern Web Interface** - Responsive design with video background and glassmorphism effects
- **📊 Live Statistics** - Real-time detection counters and performance monitoring
- **🖥️ Fullscreen Mode** - Immersive viewing experience with ESC key support
- **⚡ Performance Optimized** - Multi-threaded processing and frame skipping
- **🔧 RESTful API** - JSON endpoints for easy integration with other systems
- **📱 Responsive Design** - Works on desktop, tablet, and mobile devices

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Webcam
- Internet connection (for CDN resources)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/face-recognition-system.git
   cd face-recognition-system
   ```

2. **Create virtual environment (recommended)**
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # Linux/Mac
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up face databases**
   ```bash
   # Create directories (automatically created on first run)
   mkdir images     # For known faces
   mkdir imageB     # For criminal faces
   ```

5. **Add your face images**
   - Place known faces in `images/` folder (jpg, jpeg, png)
   - Place criminal faces in `imageB/` folder
   - Filename will be used as display name (e.g., `john_doe.jpg` → "john_doe")

### Running the Application

```bash
python main.py
```

Open your browser and navigate to:
```
http://localhost:5000
```

## 📁 Project Structure

```
face-recognition-system/
├── main.py                 # Main Flask application & routes
├── simple_facerec.py       # Face recognition core logic
├── requirements.txt        # Python dependencies
├── README.md              # Project documentation
├── .gitignore            # Git ignore rules
├── LICENSE               # MIT License
├── images/               # Known faces database
├── imageB/               # Criminal faces database
├── templates/
│   └── index.html        # Main web interface
└── static/
    ├── style.css         # Modern CSS styling
    ├── script.js         # Frontend functionality
    └── vid.mp4          # Background video (add your own)
```

## 🛠️ API Endpoints

| Endpoint | Method | Description | Response |
|----------|--------|-------------|----------|
| `/` | GET | Main web interface | HTML page |
| `/video_feed` | GET | Live video stream | MJPEG stream |
| `/start_recognition` | GET | Start face recognition | JSON status |
| `/stop_recognition` | GET | Stop face recognition | JSON status |
| `/get_face_data` | GET | Get current face detections | JSON data |
| `/test` | GET | Test server connection | JSON status |

## 🎯 Usage Guide

### 1. **Adding Face Images**
- **Known Persons**: Add clear face images to `images/` folder
- **Criminals**: Add criminal faces to `imageB/` folder
- **Naming**: Use descriptive filenames (e.g., `john_doe.jpg`, `criminal_suspect.png`)

### 2. **Using the Web Interface**
1. **Start Recognition**: Click "Start Recognition" to begin detection
2. **Monitor Feed**: Watch real-time face detection in video feed
3. **View Statistics**: Check detection counts in the stats panel
4. **Fullscreen**: Click expand icon for immersive view
5. **Stop**: Click "Stop Recognition" when finished

### 3. **Detection Types**
- **🟢 Known Persons**: Green bounding boxes
- **🔴 Criminals**: Red bounding boxes with alert animation
- **⚪ Unknown**: No bounding box (not in database)

## 🔧 Configuration

### Camera Settings
- **Resolution**: 640x480 pixels
- **Frame Rate**: 30 FPS
- **Processing**: Every 3rd frame (performance optimization)

### Face Recognition Settings
- **Model**: HOG (CPU-efficient)
- **Tolerance**: 0.6 (lower = more strict matching)
- **Frame Resizing**: 0.5x for faster processing
- **Detection Model**: `hog` for balance of speed and accuracy

## 📊 Performance Optimization

### For Better Performance:
1. **Good Lighting**: Ensure proper illumination for camera
2. **Clear Images**: Use high-quality, front-facing images in databases
3. **Close Background Apps**: Free up system resources
4. **Wired Connection**: Use Ethernet for stable performance

### Performance Features:
- Multi-threaded face detection
- Frame skipping (process 1 of 3 frames)
- Image resizing for faster processing
- Queue-based frame handling

## 🐛 Troubleshooting

### Common Issues & Solutions

**❌ Camera Not Detected**
```bash
# Check camera permissions
sudo chmod 644 /dev/video0
# Or try different camera index
# Change in main.py: cv2.VideoCapture(1)
```

**❌ No Faces Detected**
- Ensure good lighting conditions
- Check if faces are clearly visible and front-facing
- Verify image quality in databases
- Adjust tolerance in `simple_facerec.py`

**❌ High CPU Usage**
- Application processes every 3rd frame by default
- Reduce video quality in `main.py` (line with `cv2.IMWRITE_JPEG_QUALITY`)
- Close other resource-intensive applications

**❌ Dependencies Installation Issues**
```bash
# On Windows, you might need:
pip install cmake
# Then install face_recognition
pip install face_recognition

# On Linux/Mac:
sudo apt-get install cmake  # Ubuntu/Debian
brew install cmake          # macOS
```

### Error Messages

| Error | Solution |
|-------|----------|
| "Could not open camera!" | Check camera connection/permissions |
| "No faces detected" | Improve lighting, check camera angle |
| "Encoding failed" | Use clear images with visible faces |
| "Module not found" | Install missing dependencies |

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **Commit your changes**
   ```bash
   git commit -m 'Add amazing feature'
   ```
4. **Push to the branch**
   ```bash
   git push origin feature/amazing-feature
   ```
5. **Open a Pull Request**

### Development Setup
```bash
# Install development dependencies
pip install -r requirements.txt

# Run in development mode
python main.py

# The app will auto-reload on code changes
```

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **[face_recognition](https://github.com/ageitgey/face_recognition)** - Amazing face recognition library by Adam Geitgey
- **[Flask](https://flask.palletsprojects.com/)** - Lightweight web framework
- **[OpenCV](https://opencv.org/)** - Computer vision library
- **[Font Awesome](https://fontawesome.com/)** - Beautiful icons
- **Contributors** - Thanks to all who have contributed to this project

## 🔮 Future Enhancements

- [ ] Face embedding database for faster matching
- [ ] Multiple camera support
- [ ] Cloud deployment options
- [ ] Mobile app companion
- [ ] Advanced analytics and reporting
- [ ] Integration with security systems

## 📞 Support

If you encounter any issues or have questions:

1. **Check the [Issues](https://github.com/yourusername/face-recognition-system/issues)** page
2. **Create a new issue** with detailed description
3. **Provide system information** (OS, Python version, error logs)

---

**⭐ Star this repository if you find it helpful!**

**🔔 Watch for updates and new features!**

---

<div align="center">

*Built with ❤️ using Python, Flask, and OpenCV*

</div>

## 🎥 Demo

![Demo Screenshot](https://via.placeholder.com/800x400.png?text=Face+Recognition+System+Demo)

*Live demo available at: [Your Demo Link Here]*

---

**Note**: This project is intended for educational and demonstration purposes. Always ensure compliance with local privacy laws and regulations when deploying face recognition systems.
