#-----------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for license information.
#-----------------------------------------------------------------------------------------

FROM continuumio/miniconda3

# Configure apt
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update \
    && apt-get -y install --no-install-recommends apt-utils 2>&1

# Install git, process tools, lsb-release (common in install instructions for CLIs)
RUN apt-get -y install git procps lsb-release ffmpeg vim

# Install any missing dependencies for enhanced language service
RUN apt-get install -y libicu[0-9][0-9]

# Clean up
RUN apt-get autoremove -y \
    && apt-get clean -y \
    && rm -rf /var/lib/apt/lists/*
ENV DEBIAN_FRONTEND=dialog

RUN addgroup --gid 1000 docker && \
    adduser --uid 1000 --ingroup docker --home /home/docker --shell /bin/sh --disabled-password --gecos "" docker
RUN chown -R docker:docker /opt/conda/


# install fixuid
RUN USER=docker && \
    GROUP=docker && \
    curl -SsL https://github.com/boxboat/fixuid/releases/download/v0.1/fixuid-0.1-linux-amd64.tar.gz | tar -C /usr/local/bin -xzf - && \
    chown root:root /usr/local/bin/fixuid && \
    chmod 4755 /usr/local/bin/fixuid && \
    mkdir -p /etc/fixuid && \
    printf "user: $USER\ngroup: $GROUP\n" > /etc/fixuid/config.yml


USER docker:docker
ENV HOME /home/docker
# Set the default shell to bash rather than sh
ENV SHELL /bin/bash

RUN mkdir -p /home/docker/.ssh \
    && mkdir -p /home/docker/.vscode-server \
    && mkdir -p /home/docker/workspace

WORKDIR /home/docker/workspace

# Install Python dependencies from requirements.txt if it exists
RUN conda create -n env python=3.6
RUN echo "source activate env" > ~/.bashrc
ENV PATH /opt/conda/envs/env/bin:$PATH
RUN conda install virtualenv
RUN pip install tox-conda
COPY requirements.txt requirements-dev.txt /home/docker/workspace/
RUN pip install -r requirements-dev.txt

ENTRYPOINT ["fixuid"]


