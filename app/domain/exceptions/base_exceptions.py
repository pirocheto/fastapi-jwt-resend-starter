class AppError(Exception):
    def __init__(self, code: str, detail: str, status_code: int) -> None:
        self.status_code = status_code
        self.code = code
        self.detail = detail
        super().__init__(self.detail)
