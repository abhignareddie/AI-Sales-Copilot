"""Memory Tool — Stores and retrieves long-term customer memory."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.memory import Memory
from app.core.logging import logger


class MemoryTool:
    """Manages persistent customer memory in PostgreSQL."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def store_memory(
        self,
        customer_id: int,
        memory_type: str,
        memory_data: dict,
    ) -> dict:
        """Store a memory record for a customer."""
        memory = Memory(
            customer_id=customer_id,
            memory_type=memory_type,
            memory_data=memory_data,
        )
        self.db.add(memory)
        await self.db.flush()
        await self.db.refresh(memory)
        logger.info(f"Memory stored: type={memory_type} customer={customer_id}")
        return {
            "id": memory.id,
            "memory_type": memory.memory_type,
            "memory_data": memory.memory_data,
            "created_at": memory.created_at.isoformat() if memory.created_at else None,
        }

    async def retrieve_memory(
        self,
        customer_id: int,
        memory_type: str | None = None,
        limit: int = 20,
    ) -> list[dict]:
        """Retrieve memory records for a customer."""
        query = select(Memory).where(Memory.customer_id == customer_id)
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

    async def retrieve_all_memory(self, customer_id: int) -> list[dict]:
        """Retrieve all memory for a customer (used at pipeline start)."""
        return await self.retrieve_memory(customer_id, limit=50)
