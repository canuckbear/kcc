#
# The contents of this file are subject to the Apache 2.0 license you may not
# use this file except in compliance with the License.
#
# Software distributed under the License is distributed on an "AS IS" basis,
# WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License
# for the specific language governing rights and limitations under the
# License.
#
# Copyright 2023 kcc project (http://www.firmwaretoolkit.org).
# All rights reserved. Use is subject to license terms.
#
#
# Contributors list :
#
#    William Bonnet     wllmbnnt@gmail.com, wbonnet@theitmakers.com
#

# Retrieve cueeznt package version
SW_VERSION := $(shell grep kcc debian/changelog | tr \( \  | tr \) \  | tr \- \  | awk '{ print $$2 }' | sort -r | head -n 1 )
PKG_DIR    := ..

# ------------------------------------------------------------------------------
#
# Run git status
#
status:
	@echo "running git status in status"
	@echo
	@git status

# ------------------------------------------------------------------------------
#
# Target that prints the generic top level help
#
help:
	@echo "Available targets are :"
	@echo " requirements            Install all requirements using PIP"
	@echo " package                 Build the Debian package kcc.deb"
	@echo " test(s)                 Run unit tests"
	@echo " help                    Display this help"


#
# Target : init
#
# Description :
#
#	Install all requirements using PIP
#
requirements:
	pip3 install -r requirements.txt

#
# Target : test, tests
#
# Description :
#
#	Run unit tests
#
tests: test

test:
	nosetests



#
# Target : package
#
# Description : Build the <<debian package
#
#	Run unit tests
#

package:
	rm -f ../kcc_*.orig.tar.gz
	tar cvfz ../kcc_$(SW_VERSION).orig.tar.gz --exclude=kcc/__pycache__ --exclude=build --exclude=kcc.egg-info --exclude=./.git --exclude-vcs-ignores --exclude-vcs-ignores *
	debuild -us -uc -b


#
# Target : upload
#
# Description : upload th package to a debian repository
#
#

upload:
	if [ "x" = "x$(kcc_DEB_UPLOAD_SERVER)" ] ; then \
		echo "        Variable kcc_DEB_UPLOAD_SERVER is not set, please define it your shell environment." ; \
	fi ;
	if [ "x" = "x$(kcc_DEB_UPLOAD_PATH)" ] ; then \
		echo "        Variable kcc_DEB_UPLOAD_PATH is not set, please define it your shell environment." ; \
	fi ;
	if [ "x" = "x$(kcc_DEB_UPLOAD_USER)" ] ; then \
		echo "        Variable kcc_DEB_UPLOAD_USER is not set, please define it your shell environment." ; \
	fi ;
	scp $(PKG_DIR)/*.deb $(PKG_DIR)/*.buildinfo $(PKG_DIR)/*.orig.tar.gz $(PKG_DIR)/*.changes $(kcc_DEB_UPLOAD_USER)@$(kcc_DEB_UPLOAD_SERVER):$(kcc_DEB_UPLOAD_PATH) ;

