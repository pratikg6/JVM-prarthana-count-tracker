# -*- coding: utf-8 -*-
"""
Created on Mon Apr  4 21:08:24 2022

@author: Niketan
"""

import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pprint
import pandas as pd
from datetime import datetime
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
from flask import Flask,render_template,request




app = Flask(__name__)
 
@app.route('/form')
def form():
    return render_template('form.html')
 
@app.route('/data', methods = ['POST', 'GET'])
def data():
    if request.method == 'GET':
        return f"The URL /data is accessed directly. Try going to '/form' to submit form"
    if request.method == 'POST':
        form_data = request.form
        
        print(form_data)
        date=datetime.today().strftime('%d-%m-%Y')
        scope = [
            'https://www.googleapis.com/auth/drive',
            'https://www.googleapis.com/auth/drive.file'
            ]
        file_name = 'credentials.json'
        
        
        
        
        gc = gspread.service_account(filename='credentials.json')
        sh = gc.open_by_key("1CWgx1CQhkaS7fvt7zQBVsDpNA6QiYfViA711yoQZAJc") # or by sheet name: gc.open("TestList")
        
        
        name=form_data['Name']
        count=form_data['Count']
        
        worksheet = sh.sheet1
        
        
        ### retrieve data ###
        #res = worksheet.get_all_records() # list of dictionaries
        res = worksheet.get_all_values() # list of lists
        
        
        data=pd.DataFrame(res)
        
        lastdate=data.loc[0].tolist()[-1]
        data.columns = data.iloc[0]
        #data=data.iloc[1: , :]
        #date='05-04-2022'
        if date!=lastdate:
            data[date]=''
            data[date].loc[0]=date
        
        
        namelist=data.Name.unique().tolist()
        
        
        match={}
        for n in namelist:
            if name in namelist:
                temp=fuzz.partial_ratio(name,n)
                match[n]=temp    
            else:
                pass
            
        perfect=max(match, key= lambda x: match[x])
        if match[perfect]<70:
            data.loc[data['Name']==name,date]=count
        else:
            data.loc[data['Name']==perfect,date]=count
        
        worksheet.clear()
        
        worksheet.update([data.columns.tolist()] + data.values.tolist())
      
        
        return render_template('data.html',form_data = form_data)
 

app.run(host='localhost', port=5000,debug=True)

"""
date=datetime.today().strftime('%d-%m-%Y')
scope = [
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/drive.file'
    ]
file_name = 'credentials.json'




gc = gspread.service_account(filename='credentials.json')
sh = gc.open_by_key("1CWgx1CQhkaS7fvt7zQBVsDpNA6QiYfViA711yoQZAJc") # or by sheet name: gc.open("TestList")


name='maruti kasture'
count=40

worksheet = sh.sheet1


### retrieve data ###
#res = worksheet.get_all_records() # list of dictionaries
res = worksheet.get_all_values() # list of lists


data=pd.DataFrame(res)

lastdate=data.loc[0].tolist()[-1]
data.columns = data.iloc[0]
#data=data.iloc[1: , :]
if date!=lastdate:
    data[date]=''
    data[date].loc[0]=date


namelist=data.Name.unique().tolist()


match={}
for n in namelist:    
    temp=fuzz.partial_ratio(name,n)
    match[n]=temp    
    
perfect=max(match, key= lambda x: match[x])
if match[perfect]<70:
    data.loc[data['Name']==name,date]=count
else:
    data.loc[data['Name']==perfect,date]=count

worksheet.clear()

worksheet.update([data.columns.values.tolist()] + data.values.tolist())

#AIzaSyDaaYjZ3iT6A97uiLEjGOGRY_2ZmkeXzEU

"""