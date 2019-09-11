FROM python:3.6-slim

LABEL description="Development container for Lagerregal"
EXPOSE 8000/tcp

ADD . code
WORKDIR code
ENV BUILDPKGS gcc python3-dev libldap2-dev libsasl2-dev libssl-dev gettext


RUN apt-get update && apt-get install -y --no-install-recommends $BUILDPKGS
RUN pip install -r requirements.txt
RUN pip install flake8
RUN cp Lagerregal/template_development.py Lagerregal/settings.py
RUN python manage.py compilemessages -l de
RUN python manage.py migrate
RUN apt-get purge -y $BUILDPKGS

#VOLUME /code/database.db
#VOLUME /code/settings.py

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
