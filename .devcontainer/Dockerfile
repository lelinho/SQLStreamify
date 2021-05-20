ARG base=ubuntu:hirsute
FROM "${base}"
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update
RUN apt-get install --yes \
    curl \
    wget \
    git \
    zsh
RUN apt-get install --yes \   
    vim \
    unzip \
    locales-all \
    build-essential \
    ca-certificates \
    apt-transport-https
RUN apt-get install --yes \
    docker \
    docker.io \
    docker-compose \
    python \
    python3-pip \
    sudo
    
RUN chsh -s $(which zsh) \
    && useradd -s $(which zsh) \
    -d /home/devcontainer/ \
    -m -G sudo devcontainer \
    && echo "devcontainer ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers \
    && chown -R devcontainer:devcontainer /home/devcontainer 
    # LOCALES
    #&& localedef -i pt_BR -c -f UTF-8 -A /usr/share/locale/locale.alias pt_BR.UTF-8 \
    # Oh-my-zsh \
RUN /bin/su -s /bin/zsh -c "$(cd /home/devcontainer/ && curl -fsSL https://raw.github.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" devcontainer \
    && /bin/su -s /bin/zsh -c "$(mv /home/devcontainer/.zshrc.pre-oh-my-zsh /home/devcontainer/.zshrc)" devcontainer \
    && /bin/su -s /bin/zsh -c "git clone https://github.com/zsh-users/zsh-autosuggestions.git /home/devcontainer/.oh-my-zsh/custom/plugins/zsh-autosuggestions" devcontainer \
    && /bin/su -s /bin/zsh -c "git clone https://github.com/zsh-users/zsh-syntax-highlighting.git /home/devcontainer/.oh-my-zsh/custom/plugins/zsh-syntax-highlighting" devcontainer \
    && /bin/su -s /bin/zsh -c "git clone https://github.com/zsh-users/zsh-completions.git /home/devcontainer/.oh-my-zsh/custom/plugins/zsh-completions" devcontainer


    # cleaning
RUN chown -R devcontainer:devcontainer /home/devcontainer \
    && apt-get clean autoclean \
    && apt-get autoremove --yes \
    && rm -rf /var/lib/{apt,dpkg,cache,log}/

RUN pip3 install configparser jinja2

RUN usermod -aG docker devcontainer

RUN newgrp docker

USER devcontainer
    
ENV LANG pt_BR.utf8
