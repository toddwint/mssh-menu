# This is a Makefile

make_dir := .
project_dir := ..
PYTHONPATH := ..
export PYTHONPATH

include ${project_dir}/env
export script
export module
project_modules := $(wildcard ${project_dir}/*.py)

md_dir := ./markdown
output_dir := ./output
man_output_dir := ./man

install_chapters := $(wildcard install/*.md)
install_md := ${md_dir}/INSTALL.md

readme_chapters := $(wildcard readme/*.md)
readme_md := ${md_dir}/README.md

man_files := ${man_output_dir}/${script}.1 ${man_output_dir}/${script}.1.gz
manual_md := ${md_dir}/MANUAL.md

md_files := $(sort \
            $(wildcard ${md_dir}/*.md) \
			$(install_md) $(readme_md) $(manual_md) \
            )

html_files := $(patsubst ${md_dir}/%.md,${output_dir}/%.html,${md_files})
docx_files := $(patsubst ${md_dir}/%.md,${output_dir}/%.docx,${md_files})
epub_files := $(patsubst ${md_dir}/%.md,${output_dir}/%.epub,${md_files})
pdf_files := $(patsubst ${md_dir}/%.md,${output_dir}/%.pdf,${md_files})
tex_files := $(patsubst ${md_dir}/%.md,${output_dir}/%.tex,${md_files})
rtf_files := $(patsubst ${md_dir}/%.md,${output_dir}/%.rtf,${md_files})
typ_files := $(patsubst ${md_dir}/%.md,${output_dir}/%.typ,${md_files})

output_files := $(wildcard ${output_dir}/*)
project_output_files := $(subst ${output_dir},${project_dir},${output_files})

ext = $(subst .,,$(suffix $(1)))

.PHONY: all
all: prebuild man html pdf
	
.PHONY: test
test: $(md_files)
	@$(foreach f,${^},echo "prerequisite: $(f), target: $@";)

.PHONY: echo_all
echo_all:
	@echo "make_dir: $(make_dir)"
	@echo "project_dir: $(project_dir)"
	@echo "PYTHONPATH: $(PYTHONPATH)"
	@echo "script: $(script)"
	@echo "module: $(module)"
	@echo "project_modules: $(project_modules)"
	@echo "md_dir: $(md_dir)"
	@echo "output_dir: $(output_dir)"
	@echo "man_output_dir: $(man_output_dir)"
	@echo "install_chapters: $(install_chapters)"
	@echo "install_md: $(install_md)"
	@echo "readme_chapters: $(readme_chapters)"
	@echo "readme_md: $(readme_md)"
	@echo "man_files: $(man_files)"
	@echo "md_files: $(md_files)"
	@echo "html_files: $(html_files)"
	@echo "docx_files: $(docx_files)"
	@echo "epub_files: $(epub_files)"
	@echo "pdf_files: $(pdf_files)"
	@echo "tex_files: $(tex_files)"
	@echo "rtf_files: $(rtf_files)"
	@echo "typ_files: $(typ_files)"
	@echo "output_files: $(output_files)"
	@echo "project_output_files: $(project_output_files)"

.PHONY: prebuild
prebuild: check_requirements install_md readme_md manual_md

.PHONY: check_requirements
check_requirements:
	@type pandoc
	@type ./build_man_page.py

define merge-markdown
-@rm --verbose --force ${@}
sed -Ei 's/^(date: ).*/\1'$$(date -Id)'/' ${<}
sed --separate '$$s/$$/\n\n/' ${^} > ${@}.tmp
envsubst '$$script $$module' < ${@}.tmp > ${@}
-@rm --force --verbose ${@}.tmp
endef

define run-pandoc
pandoc --data-dir "${make_dir}" --defaults "$(call ext,${@})" "${^}" -o "${@}"
endef

$(install_md): $(install_chapters)
	$(merge-markdown)

$(readme_md): $(readme_chapters)
	$(merge-markdown)

.PHONY: markdown
markdown: install_md readme_md man

.PHONY: install_md
install_md: $(install_md)

.PHONY: readme_md
readme_md: $(readme_md)

.PHONY: man
man: $(man_files)

$(manual_md): $(man_files)

.PHONY: manual_md
manual_md: $(manual_md)

$(man_files): $(project_modules)
	-@mkdir -p --verbose "${man_output_dir}"
	./build_man_page.py \
		--output "${md_dir}"/MANUAL.md \
		--template "${man_output_dir}"/template.md \
		--append "${man_output_dir}"/examples.md \
		${module}:parse_arguments
	pandoc --defaults defaults -t man "${md_dir}"/MANUAL.md -o "${man_output_dir}/${script}.1"
	-@gzip --verbose --force --best --no-name --keep "${man_output_dir}/${script}.1"

.PHONY: html
html: $(html_files)

$(html_files) : ${output_dir}/%.html : ${md_dir}/%.md
	$(run-pandoc)

.PHONY: pdf
pdf: $(pdf_files)

$(pdf_files) : ${output_dir}/%.pdf : ${md_dir}/%.md
	$(run-pandoc)

.PHONY: tex
tex: $(tex_files)

$(tex_files) : ${output_dir}/%.tex : ${md_dir}/%.md
	$(run-pandoc)

.PHONY: docx
docx: $(docx_files)

$(docx_files) : ${output_dir}/%.docx : ${md_dir}/%.md
	$(run-pandoc)

.PHONY: rtf
rtf: $(rtf_files)

$(rtf_files) : ${output_dir}/%.rtf : ${md_dir}/%.md
	$(run-pandoc)

.PHONY: epub
epub: $(epub_files)

$(epub_files) : ${output_dir}/%.epub : ${md_dir}/%.md
	$(run-pandoc)

.PHONY: typ
typ: $(typ_files)

$(typ_files) : ${output_dir}/%.typ : ${md_dir}/%.md
	$(run-pandoc)

.PHONY: clean
clean:
	-@rm --verbose "${output_dir}/"*
	-@rm --verbose ${man_files}

.PHONY: copy
copy:
	-@cp --verbose "${output_dir}"/* "${project_dir}"
	-@mkdir -p --verbose "${project_dir}/man"
	-@cp --verbose ${man_files} "${project_dir}"/man/
	-@cp --verbose ${md_files} "${project_dir}"
	sed -Ei 's#(figures/)#docs/\1#' "${project_dir}/README.md"

.PHONY: clean_all
clean_all: clean
	-@rm --verbose tex2pdf*/input.log
	-@rm --verbose texput.log
	-@rmdir --verbose tex2pdf*/
