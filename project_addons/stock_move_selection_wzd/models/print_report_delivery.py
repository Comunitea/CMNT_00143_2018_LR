from odoo import models
import base64
import os
import logging
import tempfile
from contextlib import closing
from PyPDF2 import PdfFileWriter, PdfFileReader

_logger = logging.getLogger(__name__)


class IrActionsReport(models.Model):

    _inherit = "ir.actions.report"

    def _merge_pdf(self, documents):
        """Merge PDF files into one.
        :param documents: list of path of pdf files
        :returns: path of the merged pdf
        """
        writer = PdfFileWriter()
        streams = []
        for document in documents:
            pdfreport = open(document, 'rb')
            streams.append(pdfreport)
            reader = PdfFileReader(pdfreport)
            for page in range(0, reader.getNumPages()):
                writer.addPage(reader.getPage(page))

        merged_file_fd, merged_file_path = tempfile.mkstemp(
            suffix='.html', prefix='report.merged.tmp.')
        with closing(os.fdopen(merged_file_fd, 'wb')) as merged_file:
            writer.write(merged_file)

        for stream in streams:
            stream.close()

        return merged_file_path

    def render_qweb_pdf(self, res_ids=None, data=None):
        if self.report_name == "stock_move_selection_wzd.delivery_batch_view":
            pdfdatas = []
            temporary_files = []
            for res_id in res_ids:
                delivery_id = self.env['stock.batch.delivery'].browse(res_id)
                res = super().render_qweb_pdf(res_id, data)
                pdfdatas.append(res[0])
                batch_ids = delivery_id.batch_ids.ids
                domain = [('name', '=', 'Grupo de albaranes')]
                group = self.search(domain, limit=1)
                batch_pdf = group.render_qweb_pdf(batch_ids, {})
                pdfdatas.append(batch_pdf[0])
                moves = delivery_id.move_lines.filtered(
                    lambda x: x.quantity_done != 0.00 and x.product_tmpl_id.adr_idnumonu)
                if moves:
                    domain = [('name', '=', 'Batch Delivery ADR Report')]

                    group = self.search(domain, limit=1)
                    batch_pdf = group.render_qweb_pdf(res_id, {})
                    pdfdatas.append(batch_pdf[0])
            if pdfdatas:
                pdfdocuments = []
                for pdfcontent in pdfdatas:
                    pdfreport_fd, pdfreport_path = tempfile.\
                        mkstemp(suffix='.pdf', prefix='report.tmp.')
                    temporary_files.append(pdfreport_path)
                    with closing(os.fdopen(pdfreport_fd, 'wb')) as pdfr:
                        pdfr.write(pdfcontent)
                    pdfdocuments.append(pdfreport_path)
                entire_report_path = self._merge_pdf(pdfdocuments)
                temporary_files.append(entire_report_path)
                with open(entire_report_path, 'rb') as pdfdocument:
                    content = pdfdocument.read()
                # Manual cleanup of the temporary files
                for temporary_file in temporary_files:
                    try:
                        os.unlink(temporary_file)
                    except (OSError, IOError):
                        _logger.error('Error when trying to remove '
                                      'file %s' % temporary_file)
                return content, 'pdf'

        return super().render_qweb_pdf(res_ids, data)