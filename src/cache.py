"""
Persistent cache layer with Git commit tracking and auto-invalidation
Stores brief and detailed outputs separately for progressive disclosure
"""

import json
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any
from git import Repo


class CacheEntry:
    """Represents a single cache entry"""

    def __init__(
        self,
        component: str,
        query_type: str,
        brief_output: str,
        detailed_output: str,
        git_commit: str,
        timestamp: str,
    ):
        self.component = component
        self.query_type = query_type
        self.brief_output = brief_output
        self.detailed_output = detailed_output
        self.git_commit = git_commit
        self.timestamp = datetime.fromisoformat(timestamp)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON storage"""
        return {
            "component": self.component,
            "query_type": self.query_type,
            "brief_output": self.brief_output,
            "detailed_output": self.detailed_output,
            "git_commit": self.git_commit,
            "timestamp": self.timestamp.isoformat(),
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "CacheEntry":
        """Create CacheEntry from dictionary"""
        return CacheEntry(
            component=data["component"],
            query_type=data["query_type"],
            brief_output=data["brief_output"],
            detailed_output=data["detailed_output"],
            git_commit=data["git_commit"],
            timestamp=data["timestamp"],
        )


class CacheManager:
    """Manages persistent cache with Git commit tracking and auto-invalidation"""

    def __init__(self, cache_dir: Path, repo_path: Path, ttl_days: int = 7, auto_invalidate: bool = True):
        self.cache_dir = Path(cache_dir)
        self.repo_path = Path(repo_path)
        self.ttl_days = ttl_days
        self.auto_invalidate = auto_invalidate
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Initialize Git repo
        self.repo = Repo(self.repo_path)

    def get_current_commit(self) -> str:
        """Get the current Git commit hash"""
        return self.repo.head.commit.hexsha

    def get(self, component: str, query_type: str) -> Optional[CacheEntry]:
        """
        Retrieve cache entry if valid

        Returns None if:
        - Cache entry doesn't exist
        - Entry has expired (TTL)
        - Git commit has changed (auto-invalidation enabled)
        """
        cache_path = self._get_cache_path(component, query_type)

        if not cache_path.exists():
            return None

        try:
            with open(cache_path, "r") as f:
                data = json.load(f)

            entry = CacheEntry.from_dict(data)

            # Check TTL
            if datetime.now() - entry.timestamp > timedelta(days=self.ttl_days):
                cache_path.unlink()
                return None

            # Check Git commit if auto-invalidation is enabled
            if self.auto_invalidate:
                current_commit = self.get_current_commit()
                if entry.git_commit != current_commit:
                    cache_path.unlink()
                    return None

            return entry

        except (json.JSONDecodeError, KeyError, ValueError):
            # Corrupted cache file - delete it
            cache_path.unlink()
            return None

    def set(
        self,
        component: str,
        query_type: str,
        brief_output: str,
        detailed_output: str,
    ) -> None:
        """Store cache entry with current Git commit"""
        cache_path = self._get_cache_path(component, query_type)
        cache_path.parent.mkdir(parents=True, exist_ok=True)

        entry = CacheEntry(
            component=component,
            query_type=query_type,
            brief_output=brief_output,
            detailed_output=detailed_output,
            git_commit=self.get_current_commit(),
            timestamp=datetime.now().isoformat(),
        )

        with open(cache_path, "w") as f:
            json.dump(entry.to_dict(), f, indent=2)

    def clear(self, component: Optional[str] = None) -> int:
        """
        Clear cache entries

        Args:
            component: If specified, only clear cache for this component.
                      If None, clear all cache.

        Returns:
            Number of cache entries cleared
        """
        count = 0

        if component is None:
            # Clear all cache
            for cache_file in self.cache_dir.rglob("*.json"):
                cache_file.unlink()
                count += 1
        else:
            # Clear cache for specific component
            component_hash = self._hash_component_name(component)
            component_dir = self.cache_dir / component_hash
            if component_dir.exists():
                for cache_file in component_dir.glob("*.json"):
                    cache_file.unlink()
                    count += 1

        return count

    def get_stats(self) -> Dict[str, int]:
        """Get cache statistics"""
        total_entries = len(list(self.cache_dir.rglob("*.json")))
        total_components = len(list(self.cache_dir.glob("*")))

        return {
            "total_entries": total_entries,
            "total_components": total_components,
        }

    def _get_cache_path(self, component: str, query_type: str) -> Path:
        """Get the file path for a cache entry"""
        component_hash = self._hash_component_name(component)
        return self.cache_dir / component_hash / f"{query_type}.json"

    def _hash_component_name(self, component: str) -> str:
        """Generate a hash for the component name"""
        return hashlib.md5(component.encode()).hexdigest()[:8]
