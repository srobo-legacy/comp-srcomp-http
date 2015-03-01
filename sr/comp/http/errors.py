from werkzeug.exceptions import BadRequest


# 400
class UnknownMatchFilter(BadRequest):
    description = 'Unknown match filter.'

    def __init__(self, name):
        self.details = {'name': name}
