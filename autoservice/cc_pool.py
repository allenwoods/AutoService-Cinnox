"""
CC Pool — Claude Code SDK instance pool.

Pre-creates ClaudeSDKClient instances so they're warm and ready.
Checkout an instance, use it, return it.

Usage:
    from autoservice.cc_pool import get_pool, shutdown_pool

    pool = await get_pool()
    async with pool.acquire() as instance:
        await instance.client.query("hello")
        async for msg in instance.client.receive_response():
            print(msg)

    # Or use the convenience method:
    async for msg in pool.query("hello"):
        print(msg)
"""

import asyncio
import json
import logging
import os
import time
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, AsyncIterator

from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions
from claude_agent_sdk.types import Message

log = logging.getLogger("cc-pool")


def _setup_file_logging() -> None:
    """Configure cc-pool logger to write to .autoservice/logs/cc_pool.log."""
    log_dir = Path.cwd() / ".autoservice" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "cc_pool.log"

    # Avoid duplicate handlers on re-import
    if any(isinstance(h, logging.FileHandler) and h.baseFilename == str(log_file.resolve())
           for h in log.handlers):
        return

    file_handler = logging.FileHandler(str(log_file), mode="a", encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(
        "[cc-pool] %(asctime)s %(levelname)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    ))
    log.addHandler(file_handler)

    # Also add a stderr handler for INFO+
    if not any(isinstance(h, logging.StreamHandler) and not isinstance(h, logging.FileHandler)
               for h in log.handlers):
        stderr_handler = logging.StreamHandler()
        stderr_handler.setLevel(logging.INFO)
        stderr_handler.setFormatter(logging.Formatter("[cc-pool] %(levelname)s %(message)s"))
        log.addHandler(stderr_handler)

    log.setLevel(logging.DEBUG)


_setup_file_logging()


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

@dataclass
class PoolConfig:
    """Pool configuration, loadable from config.local.yaml or env vars.

    The pool uses the locally installed Claude CLI by default (found via PATH).
    Set cli_path to override with a specific binary location.
    """
    min_size: int = 1
    max_size: int = 4
    warmup_count: int = 1
    max_queries_per_instance: int = 50
    max_lifetime_seconds: float = 3600.0
    health_check_interval: float = 30.0
    checkout_timeout: float = 30.0
    cwd: str | None = None
    permission_mode: str = "bypassPermissions"
    model: str | None = None
    cli_path: str | None = None  # Path to local claude CLI (None = auto-detect)


def load_pool_config(cwd: str | None = None) -> PoolConfig:
    """Load pool config. Layered: config.yaml → config.local.yaml → env vars.

    Loading order (later overrides earlier):
      1. .autoservice/config.yaml        — shared defaults (committed to git)
      2. .autoservice/config.local.yaml   — local overrides (gitignored, secrets)
      3. CC_POOL_* environment variables  — deploy-time injection
    """
    config = PoolConfig(cwd=cwd)
    cwd_path = Path(cwd or Path.cwd())

    # Layer 1+2: YAML files (shared first, then local override)
    yaml_files = [
        cwd_path / ".autoservice" / "config.yaml",          # shared
        cwd_path / ".autoservice" / "config.local.yaml",    # local override
    ]
    for yaml_path in yaml_files:
        if not yaml_path.exists():
            continue
        try:
            import yaml
            data = yaml.safe_load(yaml_path.read_text(encoding="utf-8")) or {}
            pool_data = data.get("cc_pool", {})
            if isinstance(pool_data, dict):
                for key, val in pool_data.items():
                    if hasattr(config, key):
                        setattr(config, key, val)
        except Exception as e:
            log.warning("Failed to load pool config from %s: %s", yaml_path.name, e)

    # Layer 3: Env var overrides (CC_POOL_MIN_SIZE, CC_POOL_MAX_SIZE, etc.)
    _INT_FIELDS = {"min_size", "max_size", "warmup_count", "max_queries_per_instance"}
    _FLOAT_FIELDS = {"max_lifetime_seconds", "health_check_interval", "checkout_timeout"}
    _STR_FIELDS = {"cwd", "permission_mode", "model", "cli_path"}

    for field_name in _INT_FIELDS | _FLOAT_FIELDS | _STR_FIELDS:
        env_key = f"CC_POOL_{field_name.upper()}"
        env_val = os.environ.get(env_key)
        if env_val is not None:
            if field_name in _INT_FIELDS:
                setattr(config, field_name, int(env_val))
            elif field_name in _FLOAT_FIELDS:
                setattr(config, field_name, float(env_val))
            else:
                setattr(config, field_name, env_val)

    return config


# ---------------------------------------------------------------------------
# Pooled Instance
# ---------------------------------------------------------------------------

@dataclass
class PooledInstance:
    """Wraps a ClaudeSDKClient with pool metadata."""
    client: ClaudeSDKClient
    id: str
    created_at: float = field(default_factory=time.monotonic)
    query_count: int = 0
    last_used_at: float = field(default_factory=time.monotonic)

    def needs_recycling(self, config: PoolConfig) -> bool:
        """Check if instance should be recycled based on age or query count."""
        if self.query_count >= config.max_queries_per_instance:
            return True
        age = time.monotonic() - self.created_at
        if age >= config.max_lifetime_seconds:
            return True
        return False

    @property
    def is_healthy(self) -> bool:
        """Check if the underlying subprocess is still alive."""
        try:
            transport = self.client._transport
            if transport is None:
                return False
            process = getattr(transport, "_process", None)
            if process is None:
                return False
            return process.returncode is None
        except Exception:
            return False


# ---------------------------------------------------------------------------
# CC Pool
# ---------------------------------------------------------------------------

class CCPool:
    """Pool of pre-created ClaudeSDKClient instances."""

    def __init__(self, config: PoolConfig | None = None):
        self._config = config or PoolConfig()
        self._available: asyncio.Queue[PooledInstance] = asyncio.Queue()
        self._all_instances: dict[str, PooledInstance] = {}
        self._lock = asyncio.Lock()
        self._started = False
        self._shutdown_flag = False
        self._health_task: asyncio.Task | None = None
        self._instance_counter = 0

    @property
    def size(self) -> int:
        """Total number of tracked instances (checked out + available)."""
        return len(self._all_instances)

    def _track(self, instance: PooledInstance) -> None:
        self._all_instances[instance.id] = instance

    def _untrack(self, instance: PooledInstance) -> None:
        self._all_instances.pop(instance.id, None)

    @property
    def available_count(self) -> int:
        """Number of instances available for checkout."""
        return self._available.qsize()

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    async def start(self) -> None:
        """Start the pool: create warmup_count instances, start health monitor."""
        if self._started:
            return
        self._started = True
        self._shutdown_flag = False

        log.info(
            "Starting CC pool (min=%d, max=%d, warmup=%d)",
            self._config.min_size, self._config.max_size, self._config.warmup_count,
        )

        # Pre-create warm instances
        for i in range(self._config.warmup_count):
            try:
                instance = await self._create_instance()
                await self._available.put(instance)
                log.info("Warmed instance %s (%d/%d)", instance.id, i + 1, self._config.warmup_count)
            except Exception as e:
                log.error("Failed to create warm instance %d: %s", i + 1, e)

        # Start health monitor
        self._health_task = asyncio.create_task(
            self._health_check_loop(), name="cc-pool-health"
        )
        log.info("CC pool started with %d instance(s)", self.size)

    async def shutdown(self) -> None:
        """Graceful shutdown: stop health monitor, disconnect all instances."""
        if not self._started:
            return
        log.info("Shutting down CC pool (%d instances)...", self.size)
        self._shutdown_flag = True

        # Cancel health monitor
        if self._health_task and not self._health_task.done():
            self._health_task.cancel()
            try:
                await self._health_task
            except asyncio.CancelledError:
                pass
            self._health_task = None

        # Drain available queue
        while not self._available.empty():
            try:
                self._available.get_nowait()
            except asyncio.QueueEmpty:
                break

        # Disconnect all instances
        for instance in list(self._all_instances.values()):
            await self._destroy_instance(instance)

        self._started = False
        log.info("CC pool shut down.")

    # ------------------------------------------------------------------
    # Checkout / Checkin
    # ------------------------------------------------------------------

    async def checkout(self, timeout: float | None = None) -> PooledInstance:
        """Get a warm instance from the pool.

        If pool is exhausted and under max_size, creates a new one on demand.
        If at max_size, waits up to timeout seconds for one to be returned.

        Raises:
            TimeoutError: No instance available within timeout.
            RuntimeError: Pool not started or shutting down.
        """
        if not self._started or self._shutdown_flag:
            raise RuntimeError("Pool is not running")

        timeout = timeout if timeout is not None else self._config.checkout_timeout

        # Try to get an available instance (non-blocking)
        try:
            instance = self._available.get_nowait()
            if instance.is_healthy and not instance.needs_recycling(self._config):
                log.debug("Checked out instance %s (from queue)", instance.id)
                return instance
            # Unhealthy or needs recycling — destroy and try again
            await self._destroy_instance(instance)
        except asyncio.QueueEmpty:
            pass

        # Try to create a new instance if under max
        async with self._lock:
            if self.size < self._config.max_size:
                instance = await self._create_instance()
                log.debug("Checked out instance %s (on-demand)", instance.id)
                return instance

        # At max_size — wait for one to be returned
        log.debug("Pool exhausted (%d/%d), waiting...", self.size, self._config.max_size)
        try:
            instance = await asyncio.wait_for(self._available.get(), timeout=timeout)
            if instance.is_healthy and not instance.needs_recycling(self._config):
                log.debug("Checked out instance %s (after wait)", instance.id)
                return instance
            # Bad instance returned — destroy and create fresh
            await self._destroy_instance(instance)
            async with self._lock:
                return await self._create_instance()
        except asyncio.TimeoutError:
            raise TimeoutError(
                f"No CC instance available within {timeout}s "
                f"(pool size: {self.size}/{self._config.max_size})"
            )

    async def checkin(self, instance: PooledInstance) -> None:
        """Return an instance to the pool."""
        if self._shutdown_flag:
            await self._destroy_instance(instance)
            return

        instance.last_used_at = time.monotonic()

        if not instance.is_healthy or instance.needs_recycling(self._config):
            log.info(
                "Recycling instance %s (queries=%d, healthy=%s)",
                instance.id, instance.query_count, instance.is_healthy,
            )
            await self._destroy_instance(instance)
            # Replace in background
            asyncio.create_task(self._ensure_min_size(), name="cc-pool-refill")
            return

        await self._available.put(instance)
        log.debug("Checked in instance %s", instance.id)

    @asynccontextmanager
    async def acquire(self, timeout: float | None = None) -> AsyncIterator[PooledInstance]:
        """Async context manager: checkout on enter, checkin on exit."""
        instance = await self.checkout(timeout=timeout)
        try:
            yield instance
        finally:
            await self.checkin(instance)

    # ------------------------------------------------------------------
    # Convenience query
    # ------------------------------------------------------------------

    async def query(self, prompt: str, **kwargs: Any) -> AsyncIterator[Message]:
        """Convenience: checkout, query, yield messages, checkin.

        This is the primary integration point.
        """
        async with self.acquire() as instance:
            instance.query_count += 1
            session_id = kwargs.get("session_id", "default")
            await instance.client.query(prompt, session_id=session_id)
            async for msg in instance.client.receive_response():
                yield msg

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    async def _create_instance(self) -> PooledInstance:
        """Create and connect a new ClaudeSDKClient instance."""
        self._instance_counter += 1
        instance_id = f"cc-{self._instance_counter:03d}"

        cwd = self._config.cwd or str(Path.cwd())
        cwd_path = Path(cwd).absolute()
        plugin_path = cwd_path / ".autoservice" / ".claude"

        env = {}
        for var in ("http_proxy", "HTTP_PROXY", "https_proxy", "HTTPS_PROXY"):
            val = os.environ.get(var)
            if val:
                env[var] = val

        options = ClaudeAgentOptions(
            cwd=cwd,
            setting_sources=None,
            plugins=[{"type": "local", "path": str(plugin_path)}]
            if plugin_path.exists() else None,
            env=env,
            permission_mode=self._config.permission_mode,
            model=self._config.model,
            cli_path=self._config.cli_path,
        )

        client = ClaudeSDKClient(options)
        await client.connect()

        instance = PooledInstance(client=client, id=instance_id)
        self._track(instance)
        log.debug("Created instance %s (total: %d)", instance_id, self.size)
        return instance

    async def _destroy_instance(self, instance: PooledInstance) -> None:
        """Disconnect and remove an instance."""
        self._untrack(instance)
        try:
            await instance.client.disconnect()
        except Exception as e:
            log.warning("Error disconnecting instance %s: %s", instance.id, e)
        log.debug("Destroyed instance %s (total: %d)", instance.id, self.size)

    async def _ensure_min_size(self) -> None:
        """Create instances until min_size is met."""
        async with self._lock:
            while self.size < self._config.min_size and not self._shutdown_flag:
                try:
                    instance = await self._create_instance()
                    await self._available.put(instance)
                except Exception as e:
                    log.error("Failed to create replacement instance: %s", e)
                    break

    async def _health_check_loop(self) -> None:
        """Periodic health check: detect dead instances, maintain min_size."""
        while not self._shutdown_flag:
            try:
                await asyncio.sleep(self._config.health_check_interval)
            except asyncio.CancelledError:
                return

            if self._shutdown_flag:
                return

            # Scan available queue for unhealthy instances
            checked: list[PooledInstance] = []
            dead: list[PooledInstance] = []

            # Drain queue, check each, put healthy ones back
            while not self._available.empty():
                try:
                    inst = self._available.get_nowait()
                except asyncio.QueueEmpty:
                    break
                if inst.is_healthy and not inst.needs_recycling(self._config):
                    checked.append(inst)
                else:
                    dead.append(inst)

            for inst in checked:
                await self._available.put(inst)

            for inst in dead:
                log.info("Health check: recycling instance %s", inst.id)
                await self._destroy_instance(inst)

            # Maintain min_size
            await self._ensure_min_size()

            log.debug(
                "Health check: %d total, %d available, %d recycled",
                self.size, self.available_count, len(dead),
            )

    # ------------------------------------------------------------------
    # Status
    # ------------------------------------------------------------------

    def status(self) -> dict[str, Any]:
        """Return pool status for monitoring."""
        return {
            "started": self._started,
            "total": self.size,
            "available": self.available_count,
            "checked_out": self.size - self.available_count,
            "max_size": self._config.max_size,
            "instances": [
                {
                    "id": inst.id,
                    "query_count": inst.query_count,
                    "age_seconds": round(time.monotonic() - inst.created_at, 1),
                    "healthy": inst.is_healthy,
                }
                for inst in self._all_instances.values()
            ],
        }


# ---------------------------------------------------------------------------
# Module-level singleton
# ---------------------------------------------------------------------------

_pool: CCPool | None = None
_pool_lock = asyncio.Lock()


async def get_pool(config: PoolConfig | None = None) -> CCPool:
    """Get or create the global pool singleton."""
    global _pool
    if _pool is not None and _pool._started:
        return _pool

    async with _pool_lock:
        if _pool is not None and _pool._started:
            return _pool
        if config is None:
            config = load_pool_config()
        _pool = CCPool(config)
        await _pool.start()
        return _pool


async def shutdown_pool() -> None:
    """Shutdown the global pool."""
    global _pool
    if _pool is not None:
        await _pool.shutdown()
        _pool = None
