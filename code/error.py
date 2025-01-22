class ProjError(Exception):
    pass


class CustomError(ProjError):
    def __init__(self, *args, **kwargs):
        super().__init__(*args)
        self.custom_kwarg = kwargs.get('custom_kwarg')