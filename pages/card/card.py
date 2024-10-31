import streamlit as st
import cv2
import os
from datetime import datetime
from PIL import Image
import subprocess

# Create photos directory if it doesn't exist
if not os.path.exists("photos"):
    os.makedirs("photos")

# Page config and title
st.set_page_config(page_title="Host Camera App", page_icon="📸")
st.title("📸 Host Machine Camera")


# Function to find available cameras on Linux
def get_available_cameras():
    available_devices = []
    try:
        cmd = subprocess.run(
            ["v4l2-ctl", "--list-devices"], capture_output=True, text=True
        )
        for line in cmd.stdout.split("\n"):
            if "/dev/video" in line:
                device_num = line.strip().replace("/dev/video", "")
                if device_num.isdigit():
                    available_devices.append(int(device_num))
    except:
        # Fallback to testing first 2 indices if v4l2-ctl is not available
        for i in range(2):
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                available_devices.append(i)
                cap.release()
    return available_devices


# Initialize camera in session state
def init_camera():
    available_cameras = get_available_cameras()

    if not available_cameras:
        st.error("No cameras detected!")
        return None

    # Try cameras in order of availability
    for camera_index in available_cameras:
        camera = cv2.VideoCapture(camera_index)
        if camera.isOpened():
            # Set resolution
            camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
            camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
            st.success(f"Successfully connected to camera {camera_index}")
            return camera
    return None


# Initialize or check camera
if "camera" not in st.session_state:
    st.session_state.camera = init_camera()

# Check if camera is working
if st.session_state.camera is None:
    st.error(
        "Failed to initialize camera. Please check if your camera is connected and not being used by another application."
    )
    if st.button("Try Again"):
        st.session_state.camera = init_camera()
        st.rerun()
    st.stop()

# Sidebar settings
st.sidebar.title("Settings")
image_quality = st.sidebar.slider("Image Quality", 0, 100, 85)


# Function to capture and display frame
def get_frame():
    if st.session_state.camera is not None and st.session_state.camera.isOpened():
        ret, frame = st.session_state.camera.read()
        if ret:
            return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    return None


# Function to capture photo
def capture_photo():
    frame = get_frame()
    if frame is not None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"photos/photo_{timestamp}.jpg"

        try:
            image = Image.fromarray(frame)
            image.save(filename, quality=image_quality)
            return filename
        except Exception as e:
            st.error(f"Error saving photo: {str(e)}")
    return None


# Create two columns
col1, col2 = st.columns(2)

with col1:
    st.header("Camera Feed")
    frame_placeholder = st.empty()

    # Capture button
    if st.button("📸 Take Photo"):
        filename = capture_photo()
        if filename:
            st.success(f"Photo saved as {filename}")
        else:
            st.error("Failed to capture photo")

    # Reinitialize camera button
    if st.button("🔄 Reinitialize Camera"):
        if st.session_state.camera is not None:
            st.session_state.camera.release()
        st.session_state.camera = init_camera()
        st.rerun()

with col2:
    st.header("Saved Photos")
    try:
        saved_photos = sorted(os.listdir("photos"), reverse=True)
        for photo in saved_photos[:5]:  # Show last 5 photos
            if photo.endswith((".jpg", ".jpeg", ".png")):
                photo_path = os.path.join("photos", photo)
                try:
                    st.image(photo_path, caption=photo, use_column_width=True)
                except Exception as e:
                    st.error(f"Error loading {photo}: {str(e)}")
    except Exception as e:
        st.error(f"Error accessing photos directory: {str(e)}")

# Display camera feed
frame = get_frame()
if frame is not None:
    frame_placeholder.image(frame, channels="RGB", use_column_width=True)
else:
    st.error("Failed to get camera frame. Try reinitializing the camera.")

# Add a stop button to properly close the camera
if st.button("Stop Camera"):
    if st.session_state.camera is not None:
        st.session_state.camera.release()
        st.session_state.camera = None
    st.rerun()


# Cleanup on session end
def cleanup():
    if "camera" in st.session_state and st.session_state.camera is not None:
        st.session_state.camera.release()


# Register cleanup
import atexit

atexit.register(cleanup)
