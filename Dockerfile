FROM python:3.7

LABEL MAINTAINER=rafa.molitoris@gmail.com

ADD ./requirements.txt .
RUN pip install -r requirements.txt

# Change to non-root user (for CaaS)
RUN  adduser -u 1000 --system worker
USER 1000

ADD --chown=1000 ./logging.conf .

# Copy source code into container
ADD --chown=1000 ./metadata_registration_api /metadata_registration_api
WORKDIR /

EXPOSE 8000

CMD ["gunicorn", \
        "--workers", "4", \
        "--bind", "0.0.0.0", \
        "--log-config", "/logging.conf", \
        "metadata_registration_api.app:create_app()"]

