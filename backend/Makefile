CHECK_DIRS := app


clean-logs: ## Clean logs
	rm -rf logs/**

format: ## Run pre-commit hooks
	black $(CHECK_DIRS)
	ruff format $(CHECK_DIRS)
	pre-commit run -a
