# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line.
SPHINXOPTS    =
SPHINXBUILD   = sphinx-build
SPHINXPROJ    = kano-toolset
SOURCEDIR     = source
BUILDDIR      = build


.PHONY: all clean help Makefile

# Put it first so that "make" without argument is like "make help".
help:
	$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

all:
	# Generate the reST files from which the documentation will be built.
	sphinx-apidoc -o source/ ../
	$(MAKE) html

# Override the clean target to get rid of all generated .rst files.
clean:
	-find source -name "*.rst" -type f \
		-not -name "index.rst" -not -name "modules.rst" -not -name "readme.rst" \
		-delete
	-$(SPHINXBUILD) -M clean "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
