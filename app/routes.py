import os
from datetime import datetime

from flask import (
    render_template,
    request,
    jsonify,
    send_from_directory,
    url_for,
    current_app as app,
    Response,
)
from celery.result import AsyncResult
import cv2

from app import db
from app.models import Video
from app.tasks import process_video_landmarks, celery
from app.config import VIDEO_DIR
from app.utils.real_time_recognition import get_recognizer


@app.route("/")
def index():
    return render_template("index.html")


def generate_frames():
    recognizer = get_recognizer()

    while True:
        frame = recognizer.get_frame()
        if frame is None:
            continue

        ret, buffer = cv2.imencode(".jpg", frame)
        if not ret:
            continue

        frame_bytes = buffer.tobytes()
        yield b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n"


@app.route("/video_feed")
def video_feed():
    return Response(generate_frames(), mimetype="multipart/x-mixed-replace; boundary=frame")


@app.route("/current_predictions")
def current_predictions():
    recognizer = get_recognizer()
    current, top3 = recognizer.get_current_predictions()

    if current is None:
        return jsonify({"status": "waiting", "message": "Collecting frames..."})

    return jsonify(
        {
            "status": "success",
            "current_prediction": current,
            "top3": [{"label": label, "confidence": float(conf)} for label, conf in top3],
        }
    )


@app.route("/toggle_recognition", methods=["POST"])
def toggle_recognition():
    action = request.json.get("action", "start")
    recognizer = get_recognizer()

    if action == "start":
        success = recognizer.start_capture()
        if success:
            return jsonify({"status": "started", "success": True})
        return jsonify({"status": "error", "success": False, "message": "Failed to start camera"})

    recognizer.stop_capture()
    return jsonify({"status": "stopped", "success": True})


@app.route("/recognition_status")
def recognition_status():
    return jsonify({"is_running": get_recognizer().is_running})


def _save_video_file(label, video_file):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    save_dir = os.path.join(VIDEO_DIR, label)
    os.makedirs(save_dir, exist_ok=True)
    filename = f"{timestamp}.webm"
    video_path = os.path.join(save_dir, filename)
    video_file.save(video_path)

    video = Video(path=video_path, label=label)
    db.session.add(video)
    db.session.commit()
    return video


@app.route("/record", methods=["GET"])
def record_page():
    return render_template("save_video.html")


@app.route("/save_video", methods=["POST"])
def save_video():
    label = request.form.get("label", "").strip()
    if not label:
        return jsonify({"status": "error", "message": "Label can not be empty."}), 400

    video_file = request.files.get("video")
    if not video_file:
        return jsonify({"status": "error", "message": "No video uploaded."}), 400

    video = _save_video_file(label, video_file)
    rel_path = os.path.relpath(video.path, os.path.join(app.root_path, "videos"))

    return jsonify(
        {
            "status": "success",
            "message": "Video saved successfully.",
            "video_id": video.id,
            "path": url_for("serve_video", filename=rel_path),
        }
    )


@app.route("/videos/<path:filename>")
def serve_video(filename):
    return send_from_directory(os.path.join(app.root_path, "videos"), filename)


@app.route("/process_video", methods=["POST"])
def process_video():
    video_id = request.form.get("video_id", type=int)
    mirror = request.form.get("mirror", "true").lower() == "true"
    start_time = request.form.get("start_time", type=float, default=0.0)
    end_time = request.form.get("end_time", type=float, default=0.0)

    if start_time < 0 or end_time < 0:
        return jsonify({"status": "error", "message": "Start and end time must be positive."}), 400
    if start_time >= end_time:
        return jsonify({"status": "error", "message": "Start time must be less than end time."}), 400

    video = db.session.get(Video, video_id)
    if not video:
        return jsonify({"status": "error", "message": "Video not found."}), 404

    task = process_video_landmarks.apply_async(
        args=[video_id],
        kwargs={"mirror": mirror, "start_time": start_time, "end_time": end_time},
    )
    return jsonify({"status": "success", "task_id": task.id, "message": "Landmark extraction started."})


@app.route("/task_status/<task_id>", methods=["GET"])
def task_status(task_id):
    task = AsyncResult(task_id, app=celery)

    if task.state == "PENDING":
        response = {"state": task.state, "current": 0, "total": 1, "status": "Pending..."}
    elif task.state == "PROGRESS":
        response = {
            "state": task.state,
            "current": task.info.get("current", 0),
            "total": task.info.get("total", 1),
            "status": task.info.get("status", ""),
        }
    elif task.state == "SUCCESS":
        response = {"state": task.state, "current": 0, "total": 1, "status": "Completed"}
    else:
        response = {"state": task.state, "current": 0, "total": 1, "status": str(task.info)}

    return jsonify(response)
