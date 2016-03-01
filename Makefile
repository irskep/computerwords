.PHONY: test watchtest demo docs docsdebug deploy-docs

test:
	python3 -m unittest discover tests --failfast

watchtest:
	watch -n 0.2 make test

demo:
	python3 -m computerwords --conf demo/conf.json

docs:
	python3 -m computerwords --conf docs/conf.json

docsdebug:
	python3 -m computerwords --conf docs/conf.json --debug

deploy-docs: docs
	ghp-import -np docs/build
