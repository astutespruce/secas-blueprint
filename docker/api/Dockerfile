FROM osgeo/gdal:ubuntu-small-3.1.3

RUN apt-get update && apt-get install -y \
    git \
    python3-pip \
    libgeos-3.8.0 \
    libgeos-dev \
    libcairo2 \
    libcairo-gobject2 \
    libpango1.0 \
    fonts-lato


RUN useradd --create-home app
WORKDIR /home/app

COPY ./requirements.txt /tmp/requirements.txt
COPY ./setup.py /home/app

RUN pip3 install -r /tmp/requirements.txt

# Build & install pyogrio (note: update commit SHA1 as required)
RUN pip3 install -e git+https://github.com/brendan-ward/pyogrio.git@0a78012764c4a4688a72da51c52d90107cf6234c#egg=pyogrio && \
    cd /home/app/src/pyogrio && \
    python setup.py build_ext && \
    python setup.py install && \
    cd /home/app


# have to do this last as it doesn't have sufficient privileges for running pip install
# USER app
