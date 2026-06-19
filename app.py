from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from datetime import datetime
import json
import os

app = Flask(__name__)
app.secret_key = "campuscash2026"

# In-memory storage
users = {}
transactions = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    name = data.get('name')
    matric = data.get('matric')
    department = data.get('department')
    password = data.get('password')
    if matric in users:
        return jsonify({'success': False, 'message': 'Matric number already registered!'})
    users[matric] = {
        'name': name,
        'matric': matric,
        'department': department,
        'password': password
    }
    transactions[matric] = []
    session['user'] = matric
    return jsonify({'success': True, 'name': name})

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    matric = data.get('matric')
    password = data.get('password')
    if matric in users and users[matric]['password'] == password:
        session['user'] = matric
        if matric not in transactions:
            transactions[matric] = []
        return jsonify({'success': True, 'name': users[matric]['name']})
    return jsonify({'success': False, 'message': 'Invalid matric number or password!'})

@app.route('/logout')
def logout():
    session.pop('user', None)
    return jsonify({'success': True})

@app.route('/add_transaction', methods=['POST'])
def add_transaction():
    if 'user' not in session:
        return jsonify({'success': False, 'message': 'Not logged in!'})
    data = request.get_json()
    matric = session['user']
    transaction = {
        'id': datetime.now().strftime('%Y%m%d%H%M%S%f'),
        'type': data.get('type'),
        'category': data.get('category'),
        'description': data.get('description'),
        'amount': float(data.get('amount')),
        'date': datetime.now().strftime('%d %b %Y, %H:%M')
    }
    transactions[matric].append(transaction)
    return jsonify({'success': True, 'transaction': transaction})

@app.route('/get_data')
def get_data():
    if 'user' not in session:
        return jsonify({'success': False})
    matric = session['user']
    user_transactions = transactions.get(matric, [])
    income = sum(t['amount'] for t in user_transactions if t['type'] == 'income')
    expenses = sum(t['amount'] for t in user_transactions if t['type'] == 'expense')
    balance = income - expenses
    # Category breakdown
    categories = {}
    for t in user_transactions:
        if t['type'] == 'expense':
            cat = t['category']
            categories[cat] = categories.get(cat, 0) + t['amount']
    return jsonify({
        'success': True,
        'income': income,
        'expenses': expenses,
        'balance': balance,
        'transactions': list(reversed(user_transactions)),
        'categories': categories,
        'user': users.get(matric, {})
    })

@app.route('/delete_transaction', methods=['POST'])
def delete_transaction():
    if 'user' not in session:
        return jsonify({'success': False})
    data = request.get_json()
    matric = session['user']
    transactions[matric] = [t for t in transactions[matric] if t['id'] != data.get('id')]
    return jsonify({'success': True})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
    