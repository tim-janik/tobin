prefix		= /opt
PKG_CONFIG	= PKG_CONFIG_PATH="$$PKG_CONFIG_PATH:${prefix}/lib/pkgconfig/" pkg-config
PKG_PACKAGES	= # rapicorn1307
CXXFLAGS	= $(shell ${PKG_CONFIG} --cflags ${PKG_PACKAGES})
CXXLIBS		= $(shell ${PKG_CONFIG} --libs   ${PKG_PACKAGES}) -Wl,-rpath=${prefix}/lib
OPTIMIZTE	= -pipe -std=gnu++0x -O6 -Wall -Werror=format-security -Wdeprecated -Wno-cast-qual \
		  -rdynamic -g -fno-omit-frame-pointer \
		  -mcx16 -funroll-loops -ftracer -finline-functions -fno-keep-static-consts -ftree-vectorize
GXX 		= colorg++-4.7 ${OPTIMIZTE} ${CXXFLAGS}
TARGETS		=

all: all-targets

dummy.o: *.hh *.cc
	$(GXX) -c dummy.cc ${CXXLIBS} -o $@
dummy: dummy.o
	$(GXX) $< ${CXXLIBS} -o $@

TARGETS += dummy

clean:
	rm -f *.o *.lo ${TARGETS}
.PHONY: clean

all-targets: ${TARGETS}
.PHONY: all-targets
