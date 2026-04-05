.PHONY: setup run-channel run-web check

# --- Setup ---
# Create symlinks from .claude/ to top-level dirs, discover plugin skills,
# and create .autoservice/ runtime directories.
setup:
	@echo "==> Linking top-level dirs into .claude/"
	@mkdir -p .claude
	@for dir in skills commands agents hooks; do \
		rm -f .claude/$$dir; \
		ln -sfn ../$$dir .claude/$$dir; \
		echo "  .claude/$$dir -> ../$$dir"; \
	done
	@echo "==> Scanning plugins for skills..."
	@for skill_dir in plugins/*/skills/*/; do \
		[ -d "$$skill_dir" ] || continue; \
		name=$$(basename "$$skill_dir"); \
		rm -f skills/$$name; \
		ln -sfn ../$$skill_dir skills/$$name; \
		echo "  skills/$$name -> ../$$skill_dir"; \
	done
	@echo "==> Creating .autoservice/ runtime dirs"
	@mkdir -p .autoservice/logs .autoservice/data .autoservice/cache
	@echo "Done."

# --- Run ---
run-channel:
	uv run python3 feishu/channel.py

run-web:
	uv run uvicorn web.app:app --host 0.0.0.0 --port $${DEMO_PORT:-8000}

# --- Check ---
# Verify plugin discovery by listing discovered skill symlinks.
check:
	@echo "==> Checking plugin discovery"
	@found=0; \
	for link in skills/*/; do \
		[ -L "$${link%/}" ] && { echo "  plugin skill: $${link%/}"; found=$$((found+1)); }; \
	done; \
	echo "Found $$found plugin skill(s)."
