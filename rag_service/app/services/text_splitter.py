from langchain_text_splitters import RecursiveCharacterTextSplitter


class TextSplitterService:
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 150) -> None:
        self._splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=[
                "\n```",
                "\n## ",
                "\n### ",
                "\n\n",
                "\n",
                " ",
                "",
            ],
        )

    def split_text(self, text: str) -> list[str]:
        return [chunk for chunk in self._splitter.split_text(text) if chunk.strip()]
