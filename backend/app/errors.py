"""Framework-free errors shared by independently installable features."""
class ValidationError(ValueError):
    def __init__(self, fields):
        self.fields = fields
        super().__init__("Check the highlighted fields.")
