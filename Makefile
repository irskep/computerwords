.PHONY: test

test:
	python3 -m unittest discover tests

watchtest:
	watch -n 0.2 make test
