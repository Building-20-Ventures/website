.DEFAULT_GOAL := build
ZOLA ?= zola
PYTHON ?= python3
UV_CACHE_DIR ?= .tmp/uv-cache
BASE_URL ?= https://building20.vc
OUTPUT_DIR ?= public
PORT ?= 1111
PRODUCTION_SOURCE ?= .
STAGING_SOURCE ?= .

.PHONY: assets logo-assets building-assets build staging check test preview serve clean assemble verify-artifact
assets:
	mkdir -p static/art
	cp art/B20V-logo.png art/B20V-grid.png art/Serendipity_turning-points-serendipity.webp art/Building-20-transparent.png static/art/

# Optional authoring step; deployment consumes the checked-in PNGs.
logo-assets:
	UV_CACHE_DIR="$(UV_CACHE_DIR)" uv run --no-project --with pillow==12.3.0 python scripts/extract_logo.py

building-assets:
	UV_CACHE_DIR="$(UV_CACHE_DIR)" uv run --no-project --with pillow==12.3.0 python scripts/extract_building.py

build: assets
	$(ZOLA) build --base-url "$(BASE_URL)" --output-dir "$(OUTPUT_DIR)" --force

staging:
	$(MAKE) build BASE_URL=https://building20.vc/staging OUTPUT_DIR=.tmp/staging

check: assets
	$(ZOLA) check --skip-external-links
	$(MAKE) build OUTPUT_DIR=.tmp/production
	$(MAKE) staging
	$(PYTHON) scripts/check_site.py .tmp/production https://building20.vc
	$(PYTHON) scripts/check_site.py .tmp/staging https://building20.vc/staging

test: check
	$(PYTHON) -m unittest discover -s tests

# Both source directories are independent branch checkouts in GitHub Actions.
assemble: OUTPUT_DIR = .tmp/pages
assemble:
	$(MAKE) -C "$(PRODUCTION_SOURCE)" build BASE_URL=https://building20.vc OUTPUT_DIR=public
	$(MAKE) -C "$(STAGING_SOURCE)" build BASE_URL=https://building20.vc/staging OUTPUT_DIR=.tmp/staging
	$(PYTHON) scripts/assemble.py "$(PRODUCTION_SOURCE)/public" "$(STAGING_SOURCE)/.tmp/staging" "$(OUTPUT_DIR)"

verify-artifact: OUTPUT_DIR = .tmp/pages
verify-artifact:
	$(PYTHON) scripts/check_site.py "$(OUTPUT_DIR)" https://building20.vc
	$(PYTHON) scripts/check_site.py "$(OUTPUT_DIR)/staging" https://building20.vc/staging

preview:
	$(MAKE) build BASE_URL=http://127.0.0.1:1111 OUTPUT_DIR=.tmp/preview
	$(MAKE) build BASE_URL=http://127.0.0.1:1111/staging OUTPUT_DIR=.tmp/preview/staging
	$(PYTHON) -m http.server 1111 --bind 127.0.0.1 --directory .tmp/preview

serve: assets
	$(ZOLA) serve --interface 127.0.0.1 --port $(PORT)

clean:
	rm -rf public .tmp/production .tmp/staging .tmp/preview static/art
