sdist: resources
	python3 setup.py sdist bdist_wheel

resources: gpmbootstrap/gpmbootstrap.gresource

gpmbootstrap/gpmbootstrap.gresource: gpmbootstrap/gpmbootstrap.gresource.xml ui/main.ui ui/style.css
	glib-compile-resources gpmbootstrap/gpmbootstrap.gresource.xml

clean:
	rm dist/*
	rm gpmbootstrap/gpmbootstrap.gresource

.PHONY: clean sdist resources
