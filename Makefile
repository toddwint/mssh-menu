# This is a Makefile

include env
export script
export module

#module != basename "$${PWD}"
#script := $(subst _,-,${module})

version := $(shell python3 -c "import mssh_menu; print(mssh_menu.__version__)")
release_files := $(wildcard releases/${module}-${version}*.whl) \
        $(wildcard releases/${module}-${version}*.tar.gz) \
        $(wildcard releases/${script}*.pyz)
project_modules := $(wildcard ./*.py)

.PHONY: all
all: check_requirements shell_completions docs build zipapp clean done

.PHONY: echo_all
echo_all:
	@echo "script: $(script)"
	@echo "module: $(module)"
	@echo "version: $(version)"
	@echo "release_files: $(release_files)"
	@echo "project_modules: $(project_modules)"

.PHONY: check_requirements
check_requirements:
	@pip show --quiet build
	@type pipx

.ONESHELL:
.PHONY: shell_completions
shell_completions:
	cd ./shell-completions
	make

.ONESHELL:
.PHONY: docs
docs:
	cd ./docs
	make
	make copy

.PHONY: source
source: $(project_modules)
	-@mkdir --parents --verbose src/${module}
	@cp --verbose ${project_modules} src/${module}
	@cp --parents --verbose $(wildcard shell-completions/*/${script}) src/${module}

.PHONY: build
build: source
	python -m build . --outdir releases

.PHONY: zipapp
zipapp: source
	-@mkdir --parents --verbose releases
	python -m zipapp \
		src \
		--main ${module}.${module}:main \
		--python '/usr/bin/env python3' \
		--compress \
		--output releases/${script}.pyz

.PHONY: clean
clean:
	-@rm -rf --verbose __pycache__

.PHONY: archive-release
archive-release: $(release_files)
	-@mkdir --verbose bkup/releases/${version}	
	@cp --verbose ${^} bkup/releases/${version}
	@cp --verbose releases/release_notes.txt bkup/releases/${version}

.PHONY: done
done: archive-release
	-@rm -rf --verbose src

.PHONY: remove
remove: clean done
	#-@rm -rf --verbose dist
	#-@rm -rf --verbose zipapp
	-@rm --force --verbose ${release_files}

.PHONY: install
install:
	pip install $(filter %.whl, $(release_files)) 

.PHONY: uninstall
uninstall:
	pip uninstall ${module}

.PHONY: pipx_install
pipx_install:
	pipx install $(filter %.whl, $(release_files)) 

.PHONY: git-release-push
git-release-push: $(release_files)
	gh release create \
		"${script}/${version}" \
		--latest \
		--notes-file releases/release_notes.txt \
		--generate-notes \
		--title "${script} ${version}" \
		${^}
