all: clean build zip-clean zip

build:
	python3 -m build .

clean:
	rm -rf build/ dist/

test:
	pytest --cov=src/satyrus --cov-report html src/satyrus/tests/

deploy:
	python3 -m twine upload dist/*

zip: zip-clean
	zip Satyrus3.zip ./*

zip-clean:
	rm Satyrus3.zip

install:
	@pip install .[all] -q --use-feature=in-tree-build

install-dev:
	@pip install .[dev] -q --use-feature=in-tree-build