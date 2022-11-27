```console
create virtual environment        (python3 -m venv venv)
activate virtual environment      (.\venv\Scripts\activate)

pip install fastapi
pip install "uvicorn[standard]"
pip install python-multipart sqlalchemy jinja2

uvicorn app:app --reload        or      uvicorn app:app --host <IP ADDRESS> --port <PORT NUMBER>
```
