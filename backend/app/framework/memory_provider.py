"""Memory Provider implementations matching PostgreSQL, Redis, and Mock memory storage."""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.framework.interfaces import BaseMemoryProvider
from app.models.memory import Memory
from app.core.logging import logger


class SqlAlchemyMemoryProvider(BaseMemoryProvider):
    """Database-backed memory provider using SQL Alchemy (Postgres/SQLite)."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def store(self, key: str, memory_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        memory = Memory(
            customer_id=int(key),  # Key maps to customer_id in sales domain
            memory_type=memory_type,
            memory_data=data,
        )
        self.db.add(memory)
        await self.db.flush()
        await self.db.refresh(memory)
        return {
            "id": memory.id,
            "memory_type": memory.memory_type,
            "memory_data": memory.memory_data,
            "created_at": memory.created_at.isoformat() if memory.created_at else None,
        }

    async def retrieve(self, key: str, memory_type: Optional[str] = None, limit: int = 20) -> List[Dict[str, Any]]:
        query = select(Memory).where(Memory.customer_id == int(key))
        if memory_type:
            query = query.where(Memory.memory_type == memory_type)
        query = query.order_by(Memory.created_at.desc()).limit(limit)

        result = await self.db.execute(query)
        memories = result.scalars().all()
        return [
            {
                "id": m.id,
                "memory_type": m.memory_type,
                "memory_data": m.memory_data,
                "created_at": m.created_at.isoformat() if m.created_at else None,
            }
            for m in memories
        ]


class MockMemoryProvider(BaseMemoryProvider):
    """Mock Memory Provider using an in-memory dictionary. Extremely useful for testing."""

    def __init__(self):
        self.store_dict: Dict[str, List[Dict[str, Any]]] = {}

    async def store(self, key: str, memory_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        self.store_dict.setdefault(key, [])
        record = {
            "id": len(self.store_dict[key]) + 1,
            "memory_type": memory_type,
            "memory_data": data,
        }
        self.store_dict[key].append(record)
        return record

    async def retrieve(self, key: str, memory_type: Optional[str] = None, limit: int = 20) -> List[Dict[str, Any]]:
        records = self.store_dict.get(key, [])
        if memory_type:
            records = [r for r in records if r["memory_type"] == memory_type]
        records.reverse()
        return records[:limit]
