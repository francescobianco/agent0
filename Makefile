AGENT=/tmp/agent0.sh
SPACE=$(AGENT).d
PID=$(SPACE)/pid
IN=$(SPACE)/in
OUT=$(SPACE)/out
TEST_AGENT=/tmp/agent0-test.sh
TEST_SPACE=$(TEST_AGENT).d
TEST_PID=$(TEST_SPACE)/pid
TEST_IN=$(TEST_SPACE)/in
TEST_OUT=$(TEST_SPACE)/out
TEST_OUTPUT=tests/output

.PHONY: start connect status stop check test clean

start:
	@cp agent0.sh $(AGENT)
	@chmod +x $(AGENT)
	@if test -f $(PID); then kill `cat $(PID)` 2>/dev/null || true; fi
	@rm -fr $(SPACE)
	@$(AGENT) >/tmp/agent0.boot 2>&1 & echo $$! > /tmp/agent0.pid
	@printf '%s\n' "agent0 started: `cat /tmp/agent0.pid`"
	@i=0; while test $$i -lt 20; do test -p $(IN) && break; i=`expr $$i + 1`; sleep 1; done
	@printf '%s\n' 'connecting...'
	@$(MAKE) connect

connect:
	@test -p $(IN) || { printf '%s\n' 'agent0 not running; run make start'; exit 1; }
	@./client0.sh

status:
	@if test -f $(PID) && kill -0 `cat $(PID)` 2>/dev/null; then \
		printf '%s\n' "agent0 running: `cat $(PID)`"; \
	else \
		printf '%s\n' 'agent0 stopped'; \
	fi

stop:
	@if test -f $(PID); then kill `cat $(PID)` 2>/dev/null || true; fi

check:
	@sh -n agent0.sh

test:
	@sh -n agent0.sh
	@test -f .env || { printf '%s\n' 'missing .env with OPENCODE_API_KEY=... or OPENAI_API_KEY=...'; exit 1; }
	@key=`sed -n 's/^OPENCODE_API_KEY=//p; s/^OPENAI_API_KEY=//p' .env | sed -n '1p'`; \
	test -n "$$key" || { printf '%s\n' 'missing OPENCODE_API_KEY or OPENAI_API_KEY in .env'; exit 1; }; \
	if test -f $(TEST_PID); then kill `cat $(TEST_PID)` 2>/dev/null || true; fi; \
	rm -fr $(TEST_SPACE) $(TEST_OUTPUT); \
	mkdir -p $(TEST_OUTPUT); \
	cp agent0.sh $(TEST_AGENT); \
	chmod +x $(TEST_AGENT); \
	$(TEST_AGENT) >/tmp/agent0-test.boot 2>&1 & echo $$! > /tmp/agent0-test.pid; \
	i=0; while test $$i -lt 20; do test -p $(TEST_IN) && break; i=`expr $$i + 1`; sleep 1; done; \
	test -p $(TEST_IN) || { printf '%s\n' 'test agent did not create input fifo'; exit 1; }; \
	cat $(TEST_OUT) > $(TEST_OUTPUT)/test.log & echo $$! > $(TEST_SPACE)/reader.pid; \
	i=0; while test $$i -lt 20; do grep -q 'opencode key' $(TEST_OUTPUT)/test.log 2>/dev/null && break; i=`expr $$i + 1`; sleep 1; done; \
	printf '%s\n' "$$key" > $(TEST_IN); \
	i=0; while test $$i -lt 20; do grep -q 'agent0 alive' $(TEST_OUTPUT)/test.log 2>/dev/null && break; i=`expr $$i + 1`; sleep 1; done; \
	for prompt in tests/prompts/*.txt; do \
		test -f "$$prompt" || continue; \
		name=`basename "$$prompt" .txt`; \
		before=`wc -l < $(TEST_OUTPUT)/test.log 2>/dev/null || printf 0`; \
		cat "$$prompt" > $(TEST_IN); \
		printf '\n' > $(TEST_IN); \
		i=0; while test $$i -lt 180; do \
			after=`wc -l < $(TEST_OUTPUT)/test.log 2>/dev/null || printf 0`; \
			test "$$after" -gt "$$before" && break; \
			i=`expr $$i + 1`; sleep 1; \
		done; \
		cp $(TEST_OUTPUT)/test.log "$(TEST_OUTPUT)/$$name.out"; \
		if grep -q 'OpenCode Go request failed\|curl:' "$(TEST_OUTPUT)/$$name.out"; then \
			printf '%s\n' "test failed on $$prompt"; \
			break; \
		fi; \
	done; \
	if test -f $(TEST_SPACE)/reader.pid; then kill `cat $(TEST_SPACE)/reader.pid` 2>/dev/null || true; fi; \
	if test -f $(TEST_PID); then kill `cat $(TEST_PID)` 2>/dev/null || true; fi

clean:
	@rm -f $(AGENT)
	@rm -fr $(AGENT).d
	@rm -f $(TEST_AGENT)
	@rm -fr $(TEST_AGENT).d

push:
	@git add .
	@git commit -am "update" || true
	@git push