#! /bin/bash
LINT="prospector --output-format pylint"

lint() {
    # all linting is done in the background for this session.
    # need to make sure no previous jobs are running
    if [[ `jobs -p | wc -l` != 0 ]]; then
        pgrep -s $$| grep -v $$ | xargs -r kill -KILL 2>/dev/null
        # even though we're terminating early, we need to echo
        # END LINT so that the vs code task will know linting is done
        echo END LINT
    fi

    # run the whole lint in the background
    (
        # lint just the active file first, for quicker editing
        echo BEGIN LINT
        if [ ! -z "$1" ]; then
            eval $LINT $1
        fi
        echo END LINT

        # lint the whole project
        echo BEGIN LINT
        eval $LINT
        echo END LINT
    ) &
}

lint
while :; do
    f=`inotifywait -rqe move,modify --format %w%f . | grep '\\.py$'`
    if [ ! -z "$f" ]; then
        lint $f
    fi
done
