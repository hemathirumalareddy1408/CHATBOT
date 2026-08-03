# CHATBOT

A simple Django-based chatbot app with a Python code execution page.

## Features

- Chatbot interface powered by simple intent matching from `covid-19.json`
- Python code execution page for uploading or pasting `.py` scripts
- Home page routes directly to the chatbot interface

## Run locally

```bash
cd /workspaces/CHATBOT
python3 -m pip install -r requirements.txt
python3 manage.py runserver 0.0.0.0:8002
```

Open the browser at `http://127.0.0.1:8002/`.

## Pages

- `/` → Chatbot interface
- `/ExecuteProgram` → Python code execution page
- `/ChatData?mytext=...` → Chatbot response endpoint

## Notes

- The chatbot uses a local JSON file for intents and responses.
- Uploaded code is saved to `uploads/` and executed with `python3`.
