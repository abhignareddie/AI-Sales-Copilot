"""YAML Workflow Engine — Dynamically parses YAML configurations and compiles LangGraph state graphs."""

from __future__ import annotations

import os
import yaml
import asyncio
from typing import Any, Dict, List
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from app.framework.registry import AgentRegistry
from app.framework.interfaces import BaseAgent
from app.framework.tracer import Tracer
from app.agents.schemas.agent_state import AgentState, create_initial_state
from app.core.logging import logger


class WorkflowEngine:
    """Dynamically compiles and runs LangGraph agent workflows using YAML configuration files."""

    def __init__(self, workflow_name: str, db_session: Any = None):
        self.workflow_name = workflow_name
        self.db_session = db_session
        self.config = self._load_workflow_config()
        self.compiled_graph = self._compile_graph()

    def _load_workflow_config(self) -> Dict[str, Any]:
        """Load the YAML configuration for the named workflow."""
        # Search path
        base_dir = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(base_dir, "workflows", f"{self.workflow_name}.yaml")
        
        if not os.path.exists(path):
            raise FileNotFoundError(f"Workflow configuration file not found at {path}")

        with open(path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
            logger.info(f"[WorkflowEngine] Loaded workflow config: {config.get('name')}")
            return config

    def _compile_graph(self) -> Any:
        """Dynamically compile a LangGraph StateGraph from the loaded workflow config."""
        graph = StateGraph(AgentState)
        steps = self.config.get("workflows", [])
        
        # Add all node agent instances
        node_instances = {}
        for step in steps:
            for agent_name in step.get("agents", []):
                # Retrieve from Registry
                agent_class = AgentRegistry.get(agent_name)
                # Resolve dependency injection if Agent requires DB session
                try:
                    # Try to instantiate with db session if required
                    instance = agent_class(self.db_session)
                except TypeError:
                    instance = agent_class()
                
                node_instances[agent_name] = instance

        # Define wrapper execution function with retry policies and tracing
        def make_node_wrapper(agent_name: str, agent_instance: BaseAgent):
            async def node_fn(state: AgentState) -> AgentState:
                tracer = state.get("tracer")
                if tracer:
                    tracer.start_trace(agent_name)

                # Execute with error capture
                retries = self.config.get("retry_policy", {}).get("max_retries", 2)
                last_error = None
                
                for attempt in range(retries + 1):
                    try:
                        # Direct execution
                        new_state = await agent_instance.execute(state)
                        if tracer:
                            tracer.end_trace(agent_name, "success")
                        # Success
                        return new_state
                    except Exception as e:
                        last_error = e
                        logger.warning(f"[WorkflowEngine] Retry {attempt + 1}/{retries} on agent {agent_name} due to: {e}")
                        await asyncio.sleep(0.5)

                logger.error(f"[WorkflowEngine] Agent {agent_name} failed completely: {last_error}")
                if tracer:
                    tracer.end_trace(agent_name, "failure", error=str(last_error))
                
                # Merge errors in state
                errs = state.get("agent_errors", {}).copy()
                errs[agent_name] = str(last_error)
                return {**state, "agent_errors": errs}
                
            return node_fn

        # Add nodes to graph
        for agent_name, instance in node_instances.items():
            graph.add_node(agent_name, make_node_wrapper(agent_name, instance))

        # Dynamic parallel analysis nodes handler
        parallel_nodes_map = {}
        for step in steps:
            if step.get("parallel", False) and len(step.get("agents", [])) > 1:
                group_name = f"parallel_group_{step.get('step')}"
                agents = step.get("agents", [])
                
                # Define parallel step execution node
                def make_parallel_node(agents_list=agents, instances=node_instances):
                    async def parallel_fn(state: AgentState) -> AgentState:
                        tasks = []
                        for a_name in agents_list:
                            # Use the agent instance directly
                            instance = instances.get(a_name)
                            if instance is not None:
                                tasks.append(instance.execute(state))
                        
                        results = await asyncio.gather(*tasks, return_exceptions=True)
                        
                        # Merge states
                        merged = {**state}
                        for res in results:
                            if isinstance(res, Exception):
                                continue
                            for key, val in res.items():
                                if key == "executed_agents":
                                    merged["executed_agents"] = list(merged.get("executed_agents", [])) + list(val)
                                elif key == "agent_errors":
                                    merged.setdefault("agent_errors", {}).update(val)
                                elif key == "agent_timings":
                                    merged.setdefault("agent_timings", {}).update(val)
                                elif val:
                                    merged[key] = val
                        return merged
                    return parallel_fn
                
                # Re-add parallel handler
                graph.add_node(group_name, make_parallel_node())
                parallel_nodes_map[step.get("step")] = group_name

        # Add edges based on YAML steps
        sorted_steps = sorted(steps, key=lambda x: x.get("step"))
        
        # Helper to get start node of a step
        def get_step_node(step_index: int) -> str:
            step_item = sorted_steps[step_index]
            if step_item.get("parallel", False) and len(step_item.get("agents", [])) > 1:
                return f"parallel_group_{step_item.get('step')}"
            return step_item.get("agents", [])[0]

        # Set Entry Point to Step 1 start node
        graph.set_entry_point(get_step_node(0))

        # Add edges linking steps sequentially
        for idx in range(len(sorted_steps) - 1):
            curr_node = get_step_node(idx)
            next_node = get_step_node(idx + 1)
            graph.add_edge(curr_node, next_node)

        # Connect last step to END
        last_node = get_step_node(len(sorted_steps) - 1)
        graph.add_edge(last_node, END)

        # Compile with memory saver checkpointer
        return graph.compile(checkpointer=MemorySaver())

    async def execute(
        self,
        customer_id: int,
        business_goal: str,
        user_id: int,
    ) -> Dict[str, Any]:
        """Execute the workflow asynchronously."""
        # Initialize tracing
        state = create_initial_state(customer_id, business_goal, user_id)
        tracer = Tracer(state["execution_id"])
        # Do NOT put tracer into graph state — LangGraph checkpointer (MemorySaver)
        # serializes state with msgpack and Tracer is not serializable.

        config = {"configurable": {"thread_id": state["execution_id"]}}
        
        try:
            final_state = await self.compiled_graph.ainvoke(state, config=config)
        except Exception as e:
            logger.error(f"[WorkflowEngine] Graph execution crashed: {e}")
            final_state = {
                **state,
                "agent_errors": {"workflow_engine": str(e)},
            }

        # Structure response output
        summary = tracer.get_summary()
        
        # Save recommendations to database if saved tool exists
        recommendations = final_state.get("recommendations", [])
        if self.db_session and recommendations:
            from app.agents.tools.recommendation_tool import RecommendationTool
            try:
                rec_tool = RecommendationTool(self.db_session)
                await rec_tool.save_recommendations(customer_id, recommendations)
            except Exception as ex:
                logger.warning(f"[WorkflowEngine] Failed saving recommendations to database: {ex}")

        # Assemble general response
        cust = final_state.get("customer", {})
        risk = final_state.get("risk_assessment", {})
        opp = final_state.get("opportunity_assessment", {})

        return {
            "execution_id": summary["execution_id"],
            "execution_time": summary["total_execution_time"],
            "executed_agents": final_state.get("executed_agents", []),
            "agent_timings": summary["node_timings"],
            "agent_errors": summary["errors"],
            "planner_reasoning": final_state.get("planner_decisions", {}).get("reasoning", "Execution completed via static YAML workflow."),
            "customer_summary": {
                "company": cust.get("company_name", "Unknown"),
                "stage": cust.get("current_stage", "Unknown"),
                "health_score": cust.get("health_score", 0),
            },
            "risk": {
                "level": risk.get("risk_level", "low"),
                "score": risk.get("overall_risk_score", 0.0),
                "top_factors": risk.get("top_risk_factors", []),
            },
            "opportunity": {
                "score": opp.get("overall_opportunity_score", 0.0),
                "win_probability": opp.get("win_probability", {}).get("score", 0.0),
            },
            "recommendations": recommendations,
            "confidence": final_state.get("confidence", 0.8),
            "evidence": final_state.get("evidence", []),
            "retrieved_documents": [
                {
                    "source": d.get("source", "unknown"),
                    "similarity": d.get("similarity_score", 0.0),
                    "content_preview": d.get("content", "")[:200],
                }
                for d in final_state.get("retrieved_documents", [])
            ],
            "memory_used": len(final_state.get("memory", [])),
            "memory_updated": final_state.get("memory_updated", False),
        }
