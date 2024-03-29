FROM python:3.9.6

# Copy local code to the container image.
ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . ./

RUN pip3 install --require-hashes --no-deps -r requirements.txt

EXPOSE 8080

ENTRYPOINT ["streamlit", "run", "frontend.py", "--server.port=8080", "--server.address=0.0.0.0"]