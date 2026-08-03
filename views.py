from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import os
import json
import random
import subprocess

intents = []
with open("covid-19.json") as f:
    json_data = json.load(f)
    for item in json_data.get('intents', []):
        patterns = [p.strip().lower() for p in item.get('patterns', []) if p]
        answers = item.get('responses', [])
        for pattern in patterns:
            intents.append({'pattern': pattern, 'responses': answers})


def find_response(text):
    text = text.strip().lower()
    if not text:
        return "Unable to predict answers. Please Try Again"

    text_words = set(text.split())
    best_item = None
    best_score = 0

    for item in intents:
        pattern_words = set(item['pattern'].split())
        score = len(text_words & pattern_words)
        if score > best_score:
            best_score = score
            best_item = item
        if item['pattern'] == text:
            return random.choice(item['responses']) if item['responses'] else "Sorry, I do not know."

    if best_item and best_item['responses']:
        return random.choice(best_item['responses'])
    return "Unable to predict answers. Please Try Again"


def index(request):
    return render(request, 'TextChatbot.html', {})


def text_chatbot(request):
    return render(request, 'TextChatbot.html', {})


def ChatData(request):
    if request.method == 'GET':
        question = request.GET.get('mytext', '')
        output = find_response(question)
        return HttpResponse("Chatbot: " + output, content_type="text/plain")


@csrf_exempt
def ExecuteProgram(request):
    if request.method == 'GET':
        return render(request, 'ExecuteProgram.html', {})

    code_file = request.FILES.get('codefile')
    code_text = request.POST.get('codearea', '')
    uploads_dir = os.path.join(os.getcwd(), 'uploads')
    os.makedirs(uploads_dir, exist_ok=True)

    if code_file:
        filename = code_file.name
        if not filename.lower().endswith('.py'):
            return HttpResponse('Only .py files are allowed.', content_type='text/plain')
        filepath = os.path.join(uploads_dir, filename)
        with open(filepath, 'wb') as f:
            f.write(code_file.read())
    elif code_text.strip():
        filename = 'uploaded_code.py'
        filepath = os.path.join(uploads_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(code_text)
    else:
        return HttpResponse('No code provided.', content_type='text/plain')

    try:
        completed = subprocess.run(['python3', filepath], capture_output=True, text=True, timeout=10)
        result = completed.stdout or ''
        if completed.stderr:
            result += '\n' + completed.stderr
        html = '<h2>Execution result</h2><pre>{}</pre>'.format(result.replace('<', '&lt;').replace('>', '&gt;'))
        return HttpResponse(html, content_type='text/html')
    except subprocess.TimeoutExpired:
        return HttpResponse('Execution timed out after 10 seconds.', content_type='text/plain')
    except Exception as ex:
        return HttpResponse('Error executing code: ' + str(ex), content_type='text/plain')





    
