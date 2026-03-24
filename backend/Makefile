install:
	python -m venv venv
	venv\Scripts\activate && pip install -r requirements.txt

run:
	uvicorn main:app --reload --port 8000

test:
	pytest tests/ -v