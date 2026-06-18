from django.core.exceptions import ValidationError
import regex as re
class vali:
    def validate(self, password,user=None):
        leni=len(password)
        total_char=sum(char.isalpha() for char in password)
        pattern = r'^(?=.*[A-Z])(?=(?:.*?\d){2})(?=.*?[!@#$%^&*(),.?":{}|<>]).+$'


        if password.startswith(' ') or password.endswith(' '):
            raise ValidationError(
                "The password cannot start or end with spaces.",
                code='password_spaces',
            )
        if not  re.match(pattern,password):
            raise ValidationError(
                "your password must contain 2 numbers and one special char and atleast one uppercase letter also"

            )
        if leni<8 or total_char<5:
            raise ValidationError(
                "your password must contain at least  8 characters with one uppercase, 1 special character and 2 numbers"

            )

    def get_help_text(self):
        return "Your password must be at least 8 characters long, with atleast 5 alphabets including contain atleast 1 uppercase letter, 1 special character, 2 numbers, and cannot start or end with spaces."
