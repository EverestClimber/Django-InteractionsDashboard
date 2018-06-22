#!/usr/bin/env bash

. /data/virtualenv/interactions/bin/activate

app_pull() {
    git pull \
        && sudo service uwsgi restart interactions
        #&& sudo service celery_interactions restart
}

app_restart() {
    sudo service uwsgi restart insights
        #&& sudo service celery_interactions restart
}

app_shell() {
    python manage.py shell_plus
}

app_tail_log() {
    less +F -i /data/sysop/logs/interactions/all.log
}
