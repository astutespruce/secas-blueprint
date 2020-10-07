# TODO: pin to 3.1.4 once available
FROM osgeo/gdal:ubuntu-small-latest

RUN apt-get update && apt-get install -y \
    git \
    python3-pip \
    libgeos-3.8.0 \
    libgeos-dev \
    libcairo2 \
    libcairo-gobject2 \
    libpango1.0

# Install fonts
RUN mkdir /usr/share/fonts/google && \
    curl https://fonts.google.com/download?family=Raleway --output /tmp/Raleway.zip && \
    unzip /tmp/Raleway.zip -d /usr/share/fonts/google && \
    mv /usr/share/fonts/google/static/* /usr/share/fonts/google/ && \
    curl https://fonts.google.com/download?family=Source+Sans+Pro --output /tmp/SourceSansPro.zip && \
    unzip -o /tmp/SourceSansPro.zip -d /usr/share/fonts/google && \
    fc-cache -fv


RUN useradd --create-home app
WORKDIR /home/app

COPY ./requirements.txt /tmp/requirements.txt

RUN pip3 install -r /tmp/requirements.txt

# Build & install pyogrio (note: update commit SHA1 as required)
RUN pip3 install -e git+https://github.com/brendan-ward/pyogrio.git@0a78012764c4a4688a72da51c52d90107cf6234c#egg=pyogrio && \
    cd /home/app/src/pyogrio && \
    python setup.py build_ext && \
    python setup.py install && \
    cd /home/app


ENV PYTHONPATH="${PYTHONPATH}:/home/app"
ENV PYTHONUNBUFFERED 1