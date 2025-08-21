from __future__ import annotations

"""Custom Portia tool: Fetch a PDF by URL and return its text content."""

from io import BytesIO
import re
from typing import Any

import requests
from pydantic import BaseModel, Field

from portia.tool import Tool, ToolRunContext, ToolHardError

try:
	from pdfminer.high_level import extract_text  # type: ignore
except Exception as e:  # pragma: no cover - surfaced as ToolHardError at runtime
	extract_text = None  # fallback marker


class PdfToMarkdownToolSchema(BaseModel):
	"""Inputs for PdfToMarkdownTool."""

	url: str = Field(..., description="Public URL to a PDF file to read and return as plain text")


class PdfToMarkdownTool(Tool[str]):
	"""Reads a remote PDF (by URL) and returns its plain text content."""

	id: str = "pdf_to_markdown_tool"
	name: str = "PDF to Markdown Tool"
	description: str = (
		"Given a public URL to a PDF, download it and return the extracted plain text."
	)
	args_schema: type[BaseModel] = PdfToMarkdownToolSchema
	output_schema: tuple[str, str] = ("str", "Plain text extracted from the PDF")

	def run(self, _: ToolRunContext, url: str) -> str:
		if extract_text is None:
			raise ToolHardError(
				"pdfminer.six is not available. Please install 'pdfminer.six' in the environment."
			)

		# Fetch PDF bytes
		try:
			resp = requests.get(url, timeout=(10, 60), stream=True)
		except requests.RequestException as e:
			raise ToolHardError(f"Failed to fetch PDF: {e}")

		if resp.status_code != 200:
			raise ToolHardError(f"Failed to fetch PDF: HTTP {resp.status_code}")

		content_type = resp.headers.get("Content-Type", "").lower()
		# Some servers may not set header, so accept if header is OK or magic header matches
		data = resp.content
		if not ("application/pdf" in content_type or data[:5] == b"%PDF-"):
			raise ToolHardError(
				"URL did not return a PDF (unexpected content-type or header)."
			)

		# Extract text
		try:
			text = extract_text(BytesIO(data)) or ""
		except Exception as e:
			raise ToolHardError(f"Failed to extract text from PDF: {e}")
		return text.strip()

