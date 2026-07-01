# task-manager-python-capstone



### torun(Bash) #####
# In task_manager/ directory with venv activated
$ source .venv/Scripts/activate
uvicorn app.main:app --reload

# http://localhost:8000/docs


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