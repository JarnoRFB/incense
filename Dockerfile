FROM continuumio/miniconda3

ARG USERNAME=vscode
# Adapt to your output of id -u
ARG USER_UID=1000
ARG USER_GID=$USER_UID

# Configure apt
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update \
    && apt-get -y install --no-install-recommends apt-utils 2>&1

# Create the user
RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME \
    #
    # [Optional] Add sudo support. Omit if you don't need to install software after connecting.
    && apt-get update \
    && apt-get install -y sudo \
    && echo $USERNAME ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$USERNAME \
    && chmod 0440 /etc/sudoers.d/$USERNAME

# Install git, process tools, lsb-release (common in install instructions for CLIs)
RUN apt -y install git procps lsb-release ffmpeg vim exuberant-ctags zsh wget

# # Install any missing dependencies for enhanced language service
# RUN apt install -y libicu[0-9][0-9]

# Clean up
RUN apt-get autoremove -y \
    && apt-get clean -y \
    && rm -rf /var/lib/apt/lists/*
ENV DEBIAN_FRONTEND=dialog

RUN chown -R ${USER_UID}:${USER_GID} /opt/conda/

USER $USERNAME

ENV HOME /home/${USERNAME}


RUN mkdir -p ${HOME}/.ssh \
    && mkdir -p ${HOME}/.vscode-server \
    && mkdir -p ${HOME}/workspace

WORKDIR ${HOME}/workspace

# Install Python dependencies from requirements.txt if it exists
RUN conda create -n env python=3.7
RUN echo "source activate env" > ~/.bashrc
ENV PATH /opt/conda/envs/env/bin:$PATH
RUN conda install virtualenv
RUN pip install tox-conda
COPY requirements.txt requirements-dev.txt ${HOME}/workspace/
RUN pip install -r requirements-dev.txt


ENV TERM=xterm \
    ZSH_THEME=agnoster \
    EDITOR=vi
RUN wget https://github.com/robbyrussell/oh-my-zsh/raw/master/tools/install.sh -O - | zsh
ENV SHELL /usr/bin/zsh
