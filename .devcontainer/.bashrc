export DOCKER_COMPOSE_FILES='-f /workspace/.devcontainer/docker-compose.yml -f /workspace/.devcontainer/docker-compose.develop.yml'

alias dbexec="docker-compose $DOCKER_COMPOSE_FILES exec db "
alias psql="docker-compose $DOCKER_COMPOSE_FILES exec db psql -U postgres "
alias pgadmin4="docker run -p 8989:8989 -e PGADMIN_LISTEN_PORT=8989 -e PGADMIN_LISTEN_ADDRESS=0.0.0.0 -e PGADMIN_DEFAULT_EMAIL=thomasrea0113@gmail.com -e PGADMIN_DEFAULT_PASSWORD=password dpage/pgadmin4"

recreate_db() {
    docker-compose $DOCKER_COMPOSE_FILES exec -T db psql -U postgres -c 'DROP DATABASE IF EXISTS leaderboard;'
    docker-compose $DOCKER_COMPOSE_FILES exec -T db su - postgres -c 'createdb leaderboard'
}

clean_migrations() {
    find /workspace/leaderboard/ -name migrations -type d | xargs rm -r
    recreate_db
}
