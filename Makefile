.PHONY: test

test:
	python3 -m unittest discover kissup

watchtest:
	watch -n 0.2 make test
