.PHONY: test watchtest demo docs docsdebug deploy-docs

test:
	python3 -m unittest discover tests --failfast

watchtest:
	watch -n 0.2 make test

demo:
	python3 -m computerwords --conf demo/conf.json

docs:
	# rm -rf docs/build/static/*
	# rm -f docs/build/*.html docs/build/*.png docs/build/*.css
	python3 -m computerwords.source_parsers.python35 . computerwords > docs/build/symbols.json
	python3 -m computerwords --conf docs/conf.json

watchdocs:
	./watchdocs.py

debugdocs:
	watch -n 0.2 make docs

docsdebug:
	python3 -m computerwords --conf docs/conf.json --debug

deploy-docs: docs
	ghp-import -np docs/build
