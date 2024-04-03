import fitz
from pathlib import Path
import logging

from helper import FSL_DOC_PATH


log = logging.getLogger(__name__)


class DocFiller:
    def __init__(self, output_dir) -> None:
        self.output_dir = output_dir

    def process_doc(
        self, form_data: dict[str, float | str], stamp_num: int
    ) -> list[Path]:
        """Using form data , this opens and fills in a PDF stamp page,  then saves the file to a temp location.

        Args:
            form_data (dict[str, float  |  str]): collected by carrier obj and web response.
            stamp_num (int): indicates whether it's the first stamp or the second one; ensures any relevant existing stamps are not overwritten.

        Returns:
            list[Path]: Paths to the stamp files--to be combined later.
        """
        with fitz.open(FSL_DOC_PATH) as doc:
            out = fitz.open()
            for page in doc:  # Iterate through each page
                widgets = page.widgets()  # Get the form fields
                for widget in widgets:  # Iterate through the form fields
                    if widget.field_name not in form_data.keys():
                        pass
                    else:
                        widget.field_value = form_data[widget.field_name]
                        widget.update()  # Update the widget with the new value
                w, h = page.rect.br  # page width / height taken from bottom right point coords
                outpage = out.new_page(width=w, height=h)  # out page has same dimensions
                pix = page.get_pixmap(dpi=150)  # set desired resolution
                outpage.insert_image(page.rect, pixmap=pix)
            stamp_file_name = f"temp_stamp{stamp_num}.pdf"
            stamp_path = Path.cwd() / stamp_file_name
            log.debug(
                msg="The new temp stamp name is: {0}, and the file location is: {1}".format(
                    stamp_file_name, stamp_path
                ),
                exc_info=1,
            )
            out.save(filename=stamp_path, garbage=3, deflate=True)
        return stamp_path

    def combine_stamps_into_pdf(
        self,
        user_doc_path: Path,
        stamps: list[Path],
        insert_index: int,
    ) -> Path:
        user_doc = fitz.open(user_doc_path)
        insert_index -= 1
        for stamp in stamps:
            insert_index += 1
            log.debug(
                msg="Opening the created stamp file, located at {0}, and combining it with the user's PDF at page index: {1}.  The list of all created stamps is: {2}".format(
                    str(user_doc_path), insert_index, stamps
                ),
                exc_info=1,
            )
            stamp_doc = fitz.open(stamp)
            log.debug(
                msg="Opened the stamp file as: {0}".format(stamp_doc),
                exc_info=1,
            )
            user_doc.insert_pdf(
                stamp_doc, from_page=0, to_page=0, start_at=insert_index
            )
            log.debug(
                msg="Inserted the stamp into the user's doc.",
                exc_info=1,
            )
            stamp_doc.close()
            log.debug(
                msg="Closed the stamp file. Now creating the finalized file's name and path.",
                exc_info=1,
            )
        new_file_name = user_doc_path.stem + "__stamped.pdf"
        new_file_path = Path(self.output_dir) / new_file_name
        log.debug(
            msg="The stamped doc's name is: {0}, and its file location is: {1}".format(
                new_file_name, new_file_path
            ),
            exc_info=1,
        )
        if new_file_path.exists():
            log.debug(
                msg="File path already exists... Deleting.",
                exc_info=1,
            )
            new_file_path.unlink()
            log.debug(
                msg="Deleted file.",
                exc_info=1,
            )
        user_doc.save(new_file_path)
        user_doc.close()
        log.debug(
            msg="Saved and closed the stamped file.",
            exc_info=1,
        )
        return str(new_file_path)
