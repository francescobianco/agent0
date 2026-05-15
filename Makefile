AGENT=/tmp/agent0.sh
SPACE=$(AGENT).d
PID=$(SPACE)/pid
IN=$(SPACE)/in
OUT=$(SPACE)/out

.PHONY: start connect status stop check clean

start:
	@cp agent0.sh $(AGENT)
	@chmod +x $(AGENT)
	@rm -fr $(SPACE)
	@mkdir -p $(SPACE)
	@: > $(IN)
	@: > $(OUT)
	@if test -f $(PID) && kill -0 `cat $(PID)` 2>/dev/null; then \
		printf '%s\n' "agent0 already running: `cat $(PID)`"; \
	else \
		nohup $(AGENT) > $(OUT) 2>&1 & echo $$! > $(PID); \
		printf '%s\n' "agent0 started: `cat $(PID)`"; \
		printf '%s\n' "connect with: make connect"; \
	fi

connect:
	@test -f $(IN) || { printf '%s\n' 'agent0 terminal not ready; run make start'; exit 1; }
	@touch $(OUT)
	@(tail -n +1 -f $(OUT) & echo $$! > $(SPACE)/tail.pid; \
	trap 'kill `cat $(SPACE)/tail.pid` 2>/dev/null || true' INT TERM EXIT; \
	while IFS= read -r line; do printf '%s\n' "$$line" >> $(IN); done)

status:
	@if test -f $(PID) && kill -0 `cat $(PID)` 2>/dev/null; then \
		printf '%s\n' "agent0 running: `cat $(PID)`"; \
	else \
		printf '%s\n' 'agent0 stopped'; \
	fi

stop:
	@if test -f $(PID); then kill `cat $(PID)` 2>/dev/null || true; fi
	@if test -f $(SPACE)/tail.pid; then kill `cat $(SPACE)/tail.pid` 2>/dev/null || true; fi
	@rm -f $(PID) $(SPACE)/tail.pid

check:
	@sh -n agent0.sh

clean:
	@rm -f $(AGENT)
	@rm -fr $(AGENT).d
