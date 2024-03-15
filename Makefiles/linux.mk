build:
	@python3 -m build .

clean:
	@rm -rf build/ dist/ htmlcov/ .coverage .pytest_cache

deploy:
	@python3 -m twine upload dist/*

zip:
	@rm -f Satyrus3.zip
	@zip Satyrus3.zip /*