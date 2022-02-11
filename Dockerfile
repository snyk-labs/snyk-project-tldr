# now we create our final container, runtime
FROM python:3.9-slim AS runtime

WORKDIR /app

# copy stuff from this repo into the /app directory of the container
COPY *.py .

# now we use multistage containers to then copy the requirements from the other container
COPY requirements.txt .

# now we're *just* deploying the needed packages for whatever was in the poetry setup
RUN python -m pip install --quiet -U pip
RUN pip install --quiet -r requirements.txt
RUN mkdir /app/output

ENTRYPOINT ["/usr/local/bin/python","/app/project_tldr.py"]