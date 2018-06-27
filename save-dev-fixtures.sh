#!/usr/bin/env bash

python manage.py dumpdata --indent 2 interactionscore.affiliategroup > data/dev_fixtures/affiliate_groups.json
python manage.py dumpdata --indent 2 interactionscore.therapeuticarea > data/dev_fixtures/therapeutic_areas.json
python manage.py dumpdata --indent 2 interactionscore.project > data/dev_fixtures/projects.json
python manage.py dumpdata --indent 2 interactionscore.hcp > data/dev_fixtures/hcps.json
python manage.py dumpdata --indent 2 interactionscore.engagementplan > data/dev_fixtures/engagement_plans.json
python manage.py dumpdata --indent 2 interactionscore.engagementplanhcpitem > data/dev_fixtures/engagement_plan_hcp_items.json
python manage.py dumpdata --indent 2 interactionscore.engagementplanprojectitem > data/dev_fixtures/engagement_plan_project_items.json
python manage.py dumpdata --indent 2 interactionscore.hcpobjective > data/dev_fixtures/hcp_objectives.json
python manage.py dumpdata --indent 2 interactionscore.hcpdeliverable > data/dev_fixtures/hcp_deliverables.json
python manage.py dumpdata --indent 2 interactionscore.projectobjective > data/dev_fixtures/project_objectives.json
python manage.py dumpdata --indent 2 interactionscore.projectdeliverable > data/dev_fixtures/project_deliverables.json
