class MockEventsView:
    def __init__(self):
        self.events = []
        self.message = ''

    def show_all_events(self, all_events):
        self.events = all_events

    def select_event_to_modify(self):
        return '1'

    def not_support(self, support):
        self.message = 'not_support'

    def no_event_to_modify(self):
        self.message = 'no_event'

    def confirm_support_choice(self, support):
        return 'oui'

    def modification_success_message(self):
        self.message = 'success_modification'

    def creation_success_message(self):
        self.message = 'success_creation'

    def get_event_contract(self, contract):
        return '1'

    def invalid_user_choice(self, choice):
        self.message = 'invalid_choice'

    def get_date_time(self, date, time):
        return '13/03/2024', '13:45'

    def get_location(self):
        return '56 Rue de la Trinité'

    def get_attendees(self):
        return '56'

    def get_notes(self):
        return 'Pas de notes'
