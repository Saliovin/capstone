FROM python:3.7
ADD . /app
WORKDIR /app
RUN pip install pipenv gunicorn
COPY Pipfile* /tmp/
RUN cd /tmp && pipenv lock --requirements > requirements.txt
RUN pip install -r /tmp/requirements.txt
EXPOSE 8000
ENV DATABASE_URL=postgres://postgres:docker@pg-docker:5432/harvester_api
RUN chmod u+x ./db-script.sh
CMD ["./db-script.sh"]