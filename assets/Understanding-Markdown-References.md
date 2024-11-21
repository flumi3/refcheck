# Understanding Markdown References

Markdown supports various ways to reference external content such as links, images, and local files. This guide will
explain the different types of references you can use in your Markdown files. This document is both a tutorial and a
test case for the `refcheck` tool.

## HTTP/HTTPS Links

Markdown allows you to include links to external websites. You can write an inline link using square brackets for the
link text and parentheses for the URL.

Here are two examples:

- A link to [Google](https://www.google.com) using HTTPS.
- A reference to [Google](http://www.google.com) using HTTP.

## Image References

You can embed images in Markdown by using an exclamation mark followed by alt text in square brackets and the image
path or URL in parentheses. Images can be referenced using either absolute or relative paths:

- An absolute path image: ![Some Logo](/img/image.png)
- A relative path image: ![Sample Image](img.png)

## Local File References

Markdown links can also point to local files. These links ensure that the referenced files are accessible within your
project's directory structure:

- A reference to a Python script: [Main Python Script](src/main.py)
- A link to a user guide Markdown file: [User Guide](docs/user_guide.md)
- An absolute path reference: [Good Documentation](/project/docs/good-doc.md)

## Markdown Links with Headers

Sometimes, you might want to link to a specific section within a Markdown file. This is done by adding a hash symbol
followed by the header text:

- A link to installation instructions in another file: [Installation Instructions](other-directory/README.md#installation-instructions)
- A getting-started guide link: [Getting Started](/path/to/README.md#getting-started)
- A header link with spaces: [Markdown Links with Headers](#markdown-links-with-headers)

## HTML Links

HTML tags can be used within Markdown files for additional formatting capabilities, including links:

- HTML link using double quotes: <a href="http://example.com">Example Link</a>
- HTML link using single quotes: <a href='http://example.com'>Another Example Link</a>

## HTML Images

Similarly, HTML can be used to embed images. This is useful when you need more control over the image attributes:

- Remote HTML image: <img src="https://www.openai.com/logo.png" alt="OpenAI Logo">
- Absolute path HTML image: <img src="/assets/img.png" alt="Absolute Path Image">
- Relative path HTML image: <img src="image.png" alt="Relative Path Image">

## Inline Links

For including raw URLs in Markdown, you can simply enclose the URL in angle brackets:

- Inline HTTP link: <http://example.com>
- Inline HTTPS link: <https://example.com>
- Inline link usage in a sentence: This <http://example.com> contains all necessary explanations.

## Footnote Links

Markdown also supports footnotes for references which can be declared at the bottom and used throughout the document:

- Example reference: [1]: <http://example.com>
- In-text usage: [Example Link Text][1]

## Footnotes

Footnotes can be used to include additional information or references at the end of a document:

Here is a footnote reference[^1].

- [^1]: <http://example.com>

## Raw Links

Sometimes, you may have plain URLs in your text that are not part of a Markdown link syntax:

- Direct link to a resource: http://example.com
- Standalone raw link: http://example.com

## Additional File Types

Markdown allows linking to various types of files, not just Markdown or images:

- A reference to a PDF file: [PDF File](files/sample.pdf)

## Nested Links

References can be nested within lists or blockquotes:

- Nested within a list:
  - A reference to [OpenAI](https://www.openai.com)
  - Another [example link](http://example.com)

> Nested within a blockquote:
>
> - A reference to [example link](http://example.com)

## Links in Code Blocks

Code blocks often contain references that should not be checked:

```Markdown
# Example Code Block
[Link](http://example.com)
```
