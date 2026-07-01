# task-manager-python-capstone



### torun(Bash) #####
# In task_manager/ directory with venv activated
$ source .venv/Scripts/activate
uvicorn app.main:app --reload

# http://localhost:8000/docs

### POST #########

curl -X POST http://localhost:8000/categories/ -H "Content-Type: application/json" -d '{"name": "Work" , "color": "#FF0000"}'
curl http://127.0.0.1:8000/categories/


task_manager/
├── app/
│   ├── __init__.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── crud.py
│   ├── main.py
│   └── routers/
│       ├── __init__.py
│       └── categories.py
└── tests/
    ├── __init__.py
    ├── conftest.py
    └── test_categories.py