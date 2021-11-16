class Topic:
    def __init__(self, name) -> None:
        # Topic ID
        self.name = name
        self.num_msg = 0
        # Arrays/Dictionary to save information about the topic
        self.subs = []
        self.messages = {} # Key --> message ID; Value --> Message content
        self.subs_last_message = {} # Key --> sub ID; Value --> Message ID

        # Views to help to analyse the dictionaries
        self.messages_stored_view = self.messages.keys()
        self.last_message_view = self.subs_last_message.values()

        print('Topic ' + name + ' created successfully!')

    # Adds a message to this topic
    async def add_message(self, message):
        print("Current lenght: " + str(self.num_msg))
        self.num_msg += 1
        self.messages[self.num_msg] = message
        print("Added message. New len: "+ str(self.num_msg))

    # Removes all messages that have already been sent
    def remove_message(self):
        first_message_id = min(list(self.messages_stored_view))
        subs_last_mesage_id = min(list(self.subs_last_message))

        if first_message_id < subs_last_mesage_id:
            self.messages.pop(first_message_id)
            return self.remove_message()

    # Add a subscriber to this topic
    def add_sub(self, sub_id):
        self.subs.append(sub_id)

    # Remove a subscriber to this topic
    def remove_sub(self, sub_id):
        self.subs.remove(sub_id)