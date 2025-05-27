# This is a Makefile

projectdir := ..
makedir := .

include ${projectdir}/env
#module != basename "$${PWD}"
#script := $(subst _,-,${module})

src := $(addprefix ../,$(addsuffix .py, $(module)))
dst := $(addsuffix .py, $(module))

PYTHONPATH := ..
export PYTHONPATH

.PHONY: all
all: check_requirements clean completions fix_completions
	
.PHONY: echo_all
echo_all:
	@echo "projectdir: $(projectdir)"
	@echo "makedir: $(makedir)"
	@echo "script: $(script)"
	@echo "module: $(module)"
	@echo "src: $(src)"
	@echo "dst: $(dst)"
	@echo "PYTHONPATH: $(PYTHONPATH)"

.PHONY: check_requirements
check_requirements:
	@type shtab
	@type pycomplete
	@pip show --quiet shtab
	@pip show --quiet pycomplete
	@type ./generate_completion.py 

.PHONY: clean
clean:
	-@rm -rf --verbose ${dst}
	-@rm -rf --verbose "__pycache__"
	-@rm -rf --verbose bash
	-@rm -rf --verbose zsh
	-@rm -rf --verbose tcsh
	-@rm -rf --verbose fish
	-@rm -rf --verbose powershell

.PHONY: copy
copy:
	@cp --verbose ${src} ${dst}

.PHONY: completions
completions: shtab_bash shtab_zsh fish_completion

.PHONY: fix_completions
fix_completions: fix_shtab_bash fix_shtab_zsh

.PHONY: bash_completion
bash_completion:
	echo "Not implemented"

.PHONY: zsh_completion
zsh_completion:
	echo "Not implemented"

.PHONY: fish_completion
fish_completion:
	@echo "-Running completion for fish..."
	./generate_completion.py \
        --shell fish \
        --alias "${module}.py" \
        --alias "${script}.pyz" \
		--output "fish/${script}" \
		${module}:parse_arguments

.PHONY: shtab_bash
shtab_bash:
	@echo "-Running shtab bash command..."
	@mkdir -p "bash"
	shtab \
		--error-unimportable \
		--verbose \
		--shell=bash \
		--prog ${script} \
		${module}.parse_arguments \
		| tee "bash/${script}"
	-@rm -rf --verbose "__pycache__"

.PHONY: shtab_zsh
shtab_zsh:
	@echo "-Running shtab zsh command..."
	@mkdir -p "zsh"
	shtab \
		--error-unimportable \
		--verbose \
		--shell=zsh \
		--prog ${script} \
		${module}.parse_arguments \
		| tee "zsh/${script}"
	-@rm -rf --verbose "__pycache__"

.PHONY: shtab_tcsh
shtab_tcsh:
	@echo "-Running shtab tcsh command..."
	@mkdir -p "tcsh"
	shtab \
		--error-unimportable \
		--verbose \
		--shell=tcsh \
		--prog ${script} \
		${module}.parse_arguments \
		| tee "tcsh/${script}"
	-@rm -rf --verbose "__pycache__"

.PHONY: pycomplete_bash
pycomplete_bash:
	@echo "-Running pycomplete bash command..."
	@mkdir -p "bash"
	pycomplete \
		"${module}:parse_arguments()" \
		bash \
		--prog ${script} \
		| tee "bash/${script}"
	-@rm -rf --verbose "__pycache__"

.PHONY: pycomplete_zsh
pycomplete_zsh:
	@echo "-Running pycomplete zsh command..."
	@mkdir -p "zsh"
	pycomplete \
		"${module}:parse_arguments()" \
		zsh \
		--prog ${script} \
		| tee "zsh/${script}"
	-@rm -rf --verbose "__pycache__"

.PHONY: pycomplete_fish
pycomplete_fish:
	@echo "-Running pycomplete fish command..."
	@mkdir -p "fish"
	pycomplete \
		"${module}:parse_arguments()" \
		fish \
		--prog ${script} \
		| tee "fish/${script}"
	-@rm -rf --verbose "__pycache__"

.PHONY: pycomplete_powershell
pycomplete_powershell:
	@echo "-Running pycomplete powershell command..."
	@mkdir -p "powershell"
	pycomplete \
		"${module}:parse_arguments()" \
		powershell \
		--prog ${script} \
		| tee "powershell/${script}"
	-@rm -rf --verbose "__pycache__"

.PHONY: fix_shtab_bash
fix_shtab_bash: 
	@echo "-Making backup of shtab bash output..."
	-@cp --verbose "bash/${script}" "bash/${script}.bak"
	@echo "-Applying fix to shtab bash output..."
	sed -i '$$ s/-o filenames/-o default/' "bash/${script}"
	sed -i '$$ s/$$/ ${module}.py/' "bash/${script}"
	sed -i '$$ s/$$/ ${script}.pyz/' "bash/${script}"
	sed -i 's/=?/=0/' "bash/${script}"
	@echo "-Done!"

.PHONY: fix_shtab_zsh
fix_shtab_zsh:
	@echo "-Making backup of shtab zsh output..."
	-@cp --verbose "zsh/${script}" "zsh/${script}.bak"
	@echo "-Applying fix to shtab zsh output..."
	sed -i '/#compdef/ s/$$/ ${module}.py/' "zsh/${script}"
	sed -i '/#compdef/ s/$$/ ${script}.pyz/' "zsh/${script}"
	#sed -i '/_arguments/i\  _alternative _files' "zsh/${script}"
	@echo "-Done!"

.PHONY: fix_shtab_tcsh
fix_shtab_tcsh:
	@echo "-Making backup of shtab tcsh output..."
	-@cp --verbose "tcsh/${script}" "tcsh/${script}.bak"
	@echo "-Applying fix to shtab tcsh output..."
	#sed -Ei 's/(${script})/\1*/' "tcsh/${script}"
	@echo "-Done!"

.PHONY: fix_pycomplete_bash
fix_pycomplete_bash: 
	@echo "-Making backup of pycomplete bash output..."
	-@cp --verbose "bash/${script}" "bash/${script}.bak"
	@echo "-Applying fix to pycomplete bash output..."
	sed -i '/complete -o default/ s/$$/ ${module}.py/' "bash/${script}"
	sed -i '/complete -o default/ s/$$/ ${script}.pyz/' "bash/${script}"
	@echo "-Done!"

.PHONY: fix_pycomplete_zsh
fix_pycomplete_zsh: 
	@echo "-Making backup of pycomplete zsh output..."
	-@cp --verbose "bash/${script}" "bash/${script}.bak"
	@echo "-Applying fix to pycomplete zsh output..."
	sed -i '/#compdef/ s/$$/ ${module}.py ${script}.pyz/' "zsh/${script}"
	@echo "-Done!"

.PHONY: fix_pycomplete_fish
fix_pycomplete_fish:
	@echo "-Making backup of pycomplete fish output..."
	-@cp --verbose "fish/${script}" "fish/${script}.bak"
	@echo "-Applying fix to pycomplete fish output..."
	sed -Ei 's/(complete -c ${module})/\1 -c ${script}.py -c ${module}.pyz/' "fish/${script}"
	@echo "-Done!"

.PHONY: finish
finish:
	-@rm --verbose ${dst}
