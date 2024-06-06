import re
class Instruction:
    """An instruction template."""

    def __init__(self, instruction_id):
        self.id = instruction_id

    def build_description(self, **kwargs):
        raise NotImplementedError("`build_description` not implemented.")

    def get_instruction_args(self):
        raise NotImplementedError("`get_instruction_args` not implemented.")

    def get_instruction_args_keys(self):
        raise NotImplementedError("`get_instruction_args_keys` not implemented.")

    def check_following(self, value):
        raise NotImplementedError("`check_following` not implemented.")

class DateFormatChecker(Instruction):
    """Checks that the response contains a date in the specified format."""

    def build_description(self, *, date_format: str = 'YYYY-MM-DD'):
        """Build the instruction description.

        Args:
            date_format: A string representing the date format (default is 'YYYY-MM-DD').

        Returns:
            A string representing the instruction description.
        """
        self._date_format = date_format
        self._description_pattern = (
            "Your response should contain a date in the format {date_format}."
        )
        return self._description_pattern.format(date_format=self._date_format)

    def get_instruction_args(self):
        """Returns the keyward args of `build_description`."""
        return {"date_format": self._date_format}

    def get_instruction_args_keys(self):
        """Returns the args keys of `build_description`."""
        return ["date_format"]

    def check_following(self, value):
        """Checks if the response contains a date in the specified format.

        Args:
            value: A string representing the response.

        Returns:
            True if the response contains a date in the specified format; otherwise False.
        """
        if self._date_format == 'YYYY-MM-DD':
            pattern = r'\b\d{4}-\d{2}-\d{2}\b'
        else:
            raise ValueError("Unsupported date format")
        return re.search(pattern, value) is not None
