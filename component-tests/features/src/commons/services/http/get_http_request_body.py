from features.src.commons.services.file.read_file_as_str import ReadFileAsStr


class GetHttpRequestBody:

    _INSTANCE = None

    def __new__(cls):
        if cls._INSTANCE is None:
            cls._INSTANCE = super(GetHttpRequestBody, cls).__new__(cls)
        return cls._INSTANCE

    def execute(self, file_name: str, folder_name: str) -> str:
        file_path = f"resources/{folder_name}/http/request/{file_name}"
        request_body = ReadFileAsStr().execute(file_path)
        if not request_body:
            raise Exception(f"Http request body not found in file '{file_path}'")
        return request_body
