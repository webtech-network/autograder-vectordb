from features.src.commons.services.file.read_file_as_str import ReadFileAsStr


class GetExpectedHttpResponseBody:

    _INSTANCE = None

    def __new__(cls):
        if cls._INSTANCE is None:
            cls._INSTANCE = super(GetExpectedHttpResponseBody, cls).__new__(cls)
        return cls._INSTANCE

    def execute(self, file_name: str, folder_name: str) -> str:
        file_path = f"resources/{folder_name}/http/response/{file_name}"
        expected_response_body = ReadFileAsStr().execute(file_path)
        if not expected_response_body:
            raise Exception(f"Expected response body not found in file '{file_path}'")
        return expected_response_body
