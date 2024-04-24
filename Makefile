.PHONY: build
build:
	python3 -m pip wheel --no-deps .

.PHONY: check
check:
	python3 -m mypy voucherer/

.PHONY: clean
clean:
	rm -rf \
		build/ \
		mikrotik_voucherer.egg-info/ \
		mikrotik_voucherer-*.whl
