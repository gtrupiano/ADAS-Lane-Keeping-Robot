from flask import Flask, Response
from picamera2 import Picamera2
import cv2
import time


def main():
    # Create Flask app
    app = Flask(__name__)

    # Setup camera
    picam2 = setup_camera()

    # Register routes (connect URLs → functions)
    register_routes(app, picam2)

    # Start server
    app.run(host="0.0.0.0", port=5000, threaded=True)


def setup_camera():
    """
    Create and start the camera.
    Returns the camera object so other functions can use it.
    """
    picam2 = Picamera2()
    picam2.configure(
        picam2.create_preview_configuration(
            main={"size": (640, 480)}
        )
    )
    picam2.start()
    return picam2


def generate_frames(picam2):
    """
    This function continuously captures frames and yields them.

    IMPORTANT:
    - Flask will call this (you don't call it directly)
    - Each 'yield' sends one frame to the browser
    """
    while True:
        frame = picam2.capture_array()

        # Convert frame → JPEG
        ret, buffer = cv2.imencode('.jpg', frame)
        if not ret:
            continue

        frame_bytes = buffer.tobytes()

        # Send frame in MJPEG format
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

        time.sleep(0.03)


def register_routes(app, picam2):
    """
    This function defines all routes.

    KEY IDEA:
    We define routes INSIDE this function so they can access picam2.
    """

    @app.route("/")
    def video_feed():
        """
        Called when browser goes to "/" (default if nothing else is typed)
        """
        return Response(
            generate_frames(picam2),
            mimetype='multipart/x-mixed-replace; boundary=frame'
        )


if __name__ == "__main__":
    main()