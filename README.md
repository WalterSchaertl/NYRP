# NYRP: New York Regents Preparation

## Overview
Current project for a website to help prepare for a New York Regents
test. Students can select questions by the the year it appeared, or
by the topic it covers. Unlimited attempts are allowed per question so
students can get immediate feedback. After answering all questions or
ending the test at any point, more in-dept analysis is provided giving
students feedback on their best and worst topics. The live version
can be found here: https://regents-prep.herokuapp.com/NYRP/

## Outside Libraries
- BootStrap:  3.3.5
- JQuery:     2.1.4
- Django-widget-tweaks 1.4.8
- CSS Percentage Circle
- Google Visualization: Pie Chart

## Getting Set Up Locally
1. To get a local copy, clone this repo
`git clone git@github.com:WalterSchaertl/NYRP.git`
2. Install pip dependencies from the requirements.txt (requires python3)
`pip3 install -r requirements.txt`
3. In a terminal, start the server
`python3 manage.py runserver 0.0.0.0:8000`

Note: if you run into issues, in settings.py, ensure that debug is true
(`DEBUG = True`) and all hosts are allowed (`ALLOWED_HOSTS = ["*"]`).

## Docker
If desired to run as a container, a Dockerfile and docker-compse.yml are provided.