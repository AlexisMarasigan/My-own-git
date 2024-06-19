FROM python:3.9-slim

WORKDIR /usr/src/app

COPY . .

RUN chmod +x wyag

CMD ["./wyag"]