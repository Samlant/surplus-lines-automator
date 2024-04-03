import ctypes
from pathlib import Path
from model.carriers.base import Carrier


class OutputDirNotSet(Exception):
    """Exception for when trying to process a PDF without a save location set."""

    def __init__(self, *args: object) -> None:
        super().__init__(*args)
        message = "There is no save location set currently.  Please select a location using the window and re-drag your file to continue."
        super().__init__(message)

class DocException(Exception):
    """Base exception for PDF-related errors when running the Surplus Lines automator.

    Attributes:
        doc_path -- path to the submitted PDF
        file_name -- name and extension of the PDF file
        doc_path -- path to the submitted PDF
    """

    def __init__(self, doc_path) -> None:
        self.doc_path = doc_path
        self.file_name = doc_path.name
        self.doc_dir = doc_path.parent

    def save_msg(self, message):
        super().__init__(message)


class DocError(DocException):
    def __init__(self, doc_path) -> None:
        super().__init__(doc_path)
        message = f"Surplus Lines Automator exiting due to a DocException that the user decided to withdraw from. The file submitted was '{self.file_name}' located in '{self.doc_dir}'."
        super().save_msg(message)


class SurplusLinesNotApplicable(DocException):
    """Exception raised for docs submitted for stamping, but SL doesn't apply; either because the offer isn't written on Surplus Lines or we as an agency don't charge Surplus Lines taxes/fees for this doc.

    Attributes:
        carrier_obj -- the carrier object created from the PDF
        message -- explanation of the error
    """

    def __init__(self, carrier_obj: Carrier):
        super().__init__(carrier_obj.pdf_path)
        self.message = f"This program detected that surplus lines taxes do not apply to this document from {carrier_obj.name}. If this is incorrect and you are certain that they do,  you may override this.  Otherwise, do not proceed or check with someone else first. As reference, the file name is: {self.file_name}"
        super().save_msg(self.message)


class DocParseError(DocException):
    """Exception raised for docs that cannot be parsed. This is a base parse error used if no other parsing error category fits.

    Attributes:
        carrier_obj -- the carrier object created from the PDF
        message -- explanation of the error
    """

    def __init__(self, carrier_obj: Carrier | Path):
        if isinstance(carrier_obj, Path):
            super().__init__(carrier_obj)
            self.message = f"The carrier that provided this document could not be identified.  Perhaps this carrier's file structure has changed enough to not allow the program to detect the correct carrier. As reference, the file name is: {self.file_name}, and it's located in this folder: {self.doc_dir}"
            super().save_msg(self.message)
        else:
            super().__init__(carrier_obj.pdf_path)
            self.message = f"The document could not be parsed correctly, or {carrier_obj.name}'s file structure has changed enough to not allow the program to detect the correct type (binder, quote, etc.). As reference, the file name is: {self.file_name}, and it's located in this folder: {self.doc_dir}"
            super().save_msg(self.message)


class UnsupportedDocType(DocException):
    """Exception raised for docs whose type is not currently supported/implemented.

    Attributes:
        carrier_obj -- the carrier object created from the PDF
        doc_type -- type of document (quote, binder, policy, ap, rp, cancel)
        message -- explanation of the error
    """

    def __init__(self, carrier_obj: Carrier):
        super().__init__(carrier_obj.pdf_path)
        self.message = f"The program has not yet implemented functionality for the document that has been submitted ({self.file_name}), from {carrier_obj.name}.  As of now, please stamp the doc manually. As reference, the doc was detected to be the following type: {carrier_obj.user_doc_type}. The file is located in this folder: {self.doc_dir}"
        super().save_msg(self.message)


class UnknownDocType(DocException):
    """Exception raised for docs whose type cannot be detected (ie. quote, binder, policy, ap, rp, or cancel).

    Attributes:
        carrier_obj -- the carrier object created from the PDF
        doc_type -- type of document (quote, binder, policy, ap, rp, cancel)
        message -- explanation of the error
    """

    def __init__(self, carrier_obj: Carrier):
        super().__init__(carrier_obj.pdf_path)
        self.message = f"The program cannot detect the type of document that has been submitted ({self.file_name}), from {carrier_obj.name}.  This could be caused by {carrier_obj.name}'s file structure changing enough to not allow the program to detect the correct type (binder, quote, etc.).  For now, please stamp the doc manually. As reference, the doc is located in this folder: {self.doc_dir}"
        super().save_msg(self.message)


def spawn_message(title, message, style) -> int:
    """Spawns a message to the user"""
    return ctypes.windll.user32.MessageBoxW(
        0,
        message,
        title,
        style,
    )


# pdf = Path.joinpath(Path.cwd().parent / "tests" / "carriers" / "kemah" / "quote.pdf")
# pdf.exists()
# try:
#     raise DocParseError(pdf, "Kemah")
# except DocParseError as e:
#     print(str(e))
