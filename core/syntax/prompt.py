class Prompt:
    def __init__(self):
        self.message = "\n(parse)-•-(bunny)$> "  # The prompt message 

    def get_message(self):
        """Returns the current message."""
        return self.message

    def set_message(self, new_message):
        """Sets a new message for the prompt."""
        self.message = new_message

    def get_input(self):
        """Displays the prompt message and gets user input."""
        user_input = input(self.get_message())  # Display the message and wait for user input
        return user_input
