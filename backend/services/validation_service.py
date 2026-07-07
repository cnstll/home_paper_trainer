"""Validation service for arXiv URLs and other inputs."""

import re


class ValidationService:
    """Service for validating arXiv URLs and other user inputs."""

    @staticmethod
    def validate_arxiv_url(url: str) -> tuple[bool, str | None]:
        """Validate that a URL is a valid arXiv URL.

        Valid formats:
        - https://arxiv.org/abs/2304.00001
        - https://arxiv.org/pdf/2304.00001
        - https://arxiv.org/abs/2304.00001v1
        - https://arxiv.org/pdf/2304.00001v1
        - arxiv.org/abs/2304.00001
        - arxiv.org/pdf/2304.00001

        Args:
            url: The URL to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Normalize URL by removing trailing slashes and whitespace
        url = url.strip().rstrip("/")

        # Pattern for arXiv URLs
        # Matches: arxiv.org/abs/XXXX.XXXXX or arxiv.org/pdf/XXXX.XXXXX
        # With optional version suffix like v1, v2, etc.
        pattern = r"^https?:\/\/(www\.)?arxiv\.org\/(abs|pdf)\/([a-zA-Z0-9\.]+)(v\d+)?$"

        if not re.match(pattern, url):
            # Try without protocol
            pattern_no_protocol = r"^(www\.)?arxiv\.org\/(abs|pdf)\/([a-zA-Z0-9\.]+)(v\d+)?$"
            if not re.match(pattern_no_protocol, url):
                return False, "Invalid arXiv URL. Please try again."

        return True, None

    @staticmethod
    def extract_arxiv_id(url: str) -> str | None:
        """Extract the arXiv ID from a valid arXiv URL.

        Args:
            url: A validated arXiv URL

        Returns:
            The arXiv ID (e.g., "2304.00001") or None if extraction fails
        """
        # Pattern to extract arXiv ID (without version suffix)
        # Matches the ID part after /abs/ or /pdf/ and before optional vN
        pattern = r"(?:abs|pdf)\/([a-zA-Z0-9\.]+?)(v\d+)?$"

        match = re.search(pattern, url)
        if match:
            return match.group(1)

        return None

    @staticmethod
    def normalize_arxiv_url(url: str) -> str:
        """Normalize an arXiv URL to the abs format.

        Args:
            url: An arXiv URL (abs or pdf format)

        Returns:
            Normalized URL in abs format
        """
        url = url.strip().rstrip("/")

        # Replace pdf with abs
        url = re.sub(r"(arxiv\.org)\/pdf\/", r"\1/abs/", url)

        # Ensure https protocol
        if not url.startswith("http"):
            url = "https://" + url

        return url
