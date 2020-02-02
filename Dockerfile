FROM python:3.6-alpine

# Get latest root certificates
RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.ustc.edu.cn/g' /etc/apk/repositories && \
    apk add --no-cache ca-certificates && update-ca-certificates && \
    pip install --no-cache-dir redis flower celery[redis]

# PYTHONUNBUFFERED: Force stdin, stdout and stderr to be totally unbuffered. (equivalent to `python -u`)
# PYTHONHASHSEED: Enable hash randomization (equivalent to `python -R`)
# PYTHONDONTWRITEBYTECODE: Do not write byte files to disk, since we maintain it as readonly. (equivalent to `python -B`)
ENV PYTHONUNBUFFERED=1 PYTHONHASHSEED=random PYTHONDONTWRITEBYTECODE=1

# Default port
EXPOSE 5555

# Run as a non-root user by default, run as user with least privileges.
# USER nobody

VOLUME ["/app/"]

WORKDIR /app

ENV C_FORCE_ROOT=true

