"""Reusable provider-facing adapters.

Import a concrete module (for example ``providers.results`` or
``providers.sdk``) so importing one provider concern does not eagerly load the
other SDK's dependencies.
"""
