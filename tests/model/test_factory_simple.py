"""Simplified tests for ModelFactory class to avoid mocking conflicts."""

import pytest
from unittest.mock import Mock, patch, MagicMock

from tmuxbot.model.factory import ModelFactory


class TestModelFactorySimple:
    """Simplified test cases for ModelFactory class."""

    def test_agent_not_found(self, mock_config_missing_agent):
        """Test error handling when agent configuration is not found."""
        factory = ModelFactory(mock_config_missing_agent)

        with patch('tmuxbot.model.factory.logger') as mock_logger:
            result = factory.create_model("nonexistent-agent")

            # Verify None return and error logging
            assert result is None
            mock_logger.error.assert_called_once_with(
                "Agent configuration not found: nonexistent-agent"
            )

    def test_profile_not_found(self, mock_config_missing_profile):
        """Test error handling when profile is not found."""
        factory = ModelFactory(mock_config_missing_profile)
        result = factory.create_model("primary")

        # Verify None return when profile not found
        assert result is None

    def test_empty_agent_type(self, mock_config):
        """Test edge case with empty agent type."""
        factory = ModelFactory(mock_config)

        with patch('tmuxbot.model.factory.logger') as mock_logger:
            result = factory.create_model("")

            assert result is None
            mock_logger.error.assert_called_once_with(
                "Agent configuration not found: "
            )

    def test_factory_initialization(self, mock_config):
        """Test ModelFactory initialization."""
        factory = ModelFactory(mock_config)
        assert factory.config == mock_config

    def test_import_error_handling(self, mock_config):
        """Test ImportError is properly handled with fallback mechanism."""
        # Patch the import to raise ImportError
        with patch('tmuxbot.model.factory.importlib.import_module') as mock_import:
            mock_import.side_effect = ImportError("No module named 'tmuxbot.providers.nonexistent'")

            factory = ModelFactory(mock_config)

            # With fallback mechanism, import errors result in None being returned (no exception raised)
            result = factory.create_model("primary")
            assert result is None

    def test_create_model_with_valid_provider(self, mock_config):
        """Test successful model creation with real provider import."""
        # Use the real openai provider import but mock the pydantic_ai components
        with patch('tmuxbot.providers.openai.OpenAIProvider') as mock_provider_class, \
             patch('tmuxbot.providers.openai.OpenAIChatModel') as mock_model_class:

            # Setup mocks for pydantic_ai components
            mock_provider = Mock()
            mock_provider_class.return_value = mock_provider

            mock_model = Mock()
            mock_model_class.return_value = mock_model

            factory = ModelFactory(mock_config)
            result = factory.create_model("primary")

            # Verify that the real provider was called correctly
            assert result == mock_model
            mock_provider_class.assert_called_once()
            mock_model_class.assert_called_once()

    def test_logger_debug_message(self, mock_config):
        """Test that logger.debug is called with profile info."""
        with patch('tmuxbot.model.factory.logger') as mock_logger, \
             patch('tmuxbot.providers.openai.OpenAIProvider') as mock_provider_class, \
             patch('tmuxbot.providers.openai.OpenAIChatModel') as mock_model_class:

            mock_provider = Mock()
            mock_provider_class.return_value = mock_provider

            mock_model = Mock()
            mock_model_class.return_value = mock_model

            factory = ModelFactory(mock_config)
            result = factory.create_model("primary")

            # Verify debug messages were logged
            expected_profile = mock_config.profiles["openai-gpt-4"]
            debug_calls = [call.args[0] for call in mock_logger.debug.call_args_list]

            # Check that both debug messages were called - updated for new fallback logic
            expected_profile_msg = f"Attempting to create model for profile: {expected_profile.provider}:{expected_profile.model}"
            expected_import_msg = "Successfully imported provider module: tmuxbot.providers.openai"
            expected_primary_msg = f"Using primary profile 'openai-gpt-4' for agent 'primary'"

            assert expected_profile_msg in debug_calls
            assert expected_import_msg in debug_calls
            assert expected_primary_msg in debug_calls

    def test_attribute_error_handling(self, mock_config):
        """Test AttributeError is properly handled with fallback mechanism."""
        with patch('tmuxbot.model.factory.importlib.import_module') as mock_import:
            # Create a mock module that doesn't have create_model
            mock_provider_module = Mock()
            del mock_provider_module.create_model  # Remove create_model attribute
            mock_import.return_value = mock_provider_module

            factory = ModelFactory(mock_config)

            # With fallback mechanism, errors result in None being returned
            result = factory.create_model("primary")
            assert result is None

    def test_create_model_function_none(self, mock_config):
        """Test when getattr returns None for create_model with fallback mechanism."""
        with patch('tmuxbot.model.factory.importlib.import_module') as mock_import:
            mock_provider_module = Mock()
            # Mock getattr to return None for create_model
            mock_provider_module.create_model = None
            mock_import.return_value = mock_provider_module

            factory = ModelFactory(mock_config)

            # With fallback mechanism, errors result in None being returned
            result = factory.create_model("primary")
            assert result is None

    def test_unexpected_exception_handling(self, mock_config):
        """Test unexpected exception handling with fallback mechanism."""
        with patch('tmuxbot.providers.openai.OpenAIProvider') as mock_provider_class:
            # Make the provider constructor raise an unexpected exception
            mock_provider_class.side_effect = Exception("Unexpected error")

            factory = ModelFactory(mock_config)

            # With fallback mechanism, errors result in None being returned
            result = factory.create_model("primary")
            assert result is None

    def test_fallback_configuration_validation(self, mock_config):
        """Test validation of fallback profiles during factory initialization."""
        # Create agent config with invalid fallback
        from tmuxbot.config.settings import AgentConfig, Config

        invalid_agent = AgentConfig(
            profile="openai-gpt-4",
            instructions="Test agent",
            fallbacks=["nonexistent-profile", "another-invalid"]
        )

        config_with_invalid_fallbacks = Config(
            profiles=mock_config.profiles,
            agents={"test": invalid_agent},
            max_history=100,
            conversation_timeout=300
        )

        with patch('tmuxbot.model.factory.logger') as mock_logger:
            factory = ModelFactory(config_with_invalid_fallbacks)

            # Verify warnings were logged for invalid fallback profiles
            warning_calls = [call.args[0] for call in mock_logger.warning.call_args_list]
            assert any("nonexistent-profile" in msg for msg in warning_calls)
            assert any("another-invalid" in msg for msg in warning_calls)

    def test_fallback_success_when_primary_fails(self, mock_config):
        """Test successful fallback when primary profile fails."""
        # Create agent config with fallbacks
        from tmuxbot.config.settings import AgentConfig, Config, ProfileConfig

        fallback_profile = ProfileConfig(
            provider="openai",
            api_key="fallback-key",
            model="gpt-3.5-turbo",
        )

        agent_with_fallbacks = AgentConfig(
            profile="openai-gpt-4",
            instructions="Test agent",
            fallbacks=["fallback-profile"]
        )

        config_with_fallbacks = Config(
            profiles={
                **mock_config.profiles,
                "fallback-profile": fallback_profile
            },
            agents={"test": agent_with_fallbacks},
            max_history=100,
            conversation_timeout=300
        )

        with patch('tmuxbot.model.factory.logger') as mock_logger, \
             patch('tmuxbot.providers.openai.OpenAIProvider') as mock_provider_class, \
             patch('tmuxbot.providers.openai.OpenAIChatModel') as mock_model_class:

            # First call (primary profile) fails, second call (fallback) succeeds
            mock_provider_class.side_effect = [Exception("Primary failed"), Mock()]
            mock_model = Mock()
            mock_model_class.return_value = mock_model

            factory = ModelFactory(config_with_fallbacks)
            result = factory.create_model("test")

            # Verify fallback was used successfully
            assert result == mock_model

            # Verify warning was logged about using fallback
            warning_calls = [call.args[0] for call in mock_logger.warning.call_args_list]
            assert any("Primary profile 'openai-gpt-4' failed, using fallback 'fallback-profile'" in msg for msg in warning_calls)

    def test_fallback_all_profiles_fail(self, mock_config):
        """Test behavior when all profiles (primary + fallbacks) fail."""
        from tmuxbot.config.settings import AgentConfig, Config, ProfileConfig

        fallback_profile = ProfileConfig(
            provider="openai",
            api_key="fallback-key",
            model="gpt-3.5-turbo",
        )

        agent_with_fallbacks = AgentConfig(
            profile="openai-gpt-4",
            instructions="Test agent",
            fallbacks=["fallback-profile"]
        )

        config_with_fallbacks = Config(
            profiles={
                **mock_config.profiles,
                "fallback-profile": fallback_profile
            },
            agents={"test": agent_with_fallbacks},
            max_history=100,
            conversation_timeout=300
        )

        with patch('tmuxbot.model.factory.logger') as mock_logger, \
             patch('tmuxbot.providers.openai.OpenAIProvider') as mock_provider_class:

            # All profile creation attempts fail
            mock_provider_class.side_effect = Exception("All providers fail")

            factory = ModelFactory(config_with_fallbacks)
            result = factory.create_model("test")

            # Verify None is returned when all profiles fail
            assert result is None

            # Verify error logging
            error_calls = [call.args[0] for call in mock_logger.error.call_args_list]
            assert any("All profiles failed for agent 'test'" in msg for msg in error_calls)

    def test_fallback_with_nonexistent_fallback_profile(self, mock_config):
        """Test behavior when fallback profile doesn't exist."""
        from tmuxbot.config.settings import AgentConfig, Config

        agent_with_invalid_fallback = AgentConfig(
            profile="openai-gpt-4",
            instructions="Test agent",
            fallbacks=["nonexistent-profile"]
        )

        config_with_invalid_fallback = Config(
            profiles=mock_config.profiles,
            agents={"test": agent_with_invalid_fallback},
            max_history=100,
            conversation_timeout=300
        )

        with patch('tmuxbot.model.factory.logger') as mock_logger, \
             patch('tmuxbot.providers.openai.OpenAIProvider') as mock_provider_class:

            # Primary profile fails
            mock_provider_class.side_effect = Exception("Primary failed")

            factory = ModelFactory(config_with_invalid_fallback)
            result = factory.create_model("test")

            # Verify None is returned
            assert result is None

            # Verify appropriate error logging for nonexistent fallback profile
            error_calls = [call.args[0] for call in mock_logger.error.call_args_list]
            assert any("Profile not found: nonexistent-profile" in msg for msg in error_calls)

    def test_no_fallbacks_configured(self, mock_config):
        """Test behavior when no fallbacks are configured and primary fails."""
        with patch('tmuxbot.model.factory.logger') as mock_logger, \
             patch('tmuxbot.providers.openai.OpenAIProvider') as mock_provider_class:

            # Primary profile fails
            mock_provider_class.side_effect = Exception("Primary failed")

            factory = ModelFactory(mock_config)
            result = factory.create_model("primary")

            # Verify None is returned
            assert result is None

            # Verify error logging
            error_calls = [call.args[0] for call in mock_logger.error.call_args_list]
            assert any("All profiles failed for agent 'primary'" in msg for msg in error_calls)