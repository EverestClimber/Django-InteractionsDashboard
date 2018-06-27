#!/usr/bin/env bash

python manage.py loaddata data/dev_fixtures/affiliate_groups.json
python manage.py loaddata data/dev_fixtures/therapeutic_areas.json
python manage.py loaddata data/dev_fixtures/projects.json
python manage.py loaddata data/dev_fixtures/hcps.json
python manage.py loaddata data/dev_fixtures/engagement_plans.json
python manage.py loaddata data/dev_fixtures/engagement_plan_hcp_items.json
python manage.py loaddata data/dev_fixtures/engagement_plan_project_items.json
python manage.py loaddata data/dev_fixtures/hcp_objectives.json
python manage.py loaddata data/dev_fixtures/hcp_deliverables.json
python manage.py loaddata data/dev_fixtures/project_objectives.json
python manage.py loaddata data/dev_fixtures/project_deliverables.json
