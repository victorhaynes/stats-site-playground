FROM python:3.10-alpine3.14

ENV PYTHONBUFFERED 1

WORKDIR /backend

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

COPY . .

COPY entrypoint.sh /backend/entrypoint.sh

# Make entrypoint/startup commands executable
RUN chmod +x /backend/entrypoint.sh

ENTRYPOINT [ "/backend/entrypoint.sh" ]