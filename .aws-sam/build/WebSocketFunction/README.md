# Lambda Pushup Counter

Pushup counter running on AWS Lambda with a browser-based frontend. Uses MediaPipe Pose for body landmark detection and counts reps via elbow angle tracking.

## Architecture

```
Browser (webcam) → WebSocket → API Gateway → Lambda (MediaPipe) → WebSocket → Browser (count)
```

The browser captures webcam frames as JPEG, sends them as base64 over a WebSocket connection. The Lambda processes each frame with MediaPipe, calculates elbow angles, counts reps, and sends the result back.

## Prerequisites

- AWS CLI configured
- AWS SAM CLI installed (`pip install aws-sam-cli`)
- Python 3.11
- Docker (for SAM build with native dependencies)

## Deploy

```bash
cd lambda-pushup-counter

# Build (uses Docker for MediaPipe/OpenCV native libs)
sam build --use-container

# Deploy
sam deploy --guided
```

During guided deploy, accept defaults. Note the **WebSocketURL** output.

## Usage

1. Open `frontend/index.html` in a browser
2. Paste the WebSocket URL from the deploy output
3. Click **Start** — allow camera access
4. Do pushups facing the camera sideways (right side visible)
5. The counter increments when your right elbow goes below 85° then back above 165°

## Project Structure

```
├── template.yaml              # SAM/CloudFormation template
├── requirements.txt           # Python dependencies
├── process_frame/handler.py   # MediaPipe pose processing logic
├── websocket_handler/handler.py  # WebSocket route handler (Lambda entry)
└── frontend/index.html        # Browser UI
```

## Notes

- Lambda has a 6MB WebSocket frame limit — frames are sent at 320x240 JPEG quality 0.6 (~15-25KB each)
- Sends at 5fps to balance responsiveness vs Lambda invocations
- State (count, position) is maintained client-side and sent with each frame to keep Lambda stateless
- Cold starts may cause a 1-2s delay on first frame; subsequent frames process in ~200-500ms
- For production use, consider a Lambda layer for MediaPipe dependencies to reduce package size
