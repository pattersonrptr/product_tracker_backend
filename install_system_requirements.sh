#!/bin/bash

# Install python, libraries used by Chrome and others for the system
apt-get update && apt-get install -y \
  curl \
  gawk \
  wget \
  unzip \
  python3 \
  python3-pip \
  fonts-liberation \
  libatk-bridge2.0-0 \
  libatk1.0-0 \
  libatspi2.0-0 \
  libcairo2 \
  libcups2 \
  libdbus-1-3 \
  libgbm1 \
  libglib2.0-0 \
  libgtk-4-1 \
  libnspr4 \
  libnss3 \
  libpango-1.0-0 \
  libvulkan1 \
  libxcomposite1 \
  libxdamage1 \
  libxext6 \
  libxfixes3 \
  libxkbcommon0 \
  libxrandr2 \
  xdg-utils \
  libasound2-dev \
  netcat-traditional \
  && apt-get install --fix-missing \
  && rm -rf /var/lib/apt/lists/*

# Download Chrome Stable debian package
wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
  && dpkg -i google-chrome-stable_current_amd64.deb \
  && apt -f install \
  && rm google-chrome-stable_current_amd64.deb

# Download chromedriver
CHROME_VERSION=$(google-chrome-stable --version | awk '{print $3}') \
  && echo "$CHROME_VERSION" \
  && wget -q "https://storage.googleapis.com/chrome-for-testing-public/$CHROME_VERSION/linux64/chromedriver-linux64.zip" \
  && unzip chromedriver-linux64.zip \
  && mv chromedriver-linux64 /usr/local/bin \
  && chmod +x /usr/local/bin/chromedriver-linux64/chromedriver \
  && ln -s /usr/local/bin/chromedriver-linux64/chromedriver /usr/local/bin/chromedriver \
  && rm -rf chromedriver-linux64*
