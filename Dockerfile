FROM selenium/standalone-chrome:latest
USER root

RUN apt-get update && apt-get install -y \
    python3.10 \
    python3-pip \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && python3.10 -m pip install --upgrade pip

COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir --user -r /requirements.txt

WORKDIR /scripts
CMD ["python3", "-m", "uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
