class RoleNotValid(Exception):
    def __init__(self, role: str):
        self.message = f"{role} is not a valid role."
        super().__init__(self.message)