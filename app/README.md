PDF outline extractor 

Millions of PDF documents exist everywhere—from research papers, reports, manuals to user guides. But computers struggle to understand the structure inside these files, like where chapters, sections, or headings start. This project helps solve that problem by automatically extracting the structured outline of any PDF document. It identifies the document’s title, the headings at different levels (H1, H2, H3), and the page numbers where they appear. It outputs this information in a clean JSON format that can be used for building table-of-contents, better document navigation, search, or intelligent systems.

Why does this matter?
Most software treats PDFs as plain blobs of text. Humans, however, read by structure—titles, sections, subsections, and bullet points. Giving machines this semantic outline enables smarter applications such as:

Semantic search engines that jump to the right section

Document summarizers that understand content hierarchy

Recommendation systems pointing to relevant chapters

Easier navigation interfaces and readers

This project offers a lightweight, efficient approach to teaching computers “how to see” document structure.

What is my solution?
I created a Python program that:

Reads text from PDFs, capturing not only the words but also the font properties like size and boldness.

Infers heading levels, by analyzing font sizes and text styles — bigger and bolder text is usually a heading.

Builds a hierarchical outline tree, nesting subheadings under their parents.

Cleans and merges content so that label-description pairs become single lines, bullets are grouped, and explanatory text is attached properly.

Detects the document’s main language using a small language detection library.

Processes all PDFs automatically from an input folder and saves the extracted outlines as JSON files in an output folder.

Runs efficiently offline, needing no Internet or large machine learning models.

What libraries are used?
PyMuPDF (fitz): To extract text spans and font metadata from PDFs with precision and speed.

langdetect: To detect the predominant language of the document, helping multi-language support.

Python Standard Libraries: Such as json, pathlib, and collections to manage files, data structures, and counters.

All these are lightweight and installable through pip.

Step-by-step: How does it work?
Extract Text with Font Info:
Load the PDF, extract text per page, capturing font size, boldness, and position using PyMuPDF.

Infer Headings:
Count common font sizes to prioritize. Assume largest fonts represent H1, next largest H2, etc. Use boldness and length heuristics to confirm.

Create Outline Tree:
Starting from top-level headings, nest smaller headings as children. Recognize bullet points by their symbols and group them.

Post-process Outline:
Merge nearby label-description pairs to avoid fragmented lines, group bullets into arrays, and attach continuation lines as descriptions for clarity.

Language Detection:
Use sampled text from the document to detect language and store this metadata.

File Handling:
Process every PDF file inside the input folder. For every PDF, save a JSON outlining structure in the output folder with the same base filename.

Locally (without Docker):
Install required libraries:

pip install pymupdf langdetect

Find JSON outline files saved in the output folder created alongside.

Using Docker:

****   docker build --platform linux/amd64 -t llm-extractor .

Run the container:

****   docker run --rm -v "$(pwd)/input":/app/input:ro -v "$(pwd)/output":/app/output --network none llm-extractor

Processed JSON outlines will be available inside output folder.

Example output format
json
{
  "title": "Sample Document Title",
  "language": "en",
  "outline": [
    {
      "level": "H1",
      "text": "Introduction",
      "page": 1,
      "children": [
        {
          "level": "H2",
          "text": "Background",
          "page": 2,
          "description": "More details about the background."
        }
      ]
    }
  ]
}
Why this approach?
Simple yet effective: Uses lightweight heuristics rather than heavy models.

Language-agnostic: Works with multiple scripts since font size and style clues are universal.

Scalable: Processes multiple PDFs automatically.

Offline: No internet or external API calls, great for privacy and speed.

Docker-ready: Easy to deploy and run reproducibly anywhere.