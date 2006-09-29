NAME = danlann-manual

EXTRA_DIST = $(NAME).tex $(NAME)-@VERSION@.pdf

all: $(NAME)-@VERSION@.pdf

$(NAME)-@VERSION@.pdf: $(NAME).tex
	pdflatex -interaction batchmode $(NAME).tex
	pdflatex -interaction batchmode $(NAME).tex
	pdflatex -interaction batchmode $(NAME).tex
	cp $(NAME).pdf $(NAME)-@VERSION@.pdf

CLEANFILES = $(NAME).pdf $(NAME)-@VERSION@.pdf \
	$(NAME).toc $(NAME).aux $(NAME).out $(NAME).lst $(NAME).log
