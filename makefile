prefix		= /opt
PKG_CONFIG	= PKG_CONFIG_PATH="$$PKG_CONFIG_PATH:${prefix}/lib/pkgconfig/" pkg-config
PKG_PACKAGES	= # rapicorn1307
CXXFLAGS	= $(shell ${PKG_CONFIG} --cflags ${PKG_PACKAGES})
CXXLIBS		= $(shell ${PKG_CONFIG} --libs   ${PKG_PACKAGES}) -Wl,-rpath=${prefix}/lib
OPTIMIZTE	= -pipe -std=gnu++0x -O6 -Wall -Werror=format-security -Wdeprecated -Wno-cast-qual \
		  -rdynamic -g -fno-omit-frame-pointer \
		  -mcx16 -funroll-loops -ftracer -finline-functions -fno-keep-static-consts -ftree-vectorize
GXX 		= colorg++-4.7 ${OPTIMIZTE} ${CXXFLAGS}
top_srcdir      = .
VERSION		= 13.11.3
BUILDID		= $(shell test -x $(top_srcdir)/.git/ && ( \
		    git log -n1 --pretty=format:Git-%h --abbrev=11 ; \
		    C=`git diff HEAD --raw | wc -l ` ; test "$$C" -lt 1 || echo "+$$C" ) \
		    || sed -n "1,1{s/.*\# */ChangeLog-/g;p}" <$(top_srcdir)/ChangeLog )
TARGETS		=

all: all-targets

buildid:
	@echo $(BUILDID)

PYPICONFIG = "package_version" : "${VERSION}", "package_buildid" : "${BUILDID}"

tobin: main.py
	sed < $< > xgen-$(@F) -e '1,24s|^ *#@PACKAGE_INSTALL_CONFIGURATION_PAGE1@|	${PYPICONFIG}|'
	$(Q) chmod +x xgen-$(@F)
	$(Q) cp -p xgen-$(@F) $@
	$(Q) rm -f xgen-$(@F)

dummy.o: *.hh *.cc
	$(GXX) -c dummy.cc ${CXXLIBS} -o $@
dummy: dummy.o
	$(GXX) $< ${CXXLIBS} -o $@

TARGETS += tobin

clean:
	rm -f *.o *.lo *.pyc ${TARGETS}
.PHONY: clean

all-targets: ${TARGETS}
.PHONY: all-targets
