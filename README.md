# 🔄 Automated Recycling Plant Sorter

An intelligent recycling sorting system that uses computer vision and Arduino-controlled actuators to automatically classify and sort materials on a conveyor belt. Developed as part of an Engineering course project at Earlham College.

## 🎯 Overview

This system combines Python-based computer vision with Arduino hardware control to create an automated sorting mechanism for recycling materials. The system detects objects moving on a conveyor belt, classifies them by color and material properties using HSV color space analysis, and triggers pneumatic actuators to sort items into appropriate bins.

## ✨ Features

- **Real-time Object Detection**: Uses OpenCV to detect and track objects on a conveyor belt
- **Color-based Classification**: Identifies materials using HSV color space analysis
- **Multi-material Sorting**: Classifies red, yellow, sand-colored, and steel-like objects
- **Intelligent Aluminum Detection**: Uses a heuristic method to distinguish aluminum from steel
- **Hardware Integration**: Serial communication between Python and Arduino for actuator control
- **Visual Feedback**: Live camera feed with object tracking and classification masks
- **Adjustable ROI**: Parallelogram region of interest to focus on belt area

## 🛠️ Hardware Requirements

- Webcam/USB camera
- Arduino board (Uno/Mega recommended)
- 2x Linear actuators or pneumatic pushers
- 2x H-bridge motor drivers (L298N or similar)
- Conveyor belt system
- USB cable for Arduino-PC communication

### Wiring Configuration

**First Actuator:**
- IN1 (extend) → Pin 8
- IN2 (retract) → Pin 9

**Second Actuator:**
- IN1 (extend) → Pin 10
- IN2 (retract) → Pin 11

## 💻 Software Requirements

### Python Dependencies
```bash
pip install opencv-python numpy pyserial
```

### Arduino IDE
- Version 1.8.x or higher
- Standard Arduino libraries (included by default)

## 📋 Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/recycling-sorter.git
   cd recycling-sorter
   ```

2. **Upload Arduino sketch**
   - Open `Actuators-Plant.ino` in Arduino IDE
   - Select your board type and COM port
   - Upload the sketch to your Arduino

3. **Configure Python script**
   - Update the COM port in `sorter.py` (line 8):
     ```python
     ser = serial.Serial("COM11", 9600)  # Change to your port
     ```
   - Adjust ROI coordinates if needed (lines 11-14)

4. **Run the system**
   ```bash
   python sorter.py
   ```

## 🎨 Material Classification

The system classifies objects into the following categories:

| Material | Code | HSV Range | Action |
|----------|------|-----------|--------|
| Red | R | 0-10, 170-180 (H) | First actuator push |
| Yellow | Y | 20-35 (H) | Second actuator push |
| Sand | S | 10-25 (H) | First actuator push |
| Steel | T | 90-130 (H) | Second actuator push (first occurrence) |
| Aluminum/Unknown | U | - | No push (default bin) |
| None | N | - | No object detected |

## 🔧 Customization

### Adjusting HSV Color Ranges

Modify the threshold values in `sorter.py` (lines 15-24) based on your lighting conditions and material colors:

```python
RED1_LOW = np.array([0, 120, 80])
RED1_HIGH = np.array([10, 255, 255])
# ... adjust other ranges similarly
```

### Timing Configuration

Adjust actuator push duration in `Actuators-Plant.ino`:
```cpp
const int PUSH_TIME_MS = 350;  // Milliseconds
```

### Detection Parameters

Fine-tune detection sensitivity in `sorter.py`:
- `area > 2000`: Minimum object area (line 110)
- `radius > 20`: Minimum circle radius (line 112)
- `best_score < 800`: Minimum confidence threshold (line 59)

## 🚀 Usage

1. Position the camera to view the conveyor belt
2. Ensure the parallelogram ROI covers the belt area
3. Run the Python script
4. Place objects on the belt
5. Monitor classification in real-time through the GUI
6. Press 'q' to quit the application

## 📊 How It Works

### Vision System (Python)
1. Captures video frames from webcam
2. Applies parallelogram ROI mask to focus on belt
3. Detects objects using contour analysis
4. Extracts circular regions around detected objects
5. Analyzes HSV color distribution
6. Classifies material based on dominant color
7. Sends classification code via serial to Arduino

### Control System (Arduino)
1. Listens for serial commands from Python
2. Receives single-character classification codes
3. Triggers appropriate actuator based on code
4. Extends actuator for 350ms
5. Retracts actuator for 350ms
6. Returns to idle state

### Aluminum Detection Logic
The system uses a simple heuristic to distinguish aluminum from steel:
- First steel-like object (T code) → sorted as steel
- Subsequent steel-like objects → treated as aluminum/unknown (U code)
- This approach assumes limited steel presence in the waste stream

## 🐛 Troubleshooting

**Camera not detected:**
- Check camera connection and permissions
- Try different camera index in `cv2.VideoCapture(0)`

**Serial connection fails:**
- Verify correct COM port
- Ensure Arduino is connected and drivers installed
- Check that no other program is using the serial port

**Poor classification accuracy:**
- Adjust HSV color ranges for your lighting
- Calibrate ROI coordinates
- Ensure consistent belt speed
- Improve lighting conditions

**Actuators not responding:**
- Verify wiring connections
- Check H-bridge power supply
- Test actuators independently
- Confirm serial baud rate matches (9600)

## 🔮 Future Improvements

- Machine learning-based classification
- Multi-sensor integration (metal detector, weight sensor)
- Web-based monitoring dashboard
- Statistical logging and reporting
- Adaptive HSV calibration
- Support for more material types

## 👨‍💻 Author

**Bruno**  
Earlham College - Introduction to Engineering (ENGR-111)

## 📝 License

This project is open source and available for educational purposes.

## 🙏 Acknowledgments

- Earlham College Engineering Department
- OpenCV community for excellent documentation
- Arduino community for hardware support

---

*Built with ❤️ for a sustainable future*
