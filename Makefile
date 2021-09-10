all: build

build:
	python3 -m build .

clean:
	rm -rf build/ dist/

deploy:
	python3 -m twine upload dist/*