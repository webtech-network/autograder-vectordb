"""Service for splitting long texts into retrieval-friendly chunks."""

from langchain_text_splitters import RecursiveCharacterTextSplitter


class TextSplitterService:
    """Splits documents into chunks using recursive character splitting with code-aware separators."""

    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 150) -> None:
        """Initialize the text splitter.

        Args:
            chunk_size: Target size in characters for each chunk.
            chunk_overlap: Number of characters to overlap between adjacent chunks.
        """
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
        """Split text into non-empty chunks.

        Args:
            text: Input text to split.

        Returns:
            List of non-empty chunks, ordered by appearance in the original text.
        """
        return [chunk for chunk in self._splitter.split_text(text) if chunk.strip()]
