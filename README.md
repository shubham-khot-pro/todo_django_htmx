# Simple Django + HTMX + Postgres Todo App

A minimal, reactive Todo application using **Django** for the backend, **Postgres** for the database, and **HTMX** for dynamic frontend updates without full page reloads.

---

## 🛠 Prerequisites

* Python 3.10+
* PostgreSQL installed and running
* A virtual environment tool (`venv` or `pipenv`)

---

## 🚀 Quick Start

### 1. Clone & Setup Environment
```bash
git clone https://github.com/shubham-khot-pro/todo_django_htmx
cd django-htmx-todo
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

```

### 2. Database Configuration

Create a database in Postgres named `todo_db`. Update your `settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'todo_db',
        'USER': 'your_postgres_user',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

```

### 3. Migrations 

```bash
python3 manage.py makemigration
python3 manage.py migrate

```

### 4. Run the Server

```bash
python3 manage.py runserver

```

Visit `http://127.0.0.1:8000` to see your app.

---

## ⚡ HTMX Integration Snippet

This app uses HTMX to handle tasks asynchronously. For example, deleting a task:

```html
<div id="task-{{ task.id }}">
    <span>{{ task.title }}</span>
    <button hx-delete="{% url 'delete-task' task.id %}" 
            hx-target="#task-{{ task.id }}" 
            hx-swap="outerHTML">
        Delete
    </button>
</div>

```

---

## 📂 Project Structure

* `my_todo` - Project settings (main project)
* `todo_app` - App logic (Models, Views, Templates)
* `templates/` - HTML files with HTMX attributes
* `static/` - CSS/JS (including `htmx.min.js`)

---

## 📝 Features

* **Add Tasks:** Create new items via AJAX.
* **Toggle Status:** Mark as complete/incomplete instantly.
* **Delete:** Remove items without refreshing the page.
* **Persistent Storage:** All data stored in PostgreSQL.

```


```
