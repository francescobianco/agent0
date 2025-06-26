
push:
	@git add .
	@git commit -am "New release!" || true
	@git push

start:
	@chmod +x agent0.sh
	@docker compose up -d --force-recreate --build