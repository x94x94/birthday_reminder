class UserState:
    def __init__(self, user_id):
        self.user_id = user_id
        self.current_function = ''
        self.current_person = ''
        self.people_list = {}
        self.current_name = ''
        self.current_status = ''
