IMAGE ?= ptmnavigator_sqlite_backend


INTERACTIVE := $(shell [ -t 0 ] && echo 1)
ifdef INTERACTIVE
	USE_TTY= -t
else
	USE_TTY=
endif

DOCKER_CMD ?= docker run -i ${USE_TTY}

build:
	docker build -f Dockerfile -t $(IMAGE) . || (exit 1)

jump:
	$(DOCKER_CMD) --entrypoint /bin/bash \
		$(IMAGE)

serve:
	$(DOCKER_CMD) --network host $(IMAGE)
