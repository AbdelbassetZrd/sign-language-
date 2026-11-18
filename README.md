# Sign to Text

A real-time sign language recognition website built with Flask, MediaPipe, TensorFlow, OpenCV, and SQLite.

## Features

- Live sign language recognition through the webcam
- Top-3 prediction display
- Camera start and stop controls
- Video recording page
- Sign to Voice placeholder page
- Dark blue and white interface

## Requirements

- Linux
- Python 3.11
- Conda
- Redis
- A webcam

## Installation

From the project directory:

```bash
conda create -n sign-language python=3.11 -y
conda activate sign-language
python -m pip install -r requirements.txt
```

## Run the Website

Open a terminal and start Redis:

```bash
redis-server --save '' --appendonly no
```

Open a second terminal, activate the environment, and start Flask:

```bash
cd /home/abdelbasset/Downloads/sign-language-recognition-main
source ~/miniconda3/etc/profile.d/conda.sh
conda activate sign-language
python run.py
```

Then open:

```text
http://127.0.0.1:5000
```

Allow camera access in your browser when prompted.

## Pages

- `/` — Live Sign to Text recognition
- `/record` — Record a sign video

## Model Files

The recognition model and preprocessing files are stored in:

```text
app/model/sign_language_recognition.keras
app/model/scaler.pkl
app/model/label_encoder.pkl
app/model/feature_order.json
```

These files contain the trained model and required preprocessing values. A separate model database is not required.

## Stop the Application

Press `Ctrl+C` in the Flask terminal. Redis can be stopped with `Ctrl+C` in its terminal.

## Troubleshooting

- If port `5000` is already in use, stop the existing Flask process or restart the terminal.
- If no camera appears, allow browser camera permissions and verify that `/dev/video0` or your webcam is available.
- Always run the application in the `sign-language` Conda environment.
