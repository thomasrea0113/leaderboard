export DOCKER_COMPOSE_FILES='-f /workspace/.devcontainer/docker-compose.yml -f /workspace/.devcontainer/docker-compose.develop.yml'

alias dbexec="docker-compose $DOCKER_COMPOSE_FILES exec db "
alias psql="docker-compose $DOCKER_COMPOSE_FILES exec db psql -U postgres "

recreate_db() {
    docker-compose $DOCKER_COMPOSE_FILES exec -T db psql -U postgres -c 'DROP DATABASE IF EXISTS leaderboard;'
    docker-compose $DOCKER_COMPOSE_FILES exec -T db su - postgres -c 'createdb leaderboard'
}

clean_migrations() {
    find /workspace/leaderboard/ -name migrations -type d | xargs rm -r
    recreate_db
}
