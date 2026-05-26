from flask import Flask, Response

from .stream import generate_frames


def create_app(*, engine, hw, input_width: int, input_height: int) -> Flask:
    app = Flask(__name__)

    @app.route("/")
    def index():
        return """
        <html>
          <head>
            <title>Live Arm Detection</title>
          </head>
          <body style="background:#111;color:white;font-family:sans-serif;text-align:center;">
            <h1>3-DOF Robot Arm Control</h1>
            <p>Right arm controls: Shoulder (bottom servo), Elbow (middle), Wrist (top)</p>
            <img src="/video_feed" style="max-width:95%;height:auto;border:2px solid #444;">
          </body>
        </html>
        """

    @app.route("/video_feed")
    def video_feed():
        return Response(
            generate_frames(engine=engine, hw=hw, input_width=input_width, input_height=input_height),
            mimetype="multipart/x-mixed-replace; boundary=frame",
        )

    return app

