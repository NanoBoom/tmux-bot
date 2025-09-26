# TmuxBot Configuration Summary

## 🎉 XDG-Compliant Configuration System

TmuxBot now uses the XDG Base Directory specification for configuration management, providing a standardized and user-friendly approach to storing configuration files.

**Configuration Location**: `~/.config/tmuxbot/config.yaml`

This package includes a comprehensive configuration system for TmuxBot with XDG Base Directory compliance and profile-based architecture.

### 📁 XDG Base Directory Structure

TmuxBot follows the XDG Base Directory specification for standardized configuration management:

#### XDG Configuration Location
- **`~/.config/tmuxbot/config.yaml`** - Main configuration file (XDG-compliant location)
- **`$XDG_CONFIG_HOME/tmuxbot/config.yaml`** - Alternative location if XDG_CONFIG_HOME is set

#### Configuration Migration
- **Legacy Support**: `./config.yaml` (deprecated, shows migration warnings)
- **Migration Tools**: Automatic migration utilities available
- **Backward Compatibility**: Maintains full functionality during transition

#### Configuration Management Scripts
- **`scripts/setup-config.py`** - XDG configuration validation and setup
- **`scripts/migrate-config-xdg.py`** - Standalone migration utility
- **`tmuxbot/utils/config_migration.py`** - Migration helper functions

### 🔧 XDG Base Directory Benefits

#### Standards Compliance
- ✅ Follows Linux/Unix configuration conventions
- ✅ Compatible with system backup tools
- ✅ Integrates with configuration management systems
- ✅ Provides clean home directory organization

#### User Experience
- ✅ Consistent configuration location across systems
- ✅ Easy to find and manage configuration files
- ✅ Supports multi-user environments
- ✅ Automatic directory creation

## 🚀 Quick Start with XDG Configuration

### 1. Create XDG Configuration
```bash
# Create configuration template at XDG location (~/.config/tmuxbot/config.yaml)
python scripts/setup-config.py --create-template

# Or use the configuration loading system (creates template automatically)
python -c "from tmuxbot.config.settings import save_config_template; save_config_template()"
```

### 2. Configure API Keys
Edit the XDG configuration file with your API keys:
```bash
# Open configuration file for editing
$EDITOR ~/.config/tmuxbot/config.yaml

# The file will be located at:
# ~/.config/tmuxbot/config.yaml (default)
# or $XDG_CONFIG_HOME/tmuxbot/config.yaml (if XDG_CONFIG_HOME is set)
```

### 3. Validate Configuration
```bash
# Validate XDG configuration
python scripts/setup-config.py --validate

# Run complete configuration check
python scripts/setup-config.py --full-check

# Check migration status (if upgrading from legacy)
python scripts/setup-config.py --check-migration
```

### 4. Migrate from Legacy Configuration (if needed)
```bash
# Check if migration is needed
python scripts/migrate-config-xdg.py --status

# Preview migration plan
python scripts/migrate-config-xdg.py --dry-run

# Perform interactive migration
python scripts/migrate-config-xdg.py

# Or non-interactive migration
python scripts/migrate-config-xdg.py --yes
```

## 🔧 Configuration Resolution

The XDG-compliant configuration system uses a prioritized approach:

### Configuration File Resolution
1. **`$XDG_CONFIG_HOME/tmuxbot/config.yaml`** (if XDG_CONFIG_HOME is set)
2. **`$HOME/.config/tmuxbot/config.yaml`** (default XDG location)
3. **`./config.yaml`** (legacy fallback with deprecation warnings)

### Configuration Value Priority
1. **Environment Variables** (highest priority - `TMUXBOT_*` prefix)
2. **XDG Configuration File** (profile-based settings)
3. **Default Values** (lowest priority)

### XDG Base Directory Specification
TmuxBot follows the XDG Base Directory specification:
- **XDG_CONFIG_HOME**: User-specific configuration files (default: `$HOME/.config`)
- **Automatic Directory Creation**: Creates `~/.config/tmuxbot/` if needed
- **Permission Handling**: Graceful fallback for permission issues
- **Cross-Platform Support**: Works on Linux, macOS, and other Unix-like systems

## ⚙️ Key Features

### Provider-Based Architecture
- **Multiple AI Providers**: OpenAI, OpenRouter, Anthropic support
- **Per-Agent Configuration**: Different providers for different agents
- **Cost Optimization**: Automatic model mapping for cost savings
- **Fault Tolerance**: Circuit breaker pattern with fallback

### Environment Management
- **Development**: Cost-optimized with debug logging
- **Staging**: Balanced testing environment
- **Production**: Reliability-focused with monitoring

### Advanced Features
- **Cost Controls**: Daily/per-request limits with alerts
- **Performance Monitoring**: Response time and error tracking
- **Circuit Breaker**: Automatic provider failover
- **Caching**: Optional request caching for performance

## 📊 Configuration Examples

### OpenAI Only Setup
```bash
export OPENAI_API_KEY="sk-your-key"
export TMUXBOT_MODEL="openai:gpt-4o"
export TMUXBOT_USE_OPENROUTER="false"
```

### Cost-Optimized OpenRouter Setup
```bash
export OPENROUTER_API_KEY="sk-or-your-key"
export TMUXBOT_USE_OPENROUTER="true"
export TMUXBOT_ENV="development"
export TMUXBOT_COST_OPTIMIZATION="true"
```

### Production Multi-Provider Setup
```bash
export OPENAI_API_KEY="sk-your-openai-key"
export OPENROUTER_API_KEY="sk-or-your-openrouter-key"
export TMUXBOT_ENV="production"
export TMUXBOT_DAILY_LIMIT_USD="100.0"
```

## 🛠️ Environment-Specific Settings

### Development Environment
- **Cost Optimized**: Uses cheaper models (gpt-4o-mini, llama-3.1-8b)
- **Debug Logging**: Request/response logging enabled
- **Lower Limits**: $10/day, $0.25/request
- **Relaxed Security**: No HTTPS enforcement

### Production Environment
- **High Reliability**: Premium models, OpenAI preference
- **Monitoring**: Performance metrics, cost alerts
- **Higher Limits**: $100/day, $2/request
- **Strict Security**: API key validation, rate limiting

### Staging Environment
- **Balanced**: Mix of cost and quality
- **Testing**: Production-like features with cost controls
- **Moderate Limits**: $25/day, $0.5/request

## 🔍 Validation and Testing

The configuration package includes comprehensive validation:

### Automatic Checks
- ✅ Configuration file syntax validation
- ✅ Provider configuration validation
- ✅ Environment variable verification
- ✅ Provider system integration testing
- ✅ Model creation testing

### Manual Testing
```bash
# Validate all configurations
python scripts/setup-config.py --validate

# Test provider system end-to-end
python scripts/setup-config.py --test-providers

# Full configuration health check
python scripts/setup-config.py --full-check
```

## 🔐 Security Best Practices

### API Key Management
- ✅ Environment variables for secrets (never commit)
- ✅ Masked API keys in logs
- ✅ Optional API key rotation tracking
- ✅ Provider-specific key validation

### Production Security
- ✅ HTTPS enforcement option
- ✅ Rate limiting configuration
- ✅ Sensitive data logging controls
- ✅ Admin interface security

## 📈 Cost Management

### Built-in Cost Controls
- **Daily Limits**: Prevent runaway costs
- **Per-Request Limits**: Control individual request costs
- **Cost Optimization**: Automatic model downgrading in development
- **Cost Monitoring**: Real-time cost tracking and alerts

### Model Mapping for Savings
```yaml
# Development cost savings
model_mappings:
  "gpt-4o": "openai/gpt-4o-mini"  # Use mini in development
  "claude-3.5-sonnet": "meta-llama/llama-3.1-8b-instruct"  # Use cheaper alternative
```

## 🔧 Migration from Legacy

The new configuration system maintains **100% backward compatibility**:

- ✅ Existing `config.json` continues to work
- ✅ Automatic fallback to legacy `ModelFactory`
- ✅ Gradual migration path available
- ✅ No breaking changes to existing functionality

## 📚 Documentation

### Complete Documentation Package
1. **`CONFIG.md`** - Full configuration guide with examples
2. **`CONFIG-SUMMARY.md`** - This summary document
3. **`.env.template`** - Annotated environment variable template
4. **Inline Comments** - Detailed YAML configuration comments

### Usage Examples
Every configuration file includes:
- ✅ Detailed comments explaining options
- ✅ Example configurations for common scenarios
- ✅ Environment-specific examples
- ✅ Security and best practice notes

## 🔄 Migration from Legacy Configuration

### Automatic Migration Support
TmuxBot provides comprehensive migration tools for upgrading from legacy configurations:

#### Migration Detection
```bash
# Check if migration is needed
python scripts/setup-config.py --check-migration
python scripts/migrate-config-xdg.py --status
```

#### Migration Process
1. **Backup Creation**: Automatic backup of legacy configuration
2. **File Preservation**: Maintains permissions and timestamps
3. **Validation**: Verifies migrated configuration loads correctly
4. **User Confirmation**: Interactive prompts for safe migration

#### Migration Features
- ✅ **Interactive Mode**: Step-by-step migration with confirmations
- ✅ **Non-Interactive Mode**: Automated migration for scripts
- ✅ **Dry-Run Mode**: Preview migration without making changes
- ✅ **Backup Creation**: Automatic backup before migration
- ✅ **Rollback Support**: Easy restoration if needed

## 🎯 Next Steps

### For New Installations
1. **Create XDG configuration**: `python scripts/setup-config.py --create-template`
2. **Edit configuration file**: Add your API keys to `~/.config/tmuxbot/config.yaml`
3. **Validate setup**: `python scripts/setup-config.py --validate`
4. **Test configuration**: `python scripts/setup-config.py --full-check`

### For Existing Users
1. **Check migration status**: `python scripts/migrate-config-xdg.py --status`
2. **Preview migration**: `python scripts/migrate-config-xdg.py --dry-run`
3. **Migrate configuration**: `python scripts/migrate-config-xdg.py`
4. **Validate new setup**: `python scripts/setup-config.py --full-check`

---

**🎉 Your TmuxBot XDG configuration system is ready for production use!**

The XDG-compliant, profile-based architecture provides standards compliance, user-friendly management, and seamless migration from legacy configurations.