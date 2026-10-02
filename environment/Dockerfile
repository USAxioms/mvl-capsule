# Reference environment for local reproduction.
# The capsule uses only the Python 3 standard library: no packages to install.
# On Code Ocean, select any starter environment that provides Python 3.10 or later.
FROM python:3.12-slim
WORKDIR /capsule
COPY code /capsule/code
COPY data /data
RUN mkdir -p /results
CMD ["bash", "/capsule/code/run"]
