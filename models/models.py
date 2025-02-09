class User:
    def __init__(self, user_id, username, password):
        self.id = user_id
        self.username = username
        self.password = password

class Idea:
    def __init__(self, idea_id, type, description, user_id):
        self.id = idea_id
        self.type = type
        self.description = description
        self.user_id = user_id