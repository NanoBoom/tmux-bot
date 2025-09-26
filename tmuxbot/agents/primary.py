"""Primary coordination agent for TmuxBot."""

import logging
from pydantic_ai import Agent

from ..model.factory import ModelFactory
from ..config.settings import Config
from . import TmuxBotDeps

logger = logging.getLogger(__name__)


AGENT_TYPE = "primary"


def create_primary_agent(config: Config) -> Agent[TmuxBotDeps, str]:
    model_factory = ModelFactory(config)

    model = model_factory.create_model(AGENT_TYPE)

    # Use agent-specific instructions if configured, otherwise use default
    default_instructions = (
        "You are TmuxBot's primary coordination agent, a conversational AI assistant for terminal environments. "
        "You help with coding, system administration, and general technical tasks using a multi-provider AI system. "
        "You can intelligently select the best AI provider for different types of tasks. "
        "Always provide clear, helpful responses and ask for clarification when needed."
    )

    final_instructions = default_instructions

    # Create agent with dependency injection
    agent = Agent(
        model=model,
        deps_type=TmuxBotDeps,
        output_type=str,
        instructions=final_instructions,
    )

    # @agent.tool
    # async def get_help(ctx: RunContext[TmuxBotDeps]) -> str:
    #     """Get help information about TmuxBot capabilities."""
    #     return (
    #         "TmuxBot Provider System - I'm your intelligent AI assistant!\n\n"
    #         "I can help you with:\n"
    #         "• Coding questions and solutions (using specialized code models)\n"
    #         "• Technical research and documentation\n"
    #         "• System administration and DevOps tasks\n"
    #         "• Planning and problem-solving\n"
    #         "• Creative writing and analysis\n\n"
    #         "I use multiple AI providers to give you the best responses for each task type.\n"
    #         "Just ask me anything, and I'll select the most appropriate AI model!"
    #     )
    #
    # @agent.tool
    # async def get_provider_status(ctx: RunContext[TmuxBotDeps]) -> str:
    #     """Get status of available AI providers."""
    #     try:
    #         status_info = []
    #         if provider_manager:
    #             provider_status = provider_manager.get_all_provider_status()
    #
    #             status_info.append("Provider Status:")
    #             for provider_name, status in provider_status.items():
    #                 health = "✅ Healthy" if status["is_healthy"] else "❌ Unhealthy"
    #                 status_info.append(f"• {provider_name}: {health}")
    #
    #                 if status["last_error"]:
    #                     status_info.append(f"  Last error: {status['last_error']}")
    #
    #                 if status["circuit_breaker_state"] != "closed":
    #                     status_info.append(
    #                         f"  Circuit breaker: {status['circuit_breaker_state']}"
    #                     )
    #         else:
    #             status_info.append("Provider system not initialized")
    #
    #         return "\n".join(status_info)
    #     except Exception as e:
    #         return f"Error getting provider status: {e}"
    #
    # @agent.tool
    # async def get_status(ctx: RunContext[TmuxBotDeps]) -> str:
    #     """Get current system and session status."""
    #     status_info = []
    #
    #     status_info.append(f"Current user: {ctx.deps.current_user}")
    #     status_info.append(f"Working directory: {ctx.deps.working_directory}")
    #     status_info.append(
    #         f"Conversation messages: {len(ctx.deps.conversation_history)}"
    #     )
    #
    #     if ctx.deps.tmux_session:
    #         status_info.append("Tmux session: Active")
    #     else:
    #         status_info.append("Tmux session: Not connected")
    #
    #     return "System Status:\n" + "\n".join(f"• {info}" for info in status_info)

    return agent


# def _create_default_provider_manager() -> ProviderManager:
#     """Create a default provider manager with standard configuration."""
#     try:
#         # Load provider configurations
#         provider_config_mgr = ProviderConfigManager()
#         provider_configs = provider_config_mgr.load_all_provider_configs()
#
#         # Create provider manager
#         manager = ProviderManager(
#             selection_strategy=SelectionStrategy.PERFORMANCE_OPTIMIZED
#         )
#
#         # Register providers
#         for provider_name, provider_config in provider_configs.items():
#             try:
#                 manager.register_provider(provider_name, provider_config)
#                 logger.info(f"Registered provider: {provider_name}")
#             except Exception as e:
#                 logger.error(f"Failed to register provider '{provider_name}': {e}")
#
#         return manager
#
#     except Exception as e:
#         logger.error(f"Failed to create provider manager: {e}")
#         # Return empty manager as fallback
#         return ProviderManager()


# def setup_primary_agent_tools(
#     primary_agent: Agent,
#     coder_agent: Optional[Agent] = None,
#     devops_agent: Optional[Agent] = None,
#     sysadmin_agent: Optional[Agent] = None,
# ) -> None:
#     """
#     Set up coordination tools for the primary agent to delegate to specialist agents.
#
#     This function is expected by tests but not fully implemented in Phase 1.
#     Future phases will add proper agent delegation tools here.
#
#     Args:
#         primary_agent: The primary coordination agent
#         coder_agent: Optional coding specialist agent
#         devops_agent: Optional DevOps specialist agent
#         sysadmin_agent: Optional system admin specialist agent
#     """
#     # Placeholder implementation for Phase 1
#     # Future phases will add tools that delegate to specialist agents
#     pass
