#!/bin/bash
python wsgi.py &
gunicorn --bind 0.0.0.0:$PORT wsgi:app
