class User:
    def __init__(self, id, email, firstName):
        self.id = id
        self.email = email
        self.username = firstName

    def __repr__(self):
        return f'<User: {self.email}>'

