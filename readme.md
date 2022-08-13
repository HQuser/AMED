# Server-Side Execution
This is a Django-based (Python) project

## Example Use-Case
This project has been designed to understand users discovery information needs. 
This system may be used by non-developers or search system developers to extend or learn without the system without need to write code or have a deep understanding of complex algorithms used.

## Usage
1. Place respective API Keys in "discovery\model\research\api_calls.py" to retireve real-time web search engine contents 
2. In the project directory, install dependencies using:
```commandline
pip install -r requirements.txt
```
3. Start the project using:
```commandline
python manage.py runserver
```
4. Navigate to `http://127.0.0.1:8000/` in your web browser to view the app. If you have another web app running, use:
```commandline
python manage.py runserver 8080
```

## Structure
Core project is named 'discovery'. There is a single app called 'discovery'. The base HTML file is templates/index.html. 

```bash
discovery
|   db.sqlite3
|   manage.py
|           
+---research
|   |   admin.py
|   |   apps.py
|   |   forms.py
|   |   models.py
|   |   tests.py
|   |   urls.py
|   |   views.py
|   |   __init__.py
|   |   
|   |           
|   +---templates
|   |       contents_doc.html
|   |       contents_snip.html
|   |       content.html
|   |       doct_preview.html
|   |       index.html
|   |       start_page.html
|   |       viz.html
|   |       
|           
+---discovery
|   |   asgi.py
|   |   settings.py
|   |   urls.py
|   |   wsgi.py
|   |   __init__.py
|           
+---model
|   +---research
|   |       * This contains all the backend logic including deep learning algorithms
|   |       
|   +---myutils
+---static
|   +---research
|   |   css
|   |   icons
|   |   js 
        
```

## Dependencies
The venv was created using Python 3.7. Packages required are found in requirements.txt