
class ReadFileAsStr:
    """
    Class to read a file as a string.
    """

    _INSTANCE = None

    def __new__(cls):
        if cls._INSTANCE is None:
            cls._INSTANCE = super(ReadFileAsStr, cls).__new__(cls)
        return cls._INSTANCE

    def execute(self, file_path: str) -> str:
        with open(file=file_path, mode="r", encoding="utf-8") as file:
            return file.read()
