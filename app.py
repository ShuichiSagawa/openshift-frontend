from flask import Flask, jsonify, render_template_string, request
import os
import requests
import socket

app = Flask(__name__)

# バックエンドAPIのURL（環境変数から取得）
BACKEND_URL = os.getenv('BACKEND_URL', 'http://api-server:8080')

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>OpenShift Frontend</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        h1 { color: #ee0000; }
        .info { background: #e7f5ff; padding: 15px; border-radius: 4px; margin: 20px 0; }
        .items { margin-top: 20px; }
        .item { background: #f8f9fa; padding: 10px; margin: 5px 0; border-radius: 4px; }
        .error { background: #ffe0e0; padding: 15px; border-radius: 4px; color: #cc0000; }
        button { background: #ee0000; color: white; border: none; padding: 10px 20px; border-radius: 4px; cursor: pointer; }
        button:hover { background: #cc0000; }
        input { padding: 8px; margin: 5px; border: 1px solid #ddd; border-radius: 4px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>OpenShift Frontend</h1>
        <div class="info">
            <strong>Frontend Host:</strong> {{ frontend_host }}<br>
            <strong>Backend URL:</strong> {{ backend_url }}
        </div>

        <h2>Backend Status</h2>
        {% if backend_status %}
        <div class="info">
            <strong>Service:</strong> {{ backend_status.service }}<br>
            <strong>Hostname:</strong> {{ backend_status.hostname }}<br>
            <strong>Version:</strong> {{ backend_status.version }}
        </div>
        {% else %}
        <div class="error">Backend connection failed: {{ error }}</div>
        {% endif %}

        <h2>Items from API</h2>
        <div class="items">
        {% for item in items %}
            <div class="item">
                <strong>#{{ item.id }}</strong>: {{ item.name }} - {{ item.description }}
            </div>
        {% else %}
            <div class="error">No items available</div>
        {% endfor %}
        </div>

        <h2>Add New Item</h2>
        <form action="/add-item" method="POST">
            <input type="text" name="name" placeholder="Item name" required>
            <input type="text" name="description" placeholder="Description">
            <button type="submit">Add Item</button>
        </form>
    </div>
</body>
</html>
'''

@app.route('/')
def index():
    frontend_host = socket.gethostname()
    backend_status = None
    items = []
    error = None

    try:
        resp = requests.get(f'{BACKEND_URL}/', timeout=5)
        backend_status = resp.json()
    except Exception as e:
        error = str(e)

    try:
        resp = requests.get(f'{BACKEND_URL}/api/items', timeout=5)
        items = resp.json().get('items', [])
    except:
        pass

    return render_template_string(HTML_TEMPLATE,
        frontend_host=frontend_host,
        backend_url=BACKEND_URL,
        backend_status=backend_status,
        items=items,
        error=error
    )

@app.route('/add-item', methods=['POST'])
def add_item():
    name = request.form.get('name')
    description = request.form.get('description', '')
    try:
        requests.post(f'{BACKEND_URL}/api/items',
            json={'name': name, 'description': description}, timeout=5)
    except:
        pass
    return '<script>window.location.href="/";</script>'

@app.route('/health')
def health():
    return jsonify({'status': 'healthy'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
