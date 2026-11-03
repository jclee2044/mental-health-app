"""Shared transport failure vocabulary, independent of feature policy."""
class InvalidProviderResponse(ValueError):
    pass

class ProviderUnavailable(Exception):
    pass

class ProviderTimeout(ProviderUnavailable):
    pass
