# CHATBOT

A simple Django-based chatbot app with a Python code execution page.

## Overview

This repository contains a lightweight Django project that provides:

- A chatbot interface powered by a local intent-response dataset (`covid-19.json`).
- A page for uploading or pasting Python source code to execute on the server.
- A minimal Django routing setup with home, chat, and execution endpoints.

## Features

- Chatbot interface using basic keyword matching.
- Python code execution page for `.py` uploads or pasted code.
- Simple JSON-driven intents and responses.
- Local dev server compatibility.

## Prerequisites

- Python 3 installed
- `pip` available for package installation
- Git access if cloning or pushing changes

## Install and run locally

```bash
cd /workspaces/CHATBOT
python3 -m pip install -r requirements.txt
python3 manage.py runserver 0.0.0.0:8002
```

Then open the browser at `http://127.0.0.1:8002/`.

## App pages

- `/` → Chatbot interface
- `/TextChatbot.html` → Chatbot UI page (same as home)
- `/ExecuteProgram` → Python code execution page
- `/ChatData?mytext=...` → Returns chatbot response text

## Using the chatbot

1. Open the home page.
2. Type a question into the chatbot input.
3. Submit to receive a simple response from the intent matcher.

Example questions:

- `hello`
- `what is covid` 
- `how can i protect myself`

## Using Python execution

1. Open `/ExecuteProgram`.
2. Upload a `.py` file or paste Python code into the textarea.
3. Submit and view the output on the page.

## Project structure

- `views.py` — Django view logic for chat and code execution.
- `urls.py` — URL routing configuration.
- `templates/` — HTML templates for the home, chatbot, and execution pages.
- `covid-19.json` — Intent data used by the chatbot.
- `requirements.txt` — Python dependencies.

## Security note

This app runs uploaded code directly with `python3`. Do not expose it to untrusted users in production.

## Notes

- Uploaded code is saved to `uploads/` and executed using `python3`.
- The chatbot uses a local JSON file for intents and responses.
