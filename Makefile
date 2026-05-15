AGENT=/tmp/agent0.sh
SESSION=agent0

.PHONY: start connect status stop check clean

start:
	@cp agent0.sh $(AGENT)
	@chmod +x $(AGENT)
	@tmux has-session -t $(SESSION) 2>/dev/null && tmux kill-session -t $(SESSION) || true
	@tmux new-session -d -s $(SESSION) $(AGENT)
	@tmux display-message -p 'agent0 started in tmux session: $(SESSION)'

connect:
	@tmux attach-session -t $(SESSION)

status:
	@tmux has-session -t $(SESSION) 2>/dev/null && tmux list-sessions | sed -n '/^$(SESSION):/p' || printf '%s\n' 'agent0 stopped'

stop:
	@tmux has-session -t $(SESSION) 2>/dev/null && tmux kill-session -t $(SESSION) || true

check:
	@sh -n agent0.sh

clean:
	@rm -f $(AGENT)
	@rm -fr $(AGENT).d
