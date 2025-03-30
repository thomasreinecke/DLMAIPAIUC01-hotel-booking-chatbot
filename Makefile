# Variables
VENV = backend/.venv
FRONTEND_DIR = frontend

.PHONY: all install clean test frontend backend

all: install

## Install both frontend and backend dependencies
install: backend frontend

## Backend setup
backend:
	@echo "Cleaning backend..."
	@rm -rf __pycache__
	@rm -rf $(VENV)
	@echo "Creating virtual environment..."
	python3 -m venv $(VENV)
	@echo "Installing certifi..."
	$(VENV)/bin/pip install certifi --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org
	@echo "Capturing certifi certificate bundle path and upgrading pip/installing requirements..."
	@CERT="$$( $(VENV)/bin/python -m certifi )"; \
	echo "Certifi installed at: $$CERT"; \
	echo "Upgrading pip..."; \
	$(VENV)/bin/pip install --upgrade pip --cert=$$CERT --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org; \
	echo "Installing remaining requirements..."; \
	$(VENV)/bin/pip install -r backend/requirements.txt --cert=$$CERT --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org
	@echo "Backend installation complete."

## Frontend setup
frontend:
	@echo "Cleaning frontend..."
	@rm -rf $(FRONTEND_DIR)/node_modules
	@echo "Installing frontend dependencies..."
	@cd $(FRONTEND_DIR) && npm install
	@echo "Frontend setup complete."

## Clean both frontend and backend environments
clean:
	@echo "Cleaning backend..."
	@rm -rf $(VENV)
	@find backend -type d -name '__pycache__' -exec rm -rf {} +
	@echo "Cleaning frontend..."
	@rm -rf $(FRONTEND_DIR)/node_modules
	@echo "Cleanup complete."

## Run backend tests
test: backend
	@echo "Running backend tests..."
	@$(VENV)/bin/pytest backend/tests/

## Run the backend API server
run-backend:
	@echo "Starting backend server..."
	@$(VENV)/bin/uvicorn backend.app.main:app --reload

## Run the frontend (SvelteKit)
run-frontend:
	@echo "Starting frontend..."
	@cd $(FRONTEND_DIR) && npm run dev

## Run both frontend and backend concurrently
run: run-backend run-frontend
