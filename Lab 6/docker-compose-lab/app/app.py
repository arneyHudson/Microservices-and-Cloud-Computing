import json
from typing import Dict, List
import os
import sys
import mysql.connector
from flask import Flask, render_template

app = Flask(__name__, template_folder='./portfolio/templates', static_folder='./portfolio/static')

def get_projects() -> List[Dict]:
    config = {
        'user': 'root',
        'password': 'root',
        'host': 'db',
        'port': '3306',
        'database': 'portfolio'
    }
    
    try:
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor()
        cursor.execute('SELECT title, date_range, associated_with, background, project_goal, skills FROM projects')
        project_records = cursor.fetchall()
        print("Projects: ", projects)   

        # Convert the result into a list of dictionaries
        project_list = [{
            'title': title, 
            'date_range': date_range, 
            'associated_with': associated_with, 
            'background': background, 
            'project_goal': project_goal, 
            'skills': skills
        } for (title, date_range, associated_with, background, project_goal, skills) in project_records]

        cursor.close()
        connection.close()
        
        return project_list
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return []


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/projects')
def projects():
    project_list = json.dumps({'projects': get_projects()})
    print(json.loads(project_list))
    return render_template('projects.html', projects=project_list)

@app.route('/contact')
def contact():
    return render_template('contact.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
