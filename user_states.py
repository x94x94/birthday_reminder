class UserState:
    def __init__(self, user_id):
        self.user_id = user_id
        self.current_function = ''
        self.current_person = ''
        self.people_list = {}
        self.current_name = ''
        self.current_status = ''
        #self.profile = None

    def setCurrent_function(self, current_function):
        self.current_function = current_function

    def setCurrent_person(self, current_person):
        self.current_person = current_person

    def setPeople_list(self, people_list):
        self.people_list = people_list

    def setCurrent_name(self, current_name):
        self.current_name = current_name

    def setCurrent_status(self, current_status):
        self.current_status = current_status

    # def setUserProfile(self, profile):
    #     self.profile = profile