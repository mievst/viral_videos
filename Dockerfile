FROM pytorch/pytorch:2.1.0-cuda12.1-cudnn8-devel
ENV TZ="Europe/Moscow"
ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /opt/app
RUN conda remove --force ffmpeg -y
RUN apt update -y
RUN apt install -y curl unzip nano wget git zlib1g-dev nasm cmake gcc g++
RUN apt install -y ffmpeg libsm6 libxext6 build-essential software-properties-common ca-certificates
RUN apt-get install -qq -y build-essential xvfb xdg-utils wget unzip ffmpeg libpq-dev vim libmagick++-dev fonts-liberation sox bc gsfonts --no-install-recommends\
    && apt-get clean
RUN apt-get install -y portaudio19-dev libasound2-dev libopencv-dev libprotobuf-dev libopus-dev

## ImageMagicK Installation
RUN mkdir -p /tmp/distr && \
    cd /tmp/distr && \
    wget https://download.imagemagick.org/ImageMagick/download/releases/ImageMagick-7.0.11-2.tar.xz && \
    tar xvf ImageMagick-7.0.11-2.tar.xz && \
    cd ImageMagick-7.0.11-2 && \
    ./configure --enable-shared=yes --disable-static --without-perl && \
    make && \
    make install && \
    ldconfig /usr/local/lib && \
    cd /tmp && \
    rm -rf distr


COPY . .
COPY requirements.txt /opt/app
RUN pip install -r requirements.txt
COPY src /opt/app/src
WORKDIR /opt/app
CMD ["python", "-u", "src/run.py"]