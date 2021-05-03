class PostCustomerSerializer:

    def __init__(self, **kwargs):
        self.keys = [
            'first_name',
            'last_name',
            'email',
            'zip_code'
        ]
        self.valid = True
        if not all(item in [*kwargs] for item in self.keys):
            self.valid = False
        if '@' not in kwargs['email']:
            self.valid = False
        if len(str(kwargs['zip_code'])) != 5:
            self.valid = False
        self.values = kwargs

    def is_valid(self):
        return self.valid

    def get_values(self):
        return self.values


class PatchCustomerSerializer:

    def __init__(self, **kwargs):
        self.keys = [
            'city',
            'state',
        ]
        self.valid = True
        if not all(item in self.keys for item in [*kwargs]):
            self.valid = False
        self.values = kwargs

    def is_valid(self):
        return self.valid

    def get_values(self):
        return self.values

