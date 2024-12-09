# Step 1: Use a base image with Python
FROM python:3.9.20

# Install dependencies for Chrome, ChromeDriver, and X11
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    unzip \
    ca-certificates \
    libx11-dev \
    libxkbfile-dev \
    libgdk-pixbuf2.0-0 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libxss1 \
    libasound2 \
    fonts-liberation \
    libappindicator3-1 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libgdk-pixbuf2.0-0 \
    libdbus-1-3 \
    libxtst6 \
    lsb-release \
    x11-apps \
    && rm -rf /var/lib/apt/lists/*

# Install Chrome browser
# Remove DISPLAY reference here
RUN curl -sSL https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb -o google-chrome-stable_current_amd64.deb \
    && dpkg -i google-chrome-stable_current_amd64.deb \
    && apt-get -y --fix-broken install \
    && rm google-chrome-stable_current_amd64.deb

# Install ChromeDriver
RUN LATEST=$(curl -sSL https://chromedriver.storage.googleapis.com/LATEST_RELEASE) \
    && curl -sSL https://chromedriver.storage.googleapis.com/$LATEST/chromedriver_linux64.zip -o chromedriver.zip \
    && unzip chromedriver.zip -d /usr/local/bin/ \
    && rm chromedriver.zip \
    && chmod +x /usr/local/bin/chromedriver

# Step 2: Set the working directory to /app (inside the container)
WORKDIR /app

# Step 3: Copy the requirements file into the container
COPY requirements.txt .

# Step 4: Install the required Python packages
RUN pip install --no-cache-dir  -r requirements.txt

# Step 5: Copy the entire app directory into the container
COPY app /app

# Step 6: Expose the port that Flask is running on
EXPOSE 8000

# Set the DISPLAY environment variable to use X11
ENV DISPLAY=${DISPLAY:-host.docker.internal:0}

# Step 7: Set the command to run the Flask app
CMD ["python", "main.py"]
