build:
	python -m build .

clean:
	rm -rf build/ dist/

test:
	pytest --cov=src/satyrus --cov-report html src/satyrus/tests/

deploy:
	python -m twine upload dist/*

zip: zip-clean
	zip Satyrus3.zip ./*

zip-clean:
	rm Satyrus3.zip