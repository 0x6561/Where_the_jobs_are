#!/bin/bash
export FLASK_APP=svr.py # which script to run
export FLASK_ENV=development # enable debug mode
flask run --host=0.0.0.0 # run and allow ANY host
