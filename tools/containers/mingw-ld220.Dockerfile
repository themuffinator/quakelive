# MinGW cross build environment with GNU binutils 2.20 to match the FFmpeg DLLs.

FROM debian:bookworm-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        ca-certificates \
        curl \
        g++-mingw-w64-i686 \
        git \
        make \
        pkg-config \
        python3 \
        python3-pip \
        xz-utils \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/src

# Build and install binutils 2.20 for i686-w64-mingw32. GCC from Debian is retained,
# but we force ld/as/ar to the legacy release captured in the shipped FFmpeg binaries.
RUN curl -L https://ftp.gnu.org/gnu/binutils/binutils-2.20.tar.bz2 -o binutils-2.20.tar.bz2 \
    && tar -xf binutils-2.20.tar.bz2 \
    && mkdir binutils-build \
    && cd binutils-build \
    && ../binutils-2.20/configure --target=i686-w64-mingw32 --prefix=/opt/toolchain --disable-nls \
    && make -j"$(nproc)" \
    && make install \
    && cd /opt/src \
    && rm -rf binutils-2.20 binutils-build binutils-2.20.tar.bz2

ENV PATH="/opt/toolchain/bin:${PATH}"

# Provide a wrapper to ensure ld/as/ar from 2.20 are chosen during builds.
RUN printf '#!/bin/sh\nexec /opt/toolchain/bin/i686-w64-mingw32-ld "$@"\n' > /usr/local/bin/i686-w64-mingw32-ld-2.20 \
    && chmod +x /usr/local/bin/i686-w64-mingw32-ld-2.20

WORKDIR /workspace

CMD ["bash"]
