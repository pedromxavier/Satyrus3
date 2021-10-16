ifeq ($(OS),Windows_NT)
	fname=".\Makefiles\windows.mk"
else
	fname="./Makefiles/linux.mk"
endif

all: clean build zip

build:
	@make build --makefile=$(fname)

clean:
	@make clean --makefile=$(fname)

test:
	pytest --cov=src/satyrus --cov-report html src/satyrus/tests/

deploy:
	@make deploy --makefile=$(fname)

zip:
	@make zip --makefile=$(fname)

install:
	@pip install .[dev] -q --use-feature=in-tree-build