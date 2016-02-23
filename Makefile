.PHONY: test watchtest demodocs

test:
	python3 -m unittest discover tests

watchtest:
	watch -n 0.2 make test

demodocs:
	python3 -m computerwords - < docs/demo.txt > docs/demo.html
