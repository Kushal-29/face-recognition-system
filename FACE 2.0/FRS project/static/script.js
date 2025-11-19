class FaceRecognitionApp {
    constructor() {
        this.isRunning = false;
        this.videoFeed = document.getElementById('videoFeed');
        this.videoOverlay = document.getElementById('videoOverlay');
        this.initializeEventListeners();
        this.setupFullscreen();
        this.setupPerformanceMonitoring();
        this.startFaceDataPolling();
        this.checkServerStatus();
        this.setupBackgroundVideo();
    }

    setupBackgroundVideo() {
        const bgVideo = document.getElementById('bgVideo');
        
        // Force video to play and handle errors
        bgVideo.play().catch(error => {
            console.log('Background video autoplay failed:', error);
            // Add click event to start video
            document.body.addEventListener('click', function() {
                bgVideo.play().catch(e => console.log('Still cannot play video:', e));
            }, { once: true });
        });

        // Fallback if video fails to load
        bgVideo.addEventListener('error', function() {
            console.error('Background video failed to load');
            document.body.style.background = "linear-gradient(135deg, #1a2a6c, #b21f1f, #fdbb2d)";
        });
    }

    initializeEventListeners() {
        document.getElementById('startBtn').addEventListener('click', () => this.startRecognition());
        document.getElementById('stopBtn').addEventListener('click', () => this.stopRecognition());
        document.getElementById('testBtn').addEventListener('click', () => this.testConnection());
    }

    setupFullscreen() {
        const fullscreenBtn = document.getElementById('fullscreenBtn');
        const videoWrapper = document.getElementById('videoWrapper');
        
        fullscreenBtn.addEventListener('click', () => this.toggleFullscreen());
        
        // ESC key to exit fullscreen
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && document.fullscreenElement) {
                this.exitFullscreen();
            }
        });
        
        // Fullscreen change event
        document.addEventListener('fullscreenchange', () => {
            this.handleFullscreenChange();
        });
    }

    toggleFullscreen() {
        const videoWrapper = document.getElementById('videoWrapper');
        
        if (!document.fullscreenElement) {
            this.enterFullscreen(videoWrapper);
        } else {
            this.exitFullscreen();
        }
    }

    enterFullscreen(element) {
        if (element.requestFullscreen) {
            element.requestFullscreen();
        } else if (element.webkitRequestFullscreen) {
            element.webkitRequestFullscreen();
        } else if (element.msRequestFullscreen) {
            element.msRequestFullscreen();
        }
    }

    exitFullscreen() {
        if (document.exitFullscreen) {
            document.exitFullscreen();
        } else if (document.webkitExitFullscreen) {
            document.webkitExitFullscreen();
        } else if (document.msExitFullscreen) {
            document.msExitFullscreen();
        }
    }

    handleFullscreenChange() {
        const videoWrapper = document.getElementById('videoWrapper');
        const fullscreenBtn = document.getElementById('fullscreenBtn');
        const fullscreenIcon = fullscreenBtn.querySelector('i');
        
        if (document.fullscreenElement) {
            videoWrapper.classList.add('fullscreen');
            document.body.classList.add('fullscreen-mode');
            fullscreenIcon.className = 'fas fa-compress';
            fullscreenBtn.title = 'Exit Fullscreen (ESC)';
        } else {
            videoWrapper.classList.remove('fullscreen');
            document.body.classList.remove('fullscreen-mode');
            fullscreenIcon.className = 'fas fa-expand';
            fullscreenBtn.title = 'Enter Fullscreen';
        }
    }

    async checkServerStatus() {
        try {
            const response = await fetch('/test');
            const data = await response.json();
            if (data.status === 'success') {
                this.updateCameraStatus('Server Connected', '#4CAF50');
            }
        } catch (error) {
            this.updateCameraStatus('Server Error', '#f44336');
            console.error('Server status check failed:', error);
        }
    }

    async testConnection() {
        this.showNotification('Testing connection...', 'info');
        try {
            const response = await fetch('/test');
            const data = await response.json();
            this.showNotification('✅ Server is working!', 'success');
        } catch (error) {
            this.showNotification('❌ Server connection failed!', 'error');
            console.error('Test connection failed:', error);
        }
    }

    async startRecognition() {
        this.showNotification('Starting face recognition...', 'info');
        this.updateCameraStatus('Starting...', '#FF9800');
        
        try {
            const response = await fetch('/start_recognition');
            const data = await response.json();
            
            if (data.status === 'started') {
                this.isRunning = true;
                this.updateUI(true);
                this.showNotification('✅ ' + data.message, 'success');
                this.updateCameraStatus('Active', '#4CAF50');
                
                // Start video feed
                this.videoFeed.src = '/video_feed?' + new Date().getTime();
                this.videoFeed.style.display = 'block';
                this.videoOverlay.style.display = 'none';
                
                console.log('Video feed started');
            } else if (data.status === 'error') {
                this.showNotification('❌ ' + data.message, 'error');
                this.updateCameraStatus('Camera Error', '#f44336');
            } else {
                this.showNotification('ℹ️ ' + data.message, 'info');
            }
        } catch (error) {
            console.error('Error starting recognition:', error);
            this.showNotification('❌ Failed to start recognition!', 'error');
            this.updateCameraStatus('Connection Error', '#f44336');
        }
    }

    async stopRecognition() {
        this.showNotification('Stopping face recognition...', 'info');
        
        try {
            const response = await fetch('/stop_recognition');
            const data = await response.json();
            
            if (data.status === 'stopped') {
                this.isRunning = false;
                this.updateUI(false);
                this.showNotification('🛑 ' + data.message, 'info');
                this.updateCameraStatus('Ready', '#2196F3');
                
                // Stop video feed
                this.videoFeed.style.display = 'none';
                this.videoOverlay.style.display = 'flex';
                this.videoFeed.src = '';
                this.clearDetections();
                
                console.log('Video feed stopped');
            }
        } catch (error) {
            console.error('Error stopping recognition:', error);
            this.showNotification('❌ Failed to stop recognition!', 'error');
        }
    }

    updateUI(isRunning) {
        const startBtn = document.getElementById('startBtn');
        const stopBtn = document.getElementById('stopBtn');
        
        startBtn.disabled = isRunning;
        stopBtn.disabled = !isRunning;
    }

    updateCameraStatus(status, color = '#2196F3') {
        const statusElement = document.getElementById('cameraStatus');
        if (statusElement) {
            statusElement.textContent = status;
            statusElement.style.color = color;
        }
    }

    async fetchFaceData() {
        if (!this.isRunning) return;

        try {
            const response = await fetch('/get_face_data');
            const data = await response.json();
            this.updateDetections(data.faces);
        } catch (error) {
            console.error('Error fetching face data:', error);
        }
    }

    updateDetections(faces) {
        const detectionsList = document.getElementById('detectionsList');
        const totalFaces = document.getElementById('totalFaces');
        const knownFaces = document.getElementById('knownFaces');
        const criminalFaces = document.getElementById('criminalFaces');

        // Update counters
        if (totalFaces) totalFaces.textContent = faces.length;
        if (knownFaces) knownFaces.textContent = faces.filter(face => face.type === 'known').length;
        if (criminalFaces) criminalFaces.textContent = faces.filter(face => face.type === 'criminal').length;

        // Update detections list
        if (faces.length === 0) {
            detectionsList.innerHTML = `
                <div class="no-detections">
                    <i class="fas fa-user-slash"></i>
                    <p>No faces detected</p>
                </div>
            `;
        } else {
            detectionsList.innerHTML = faces.map(face => `
                <div class="detection-item ${face.type}">
                    <div class="detection-icon ${face.type}">
                        <i class="fas ${face.type === 'criminal' ? 'fa-exclamation-triangle' : 'fa-user-check'}"></i>
                    </div>
                    <div class="detection-info">
                        <div class="detection-name">${face.name}</div>
                        <div class="detection-type">${face.type === 'criminal' ? 'Criminal Alert' : 'Known Person'}</div>
                    </div>
                </div>
            `).join('');
        }
    }

    clearDetections() {
        const totalFaces = document.getElementById('totalFaces');
        const knownFaces = document.getElementById('knownFaces');
        const criminalFaces = document.getElementById('criminalFaces');
        const detectionsList = document.getElementById('detectionsList');
        
        if (totalFaces) totalFaces.textContent = '0';
        if (knownFaces) knownFaces.textContent = '0';
        if (criminalFaces) criminalFaces.textContent = '0';
        if (detectionsList) detectionsList.innerHTML = `
            <div class="no-detections">
                <i class="fas fa-user-slash"></i>
                <p>No faces detected</p>
            </div>
        `;
    }

    setupPerformanceMonitoring() {
        let frameCount = 0;
        let lastTime = performance.now();
        
        const updatePerformance = () => {
            frameCount++;
            const currentTime = performance.now();
            
            if (currentTime - lastTime >= 1000) {
                const fps = Math.round((frameCount * 1000) / (currentTime - lastTime));
                frameCount = 0;
                lastTime = currentTime;
                
                const performanceElement = document.getElementById('performanceStatus');
                if (performanceElement) {
                    performanceElement.textContent = `${fps} FPS`;
                    
                    if (fps >= 25) {
                        performanceElement.style.color = '#4CAF50';
                    } else if (fps >= 15) {
                        performanceElement.style.color = '#FF9800';
                    } else {
                        performanceElement.style.color = '#f44336';
                    }
                }
            }
            requestAnimationFrame(updatePerformance);
        };
        
        updatePerformance();
    }

    startFaceDataPolling() {
        setInterval(() => this.fetchFaceData(), 1000);
    }

    showNotification(message, type) {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.innerHTML = `
            <i class="fas ${this.getNotificationIcon(type)}"></i>
            <span>${message}</span>
        `;

        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: ${this.getNotificationColor(type)};
            color: white;
            padding: 15px 20px;
            border-radius: 10px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
            display: flex;
            align-items: center;
            gap: 10px;
            z-index: 1000;
            animation: slideInRight 0.3s ease;
        `;

        document.body.appendChild(notification);

        setTimeout(() => {
            notification.style.animation = 'slideOutRight 0.3s ease';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }, 3000);
    }

    getNotificationIcon(type) {
        const icons = {
            success: 'fa-check-circle',
            error: 'fa-exclamation-circle',
            info: 'fa-info-circle'
        };
        return icons[type] || 'fa-info-circle';
    }

    getNotificationColor(type) {
        const colors = {
            success: '#4CAF50',
            error: '#f44336',
            info: '#2196F3'
        };
        return colors[type] || '#2196F3';
    }
}

// Add CSS animations for notifications
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInRight {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOutRight {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

// Initialize the app when DOM is loaded
let app;
document.addEventListener('DOMContentLoaded', () => {
    app = new FaceRecognitionApp();
    console.log('✅ Face Recognition App Initialized!');
});