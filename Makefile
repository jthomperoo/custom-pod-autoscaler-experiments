default:
	pandoc dissertation.md --pdf-engine=xelatex -o dissertation.pdf -V geometry:margin=1in --table-of-contents