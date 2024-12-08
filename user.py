class User():
    def __init__(self) -> None:
        self.__username: str = None
        self.__password: str = None
    
    def get_username(self) -> str:
        return self.__username
    
    def get_password(self) -> str:
        return self.__password

    def set_username(self, username: str) -> None | str:
        self.__username = username
    
    def set_password(self, password: str) -> None | str:
        self.__password = password
    
