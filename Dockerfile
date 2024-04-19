# Use a base image with Python 3.12
FROM python:3.11

# Set the working directory inside the container
WORKDIR /app



# Copy the Python code, templates, session file, and other files into the container
COPY main.py /app/
COPY engine.py /app/
COPY datastorage.py /app/
COPY webdriver_setup.py /app/
COPY templates /app/templates
COPY static /app/static
COPY error_log.txt /app/error_log.txt
COPY requirements.txt /app/requirements.txt

# Set environment variable to prevent debconf from prompting for user input
ENV DEBIAN_FRONTEND=noninteractive

# Install apt-utils to avoid debconf warning
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
 && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Firefox 115 ESR
# Install apt-utils to avoid debconf warning and install Firefox
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
    apt-utils \
    wget \
    bzip2 \
    firefox-esr \
 && rm -rf /var/lib/apt/lists/*

# Download and install geckodriver
ARG GECKODRIVER_VERSION=0.34.0
RUN apt-get update && apt-get install -y wget unzip && \
    wget https://github.com/mozilla/geckodriver/releases/download/v${GECKODRIVER_VERSION}/geckodriver-v${GECKODRIVER_VERSION}-linux64.tar.gz && \
    tar -xvzf geckodriver-v${GECKODRIVER_VERSION}-linux64.tar.gz && \
    mv geckodriver /usr/local/bin/ && \
    rm geckodriver-v${GECKODRIVER_VERSION}-linux64.tar.gz && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set environment variable to enable headless mode for Firefox
#ENV MOZ_HEADLESS=1

# Expose port 8080
EXPOSE 8080

# Set the entry point for the container
CMD ["python3", "main.py"]