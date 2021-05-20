FROM python:3.6-slim

LABEL description="Demo container with ephemeral database for Lagerregal"
EXPOSE 8000/tcp

ADD . code
WORKDIR code

ENV BUILDPKGS gcc python3-dev libldap2-dev libsasl2-dev libssl-dev
ENV DJANGO_SETTINGS_MODULE Lagerregal.settings.demo


RUN apt-get update && apt-get install -y --no-install-recommends $BUILDPKGS
RUN pip install -r dependencies.txt
RUN python manage.py migrate
RUN python manage.py populate
RUN apt-get purge -y $BUILDPKGS

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
