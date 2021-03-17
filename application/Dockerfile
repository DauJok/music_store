FROM python:3
WORKDIR /usr/src/app
COPY requirements.txt ./
RUN python3 -m pip intall --user --no-cache-dir -r requirements.txt
# Copy project to workdir
COPY . .
# Run app
CMD ["python", "app.py"]