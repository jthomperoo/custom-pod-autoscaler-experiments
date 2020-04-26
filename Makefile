default:
	pandoc dissertation.md                  \
	  --pdf-engine=xelatex                  \
	  -o dissertation.pdf                   \
	  -V geometry:margin=1in                \
	  --table-of-contents                   \
	  --template template/eisvogel.tex      \
	  --filter pandoc-citeproc              \
	  --listings                            \
	  --include-before-body=preamble.tex    \
	  --include-after-body=postamble.tex