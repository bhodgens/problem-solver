#PROJECT="/opt/problem-solver"
PROJECT="test"
PYTHON = $(shell which python || which python3)
install: 
	mkdir -p $(PROJECT) && cd $(PROJECT)
	$(PYTHON) -m venv problem-solver
	source problem-solver/bin/activate
	pip install -r requirements.txt
uninstall:
	rm -rf $(PROJECT)  
run: 
	cd $(PROJECT)
	problem-solver
	source venv/bin/activate
	echo "running on port 8000"
	python problemsolver.py 
	deactivate 
