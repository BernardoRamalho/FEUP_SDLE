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
        self.messages[self.num_msg] = message
        self.num_msg += 1

    # Removes all messages that have already been sent
    def remove_message(self):
        if len(self.messages_stored_view) == 0:
            return
            
        first_message_id = min(self.messages_stored_view)
        subs_last_mesage_id = min(self.last_message_view)

        if first_message_id < subs_last_mesage_id:
            self.messages.pop(first_message_id)
            return self.remove_message()

    # Retrieves a message to send to a subscriber
    def get_message(self, sub_id):
        if sub_id not in self.subs:
            print('Subscriber not subscribed to topic ' + self.name)
            return "Error"

        message_id = self.subs_last_message[sub_id]

        if message_id == self.num_msg:
            print("No message for subscriber.")
            return "Null"

        self.subs_last_message[sub_id] = message_id + 1
        message = self.messages[message_id]
        print('Got message: ' + message)
        self.remove_message()
        print(self.messages)
        print(self.subs_last_message)
        return message


    # Add a subscriber to this topic
    def add_sub(self, sub_id):
        if sub_id in self.subs:
            print("Subscriber " + sub_id + " already subscribed to topic " + self.name)
            return

        self.subs.append(sub_id)
        self.subs_last_message[sub_id] = self.num_msg

    # Remove a subscriber to this topic
    def remove_sub(self, sub_id):
        if sub_id not in self.subs:
            print("Subscriber " + sub_id + " already unsubscribed to topic " + self.name)
            return

        self.subs.remove(sub_id)
        self.subs_last_message.pop(sub_id)

    def print_info(self):
        print(self.messages)
        print(self.subs)