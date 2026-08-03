from django.shortcuts import render
from django.template import RequestContext
from django.contrib import messages
from django.http import HttpResponse
import os
import pandas as pd
import numpy as np
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
import pymysql
from django.views.decorators.csrf import csrf_exempt
import os
import speech_recognition as sr
import subprocess
from numpy import dot
from numpy.linalg import norm
from django.core.files.storage import FileSystemStorage
import random
import json
from keras import layers, activations, models, preprocessing, optimizers
from keras.utils import to_categorical
import re
import matplotlib.pyplot as plt
import io
import base64
from datetime import date
from googletrans import Translator

translator = Translator()
global uname, X, Y, vectorizer, tfidf
recognizer = sr.Recognizer()

X = []
Y = []

with open("Dataset/covid-19.json") as f:
    json_data = json.load(f)

json_data = json_data['intents']
for i in range(len(json_data)):
    question = json_data[i]['patterns']
    answer = json_data[i]['responses']
    for i in range(len(question)):
        for j in range(len(answer)):
            X.append(question[i].strip().lower())
            Y.append(answer[j])

tokenizer = preprocessing.text.Tokenizer()
tokenizer.fit_on_texts( X + Y )
VOCAB_SIZE = len( tokenizer.word_index )+1

vocab = []
for word in tokenizer.word_index:
    vocab.append(word)

def tokenize(sentences):
    tokens_list = []
    vocabulary = []
    for sentence in sentences:
        sentence = sentence.lower()
        sentence = re.sub('[^a-zA-Z0-9]', ' ', sentence)
        tokens = sentence.split()
        vocabulary += tokens
        tokens_list.append(tokens)
    return tokens_list, vocabulary

#encoder_input_data
tokenized_questions = tokenizer.texts_to_sequences(X)
maxlen_questions = max( [len(x) for x in tokenized_questions ] )
padded_questions = preprocessing.sequence.pad_sequences( tokenized_questions, maxlen = maxlen_questions, padding = 'post')
encoder_input_data = np.array(padded_questions)
print(encoder_input_data.shape, maxlen_questions)

# decoder_input_data
tokenized_answers = tokenizer.texts_to_sequences(Y)
maxlen_answers = max( [ len(x) for x in tokenized_answers ] )
padded_answers = preprocessing.sequence.pad_sequences( tokenized_answers , maxlen=maxlen_answers , padding='post' )
decoder_input_data = np.array( padded_answers )
print( decoder_input_data.shape , maxlen_answers )


# decoder_output_data
tokenized_answers = tokenizer.texts_to_sequences(Y)
for i in range(len(tokenized_answers)) :
    tokenized_answers[i] = tokenized_answers[i][1:]
padded_answers = preprocessing.sequence.pad_sequences( tokenized_answers , maxlen=maxlen_answers , padding='post' )
onehot_answers = to_categorical( padded_answers , VOCAB_SIZE )
decoder_output_data = np.array( onehot_answers )
print( decoder_output_data.shape )


encoder_inputs = layers.Input(shape=( maxlen_questions , ))
encoder_embedding = layers.Embedding( VOCAB_SIZE, 200 , mask_zero=True ) (encoder_inputs)
encoder_outputs , state_h , state_c = layers.LSTM( 200 , return_state=True )( encoder_embedding )
encoder_states = [ state_h , state_c ]

decoder_inputs = layers.Input(shape=( maxlen_answers ,  ))
decoder_embedding = layers.Embedding( VOCAB_SIZE, 200 , mask_zero=True) (decoder_inputs)
decoder_lstm = layers.LSTM( 200 , return_state=True , return_sequences=True )
decoder_outputs , _ , _ = decoder_lstm ( decoder_embedding , initial_state=encoder_states )
decoder_dense = layers.Dense( VOCAB_SIZE , activation='softmax') 
output = decoder_dense ( decoder_outputs )

model = models.Model([encoder_inputs, decoder_inputs], output )
model.compile(optimizer=optimizers.RMSprop(), loss='categorical_crossentropy', metrics = ['accuracy'])

if os.path.exists("model/model.h5") == False:
    hist = model.fit([encoder_input_data , decoder_input_data], decoder_output_data, batch_size=50, epochs=150) 
    model.save('model/model.h5')
    f = open('model/lstm_history.pckl', 'wb')
    pickle.dump(hist.history, f)
    f.close()    
else:
    model.load_weights('model/model.h5')

vectorizer = TfidfVectorizer(use_idf=True, smooth_idf=False, norm=None, decode_error='replace')
tfidf = vectorizer.fit_transform(X).toarray()

def TrainModel(request):
    if request.method == 'GET':
        f = open('model/lstm_history.pckl', 'rb')
        data = pickle.load(f)
        f.close()
        accuracy = data['accuracy'][140]
        accuracy_value = data['accuracy']
        loss_value = data['loss']
        plt.figure(figsize=(8,5))
        plt.grid(True)
        plt.xlabel('EPOCH')
        plt.ylabel('Accuracy/Loss')
        plt.plot(accuracy_value, 'ro-', color = 'green')
        plt.plot(loss_value, 'ro-', color = 'red')
        plt.legend(['VGG16', 'Resnet50','Modified VGG19','Modified MobileNetV2'], loc='upper left')
        plt.title('LSTM Training Accuracy & Loss Graph')
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight')
        plt.close()
        img_b64 = base64.b64encode(buf.getvalue()).decode()    
        context= {'data':'LSTM Training Accuracy : '+str(accuracy), 'img': img_b64}
        return render(request, 'UserScreen.html', context)

def TextChatbot(request):
    if request.method == 'GET':
        return render(request, 'TextChatbot.html', {})

def Chatbot(request):
    if request.method == 'GET':
        return render(request, 'Chatbot.html', {})

def saveHistory(text, output):
    global uname
    today = date.today()
    db_connection = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'MedicalChatbot',charset='utf8')
    db_cursor = db_connection.cursor()
    student_sql_query = "INSERT INTO history(username, question, answer, chat_date) VALUES('"+uname+"','"+text+"','"+output+"','"+str(today)+"')"
    db_cursor.execute(student_sql_query)
    db_connection.commit()

def ChatData(request):
    if request.method == 'GET':
        global Y, vectorizer, tfidf, questions
        question = request.GET.get('mytext', False)
        query = question
        print(query)
        arr = query
        arr = arr.strip().lower()
        testData = vectorizer.transform([arr]).toarray()
        testData = testData[0]
        print(testData.shape)
        output =  "unable to recognize"
        max_accuracy = 0
        index = -1
        recommend = []
        for i in range(len(tfidf)):
            predict_score = dot(tfidf[i], testData)/(norm(tfidf[i])*norm(testData))
            if predict_score > max_accuracy:
                max_accuracy = predict_score
                index = i
                recommend.append(i)
        output = ""
        if index != -1:
            output = Y[index]                 
        else:
            output = "Unable to predict answers. Please Try Again"
        saveHistory(question, output)     
        print(output)    
        return HttpResponse("Chatbot: "+output+"\n"+translator.translate(output, dest='te').text, content_type="text/plain")

@csrf_exempt
def record(request):
    if request.method == "POST":
        global Y, vectorizer, tfidf, questions, recognizer
        print("Enter")
        audio_data = request.FILES.get('data')
        fs = FileSystemStorage()
        if os.path.exists('ChatApp/static/record.wav'):
            os.remove('ChatApp/static/record.wav')
        if os.path.exists('ChatApp/static/record1.wav'):
            os.remove('ChatApp/static/record1.wav')    
        fs.save('ChatApp/static/record.wav', audio_data)
        path = 'E:/vittal/March24/MedicalChatbot/ChatApp/static/'
        res = subprocess.check_output(path+'ffmpeg.exe -i '+path+'record.wav '+path+'record1.wav', shell=True)
        with sr.WavFile('ChatApp/static/record1.wav') as source:
            audio = recognizer.record(source)
        try:
            text = recognizer.recognize_google(audio)
        except Exception as ex:
            text = "unable to recognize"
        output =  "unable to recognize"
        max_accuracy = 0
        index = -1
        recommend = []
        if text != "unable to recognize":
            temp = []
            query = text
            print(query)
            arr = query
            arr = arr.strip().lower()
            testData = vectorizer.transform([arr]).toarray()
            testData = testData[0]
            print(testData.shape)
            for i in range(len(tfidf)):
                predict_score = dot(tfidf[i], testData)/(norm(tfidf[i])*norm(testData))
                if predict_score > max_accuracy:
                    max_accuracy = predict_score
                    index = i
                    recommend.append(i)
        output = ""
        if index != -1:
            output = Y[index]                  
        else:
            output = "Unable to recognize. Please Try Again"
        if text != "unable to recognize":
            saveHistory(text, output)    
        print(output)    
        return HttpResponse("Chatbot: "+output+"\n"+translator.translate(output, dest='te').text, content_type="text/plain")    

def Signup(request):
    if request.method == 'GET':
       return render(request, 'Signup.html', {})

def index(request):
    if request.method == 'GET':
       return render(request, 'index.html', {})

def UserLogin(request):
    if request.method == 'GET':
       return render(request, 'UserLogin.html', {})
    
def UserLoginAction(request):
    if request.method == 'POST':
        global uname
        username = request.POST.get('t1', False)
        password = request.POST.get('t2', False)
        index = 0
        con = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'MedicalChatbot',charset='utf8')
        with con:    
            cur = con.cursor()
            cur.execute("select * FROM register")
            rows = cur.fetchall()
            for row in rows:
                if row[0] == username and password == row[1]:
                    uname = username
                    index = 1
                    break		
        if index == 1:
            context= {'data':'welcome '+username}
            return render(request, 'UserScreen.html', context)
        else:
            context= {'data':'login failed'}
            return render(request, 'UserLogin.html', context)


def SignupAction(request):
    if request.method == 'POST':
        username = request.POST.get('t1', False)
        password = request.POST.get('t2', False)
        contact = request.POST.get('t3', False)
        email = request.POST.get('t4', False)
        address = request.POST.get('t5', False)
        status = "none"
        con = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'MedicalChatbot',charset='utf8')
        with con:    
            cur = con.cursor()
            cur.execute("select * FROM register")
            rows = cur.fetchall()
            for row in rows:
                if row[0] == username:
                    status = "Username already exists"
                    break
        if status == "none":
            db_connection = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'MedicalChatbot',charset='utf8')
            db_cursor = db_connection.cursor()
            student_sql_query = "INSERT INTO register(username,password,contact,email,address) VALUES('"+username+"','"+password+"','"+contact+"','"+email+"','"+address+"')"
            db_cursor.execute(student_sql_query)
            db_connection.commit()
            print(db_cursor.rowcount, "Record Inserted")
            if db_cursor.rowcount == 1:
                status = "Signup Process Completed. You can Login now"
        context= {'data': status}
        return render(request, 'Signup.html', context)

def ViewHistory(request):
    if request.method == 'GET':
        global uname
        output = ''
        output+='<table border=1 align=center width=100%><tr><th><font size="" color="black">Username</th><th><font size="" color="black">Question</th><th><font size="" color="black">Chatbot Response</th>'
        output+='<th><font size="" color="black">Date</th></tr>'
        con = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'MedicalChatbot',charset='utf8')
        with con:
            cur = con.cursor()
            cur.execute("select * from history where username='"+uname+"'")
            rows = cur.fetchall()
            output+='<tr>'
            for row in rows:
                output+='<td><font size="" color="black">'+row[0]+'</td><td><font size="" color="black">'+str(row[1])+'</td><td><font size="" color="black">'+row[2]+'</td><td><font size="" color="black">'+row[3]+'</td></tr>'
        output+= "</table></br></br></br></br>"        
        context= {'data':output}
        return render(request, 'UserScreen.html', context)    





    
