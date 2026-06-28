"""Tracing module for logging, timing, token tracking, and error reporting."""

from __future__ import annotations

import time
from typing import Any, Dict, List, Optional
from app.core.logging import logger


class Tracer:
    """ Observability tracer to monitor multi-agent execution steps, latency, and tokens. """

    def __init__(self, execution_id: str):
        self.execution_id = execution_id
        self.start_time = time.time()
        self.traces: List[Dict[str, Any]] = []

    def start_trace(self, node_name: str) -> None:
        """Log the starting point of an agent node."""
        logger.info(f"[Trace:{self.execution_id}] Node started: {node_name}")
        self.traces.append({
            "node": node_name,
            "action": "start",
            "timestamp": time.time(),
        })

    def end_trace(
        self,
        node_name: str,
        status: str = "success",
        error: Optional[str] = None,
        tokens_used: int = 0,
    ) -> None:
        """Log the ending point of an agent node and its execution metadata."""
        end_time = time.time()
        # Find start trace
        start_time = end_time
        for t in reversed(self.traces):
            if t["node"] == node_name and t["action"] == "start":
                start_time = t["timestamp"]
                break
        
        duration = round(end_time - start_time, 3)
        logger.info(f"[Trace:{self.execution_id}] Node ended: {node_name} | status: {status} | duration: {duration}s")
        
        self.traces.append({
            "node": node_name,
            "action": "end",
            "status": status,
            "duration": duration,
            "error": error,
            "tokens_used": tokens_used,
            "timestamp": end_time,
        })

    def get_summary(self) -> Dict[str, Any]:
        """Compile timing and token statistics for all executed nodes."""
        total_time = round(time.time() - self.start_time, 3)
        node_durations = {}
        errors = {}
        total_tokens = 0

        for t in self.traces:
            if t["action"] == "end":
                node_durations[t["node"]] = t["duration"]
                total_tokens += t.get("tokens_used", 0)
                if t["status"] == "failure":
                    errors[t["node"]] = t.get("error", "Unknown error")

        return {
            "execution_id": self.execution_id,
            "total_execution_time": total_time,
            "node_timings": node_durations,
            "total_tokens_used": total_tokens,
            "errors": errors,
        }

    def trace_rag_operation(self, operation: str, duration: float, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Trace a specific RAG operation (e.g. search, chunking, graph extraction) with latency."""
        logger.info(f"[Trace:{self.execution_id}] RAG Operation: {operation} | duration: {duration:.3f}s")
        self.traces.append({
            "node": f"rag_{operation}",
            "action": "rag_metric",
            "duration": duration,
            "metadata": metadata or {},
            "timestamp": time.time()
        })

