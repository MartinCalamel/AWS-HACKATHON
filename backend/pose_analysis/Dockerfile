FROM public.ecr.aws/lambda/python:3.12

# Install system dependencies for MediaPipe/OpenCV
RUN dnf install -y mesa-libGL mesa-libGLU libXext libSM libXrender && dnf clean all

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy handler
COPY handler.py .

CMD ["handler.handler"]
