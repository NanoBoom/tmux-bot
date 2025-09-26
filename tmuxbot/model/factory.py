# Standard library imports
import importlib
import logging
from typing import Callable, Optional, cast

# Third-party imports
from pydantic_ai.models import Model

# Local imports
from ..config import Config

logger = logging.getLogger(__name__)


class ModelFactory:
    """Factory class for creating AI models based on configuration profiles.

    The ModelFactory dynamically loads AI provider modules and creates models
    according to agent configurations and provider profiles. It supports
    multiple AI providers through a plugin-like architecture.

    Attributes:
        config: TmuxBot configuration containing profiles and agent settings.

    Example:
        >>> config = load_config()
        >>> factory = ModelFactory(config)
        >>> model = factory.create_model("primary")
    """

    def __init__(self, config: Config) -> None:
        self.config = config
        self._validate_fallback_configuration()

    def _validate_fallback_configuration(self) -> None:
        """Validate that all fallback profiles exist in the configuration.

        Logs warnings for any fallback profiles that don't exist.
        """
        for agent_name, agent_config in self.config.agents.items():
            if agent_config.fallbacks:
                for fallback_profile in agent_config.fallbacks:
                    if fallback_profile not in self.config.profiles:
                        logger.warning(
                            f"Agent '{agent_name}' has fallback profile '{fallback_profile}' "
                            f"which is not defined in the configuration"
                        )

    def create_model(
        self,
        agent_type: str,
    ) -> Optional[Model]:
        """Create a model instance for the specified agent type with fallback support.

        Dynamically loads the appropriate AI provider module based on the agent's
        profile configuration and creates a model instance using the provider's
        create_model function. If the primary profile fails, tries fallback profiles
        in order.

        Args:
            agent_type: The type of agent to create a model for (e.g., "primary", "coder").
                       Must match an agent configuration in the config.

        Returns:
            A configured AI model ready for use, or None if the agent configuration
            or profile is not found, or if all profiles (primary + fallbacks) fail.

        Raises:
            ValueError: If the provider module doesn't exist or lacks a create_model function.
            RuntimeError: If an unexpected error occurs during model creation.

        Example:
            >>> factory = ModelFactory(config)
            >>> model = factory.create_model("primary")
            >>> if model:
            ...     response = model.generate("Hello, world!")
        """
        agent_config = self.config.agents.get(agent_type)
        if agent_config is None:
            logger.error(f"Agent configuration not found: {agent_type}")
            return None

        # Try primary profile first, then fallbacks
        profile_names = [agent_config.profile]
        if agent_config.fallbacks:
            profile_names.extend(agent_config.fallbacks)

        last_error = None
        for profile_name in profile_names:
            try:
                model = self._create_model_for_profile(profile_name)
                if model is not None:
                    if profile_name != agent_config.profile:
                        logger.warning(
                            f"Primary profile '{agent_config.profile}' failed, using fallback '{profile_name}' for agent '{agent_type}'"
                        )
                    else:
                        logger.debug(
                            f"Using primary profile '{profile_name}' for agent '{agent_type}'"
                        )
                    return model
            except Exception as e:
                last_error = e
                logger.warning(
                    f"Profile '{profile_name}' failed for agent '{agent_type}': {e}"
                )
                continue

        # If we get here, all profiles failed
        if last_error:
            logger.error(
                f"All profiles failed for agent '{agent_type}'. Last error: {last_error}"
            )
        else:
            logger.error(f"No valid profiles found for agent '{agent_type}'")

        return None

    def _create_model_for_profile(self, profile_name: str) -> Optional[Model]:
        """Create a model for a specific profile.

        Args:
            profile_name: Name of the profile to use.

        Returns:
            A configured AI model, or None if profile not found.

        Raises:
            ValueError: If the provider module doesn't exist or lacks a create_model function.
            RuntimeError: If an unexpected error occurs during model creation.
            ConnectionError: If unable to connect to the AI provider.
        """
        profile = self.config.profiles.get(profile_name)
        if profile is None:
            logger.error(f"Profile not found: {profile_name}")
            return None

        logger.debug(
            f"Attempting to create model for profile: {profile.provider}:{profile.model}"
        )

        provider_name = profile.provider

        try:
            provider_module = importlib.import_module(
                f"tmuxbot.providers.{provider_name}"
            )

            logger.debug(
                f"Successfully imported provider module: tmuxbot.providers.{provider_name}"
            )

            create_model_attr = getattr(provider_module, "create_model", None)
            if create_model_attr is None:
                error_msg = f"Provider module '{provider_name}' does not have a 'create_model' function"
                raise ValueError(error_msg)

            create_model_func = cast(Callable[..., Model], create_model_attr)
            return create_model_func(profile)

        except ImportError as err:
            error_msg = f"Unsupported provider specified: '{provider_name}'. Could not find provider module 'tmuxbot.providers.{provider_name}'"
            logger.error(error_msg)
            raise ValueError(error_msg) from err

        except AttributeError as err:
            error_msg = f"Provider module '{provider_name}' does not have a 'create_model' function"
            logger.error(error_msg)
            raise ValueError(error_msg) from err

        except Exception as e:
            error_msg = f"An unexpected error occurred while loading provider '{provider_name}': {e}"
            logger.error(error_msg, exc_info=True)
            raise RuntimeError(error_msg) from e
