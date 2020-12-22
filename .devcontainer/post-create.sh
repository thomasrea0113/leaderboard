#! /bin/bash

# will only work from within the .devcontainer folder
echo "alias dbexec='docker-compose exec db '" >>~/.bashrc
echo "alias psql='docker-compose exec db psql -U postgres '" >>~/.bashrc

cd .devcontainer
docker-compose exec -T db psql -U postgres -c 'DROP DATABASE IF EXISTS leaderboard;'
docker-compose exec -T db su - postgres -c 'createdb leaderboard'
