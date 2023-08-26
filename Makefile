##@ Label sections
.PHONY: help
help:  # Display this help
	@grep -E '^[a-zA-Z0-9 -]+:.*#'  Makefile | sort | while read -r l; do printf "\033[1;32m$$(echo $$l | cut -f 1 -d':')\033[00m:$$(echo $$l | cut -f 2- -d'#')\n"; done

##@ Build commands
.PHONY: build
build: # build image
	docker build -t my_essentia_with_jupyter .

.PHONY: notebook
notebook: # serve notebook in localhost:8888
	docker run --rm -it -p 8888:8888 -v ${PWD}/data:/data -v ${PWD}/pianodeafcraft:/src my_essentia_with_jupyter
