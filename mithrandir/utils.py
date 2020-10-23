def Validator(some_type):
    def wrapped(data):
        if not isinstance(data, some_type):
            raise TypeError("Invalid type > ", data, "not equals", some_type)
        return data

    return wrapped
