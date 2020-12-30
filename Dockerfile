FROM python:3.9

ARG ENV=production

RUN if [ "$ENV" = "development" ]; then \
    curl -sL https://deb.nodesource.com/setup_12.x | bash - \
    && apt-get install -y nodejs inotify-tools \
    # Install Docker CE CLI
    apt-transport-https ca-certificates curl gnupg2 lsb-release \
    && curl -fsSL https://download.docker.com/linux/$(lsb_release -is | tr '[:upper:]' '[:lower:]')/gpg | apt-key add - 2>/dev/null \
    && echo "deb [arch=amd64] https://download.docker.com/linux/$(lsb_release -is | tr '[:upper:]' '[:lower:]') $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list \
    && apt-get update \
    && apt-get install -y docker-ce-cli \
    # 
    # Install Docker Compose
    && export LATEST_COMPOSE_VERSION=$(curl -sSL "https://api.github.com/repos/docker/compose/releases/latest" | grep -o -P '(?<="tag_name": ").+(?=")') \
    && curl -sSL "https://github.com/docker/compose/releases/download/${LATEST_COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose \
    && chmod +x /usr/local/bin/docker-compose; \
    fi

WORKDIR /workspace

COPY leaderboard/requirements ./leaderboard/requirements

RUN python -m pip install --upgrade pip && pip install -r leaderboard/requirements/$ENV.txt

COPY . .
