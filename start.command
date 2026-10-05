#!/bin/bash
cd "$(dirname "$0")"
python3 -m venv venv
source venv/bin/activate
pip install -q -r requirements.txt
[ -f instance/blog.db ] || python seed.py
(sleep 2; open http://127.0.0.1:5001) &
python app.py
