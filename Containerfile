#
# Build: podman build -t nytxw .
#
# Run: podman run --rm -v $HOME/.mozilla:/root/.mozilla:Z,ro \
#                 -v $HOME/path/to/nyt:/xw:Z \
#                  nytxw Firefox \
#                        $(date +'https://www.nytimes.com/crosswords/game/daily/%Y/%m/%d') \
#                        /xw/$(date --iso-8601=date).puz
#
FROM docker.io/library/alpine:latest
WORKDIR /nytxw_puz
ADD *.py *.txt /nytxw_puz
RUN apk update && \
    apk add python3 py3-pip py3-wheel python3-dev gcc musl-dev libffi-dev zlib-dev rust cargo openssl-dev && \
    python3 -m pip install -r requirements.txt && \
    apk del py3-wheel python3-dev gcc musl-dev libffi-dev zlib-dev rust cargo openssl-dev && \
    rm -rf /root/.cargo
ENTRYPOINT ["/nytxw_puz/nyt.py"]
