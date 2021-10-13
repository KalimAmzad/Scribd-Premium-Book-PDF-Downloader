from bs4 import BeautifulSoup
import requests

from .content.document import ScribdTextualDocument
from .content.document import ScribdImageDocument
from .content.book import ScribdBook
from .content.audiobook import ScribdAudioBook

from .pdf_converter import ConvertToPDF
import glob
from mdpdf.converter import Converter
from mdpdf import log


class Downloader:
    """
    A helper class for downloading books and documents off Scribd.

    Parameters
    ----------
    url : `str`
        A string containing path to a Scribd URL
    """

    def __init__(self, url):
        print("Initialization")
        self.url = url
        is_audiobook = self.is_audiobook()
        is_document = self.is_document()
        is_book = self.is_book()

        # if is_audiobook:
        #     is_book = False
        #     is_document = False
        # else:
        #     is_book = self.is_book()

        self._is_audiobook = is_audiobook
        self._is_book = is_book
        self._is_document = is_document

    def download(self, is_image_document=None):
        """
        Downloads books and documents from Scribd.
        Returns an object of `ConvertToPDF` class.
        """
        if self._is_audiobook:
            content = self._download_audiobook()
            return content

        if self._is_book:
            content = self._download_book()
        else:
            print("Document Downloading")
            if is_image_document is None:
                raise TypeError(
                    "The input URL points to a document. You must specify "
                    "whether it is an image document or a textual document "
                    "in the `image_document` parameter."
                )
            content = self._download_document(is_image_document)
        return content

    def _download_book(self):
        """
        Downloads books off Scribd.
        Returns an object of `ConvertToPDF` class.
        """
        book = ScribdBook(self.url)
        md_path = book.download()
        pdf_path = "{}.pdf".format(book.sanitized_title)

        # input_filename = '{}.md'.format(book.sanitized_title)
        # output_filename = '{}.pdf'.format(book.sanitized_title)
        # path_wkhtmltopdf = r'G:\Office Work\Scribd Downloader\scribd-downloader\wkhtmltox\bin\wkhtmltopdf.exe'
        # config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)

        # with open(input_filename, 'r', encoding='UTF8') as f:
        #     html_text = markdown(f.read(), output_format='html4')


        # return pdfkit.from_string(html_text, output_filename, configuration=config)
        inputs = md_path
        output = pdf_path
        if inputs:
            log.init()
            globlist = []
            for i in inputs:
                log.debug(i)
                matches = glob.glob(i)
                if matches:
                    globlist.extend(matches)
                else:
                    print(f"File not found: {i}.")
            converter = Converter(output)
            converter.convert(globlist)
        else:
            print("No input specified.")
        # return ConvertToPDF(md_path, pdf_path)

    def _download_document(self, image_document):
        """
        Downloads textual and image documents off Scribd.
        Returns an object of `ConvertToPDF` class.
        """
        if image_document:
            document = ScribdImageDocument(self.url)
        else:
            document = ScribdTextualDocument(self.url)

        content_path = document.download()
        pdf_path = "{}.pdf".format(document.sanitized_title)
        # return ConvertToPDF(content_path, pdf_path)

    def _download_audiobook(self):
        """
        Downloads audiobooks off Scribd.
        Returns a list containing local audio filepaths.
        """
        audiobook = ScribdAudioBook(self.url)
        playlist = audiobook.playlist
        if not audiobook.premium_cookies:
            print("Premium cookies not detected. Only the preview version of audiobook will be downloaded.")
        playlist.download()
        return playlist.download_paths

    def is_book(self):
        """
        Checks whether the passed URL points to a Scribd book
        or a Scribd document.
        """
        return "book" in self.url and "audiobook" not in self.url
        # response = requests.get(self.url)
        # soup = BeautifulSoup(response.text, "html.parser")
        # content_class = soup.find("body")["class"]
        # matches_with_book = content_class[0] == "autogen_class_views_layouts_book_web"
        # return matches_with_book

    def is_audiobook(self):
        """
        Checks whether the passed URL points to a Scribd audiobook.
        """
        return "audiobook" in self.url

    def is_document(self):
        """
        Checks whether the passed URL points to a Scribd audiobook.
        """
        # print("Document Downloading") if "document" in self.url

        return "document" in self.url
