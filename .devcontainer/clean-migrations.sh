#! /bin/bash

find ../leaderboard/ -name migrations -type d | xargs rm -r
docker-compose exec -T db psql -U postgres -c 'DROP DATABASE IF EXISTS leaderboard;'
docker-compose exec -T db su - postgres -c 'createdb leaderboard'