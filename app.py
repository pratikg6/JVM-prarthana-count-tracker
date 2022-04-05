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
from gspread_dataframe import get_as_dataframe, set_with_dataframe




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
                        
        worksheet = sh.sheet1


        df = get_as_dataframe(worksheet, parse_dates=True, skiprows=0, header=None)
        data=df.dropna(axis = 1, how ='all')
        data=data.dropna(axis = 0, how ='all')
        
        data=data.fillna(0)
        
        
        
        lastdate=data.loc[0].tolist()[-1]
        data.columns = data.iloc[0]
        
        if date!=lastdate:
            data[date]=''
            data[date].loc[0]=date
        
        
        namelist=data.Name.unique().tolist()
        name=form_data['Name']        
        match={}
        count=form_data['Count']
        for n in namelist:
            temp=fuzz.ratio(name,n)
            match[n]=temp    
        perfect= max(match, key=match.get)
        length=len(data)
        if name not in namelist and match[perfect]<75:
            data.loc[length, 'Mobile Number'] = name
            data.loc[length, 'Serial Number'] = length+1
            data.loc[data['Mobile Number']==name,date]=count
            total=data[data['Mobile Number']==name].iloc[0].tolist()
        else:
            data.loc[data['Mobile Number']==perfect,date]=count
            total=data[data['Mobile Number']==perfect].iloc[0].tolist()
            
        
        data=data.fillna(0)
        
        
        set_with_dataframe(worksheet, data,include_column_header=False)
        
        todaysum=data[date].loc[1:].astype(int).sum()

        
        total=total[4 :]
        total=[int(x) for x in total]
        total=sum(total)

        
        
        return render_template('data.html',form_data = form_data, value=todaysum, total=total)
 
if __name__=='__main__':
 app.run(debug=True)
