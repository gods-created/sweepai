class UnicornException(Exception):
    def __init__(
        self,
        status: int,
        err_description: str
    ):
        self.status = status
        self.err_description = err_description