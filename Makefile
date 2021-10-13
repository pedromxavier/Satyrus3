ifeq ($(OS),Windows_NT)
	fname=".\Makefiles\windows.mk"
else
	fname="./Makefiles/linux.mk"
endif

all: clean build zip-clean zip

build:
	@make build --makefile=$(fname)

clean:
	@make clean --makefile=$(fname)

test:
	pytest --cov=src/satyrus --cov-report html src/satyrus/tests/

deploy:
	@make deploy --makefile=$(fname)

zip: zip-clean
	zip Satyrus3.zip ./*

zip-clean:
	@make zip-clean --makefile=$(fname)

install:
	@pip install .[all] -q --use-feature=in-tree-build

install-dev:
	@pip install .[dev] -q --use-feature=in-tree-build