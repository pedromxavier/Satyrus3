all: build

build:
	python3 -m build .

clean:
	rm -rf build/ dist/

deploy:
	python3 -m twine upload dist/*

zip: zip-clean
	zip Satyrus3.zip ./*

zip-clean:
	rm Satyrus3.zip