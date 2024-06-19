APP=nodeodmcli
BUILD_FILES=__main__.py
BUILD_DIR=build

app: $(BUILD_FILES)
	rm -f $(APP)
	cp -p $(BUILD_FILES) build
	python3 -m zipapp -p "/usr/bin/env python3" -o $(APP) $(BUILD_DIR)

requirements: requirements.txt
	python3 -m pip install -r requirements.txt --target $(BUILD_DIR)