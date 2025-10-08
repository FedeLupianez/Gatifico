run:
	@uv run src/main.py

build:
	@pyinstaller compile.spec

clean:
	@rm -rf build/ dist/
