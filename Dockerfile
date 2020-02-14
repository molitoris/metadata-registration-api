FROM python:3.7

LABEL MAINTAINER rafael.mueller1@gmail.com

# Copy SSH key for git private repos
ADD id_rsa_docker /root/.ssh/id_rsa
RUN chmod 600 /root/.ssh/id_rsa

# Skip Host verification for git
RUN echo "StrictHostKeyChecking no " > /root/.ssh/config

ADD ./requirements.txt .
RUN pip install -r requirements.txt

# Copy credentials into container
ADD .credentials.yaml .

# Copy source code into container
ADD ./metadata_registration_api /metadata_registration_api
WORKDIR /

EXPOSE 8000

CMD ["gunicorn", "--workers", "4", "--bind", "0.0.0.0", "metadata_registration_api.app:create_app (config='PRODUCTION')"]

