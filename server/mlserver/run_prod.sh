#!/bin/bash
FLASK_ENV=production gunicorn -b 0.0.0.0:8666 app:app
