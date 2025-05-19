# stage 1: Build stage
FROM ubuntu:20.04 AS builder

ENV LANG=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    TZ=Europe/Moscow \
    DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1

RUN ln -fs /usr/share/zoneinfo/Etc/UTC /etc/localtime \
    && apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    python3 \
    python3-pip \
    && apt-get clean && rm -rf /tmp/* /var/tmp/*

RUN pip3 install --no-cache-dir \
    numpy \
    matplotlib \
    && rm -rf /tmp/* /var/tmp/*

WORKDIR /build

COPY src/ /build/src/

RUN cmake -S src -B build -DCMAKE_INSTALL_PREFIX=/app \
    && cmake --build build --target install


# stage 2: Final minimal image
FROM ubuntu:20.04

ENV TZ=Europe/Moscow \
    DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3-minimal \
    python3-tk \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# RUN pip3 install --no-cache-dir \
#     numpy \
#     matplotlib \
#     && rm -rf /tmp/* /var/tmp/*

WORKDIR /app

COPY --from=builder /app /app

# copy Python site-packages from builder
COPY --from=builder /usr/lib/python3/dist-packages /usr/lib/python3/dist-packages
COPY --from=builder /usr/local/lib/python3.8/dist-packages /usr/local/lib/python3.8/dist-packages

# wrap entrypoint
COPY ./entrypoint.sh /app/entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]
