FROM python:3-onbuild
COPY . /usr/src/app

EXPOSE 8081
EXPOSE 80
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "ls", "-a" ]
CMD [ "python", "run.py" ]
