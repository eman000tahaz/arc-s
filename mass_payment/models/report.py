# -*- encoding: UTF-8 -*

from openerp import api, models, _
from odoo.tools import config
from odoo.sql_db import TestCursor
from odoo.exceptions import UserError

import logging
import lxml.html
import os

from functools import partial

_logger = logging.getLogger(__name__)


class Report(models.Model):
    _inherit = 'report'

    @api.model
    def get_pdf(self, docids, report_name, html=None, data=None):
        """This method generates and returns pdf version of a report.
        """

        if self._check_wkhtmltopdf() == 'install':
            # wkhtmltopdf is not installed
            # the call should be catched before (cf /report/check_wkhtmltopdf) but
            # if get_pdf is called manually (email template), the check could be
            # bypassed
            raise UserError(_("Unable to find Wkhtmltopdf on this system. The PDF can not be created."))

        # As the assets are generated during the same transaction as the rendering of the
        # templates calling them, there is a scenario where the assets are unreachable: when
        # you make a request to read the assets while the transaction creating them is not done.
        # Indeed, when you make an asset request, the controller has to read the `ir.attachment`
        # table.
        # This scenario happens when you want to print a PDF report for the first time, as the
        # assets are not in cache and must be generated. To workaround this issue, we manually
        # commit the writes in the `ir.attachment` table. It is done thanks to a key in the context.
        context = dict(self.env.context)
        if not config['test_enable']:
            context['commit_assetsbundle'] = True

        # Disable the debug mode in the PDF rendering in order to not split the assets bundle
        # into separated files to load. This is done because of an issue in wkhtmltopdf
        # failing to load the CSS/Javascript resources in time.
        # Without this, the header/footer of the reports randomly disapear
        # because the resources files are not loaded in time.
        # https://github.com/wkhtmltopdf/wkhtmltopdf/issues/2083
        context['debug'] = False

        if html is None:
            html = self.with_context(context).get_html(docids, report_name, data=data)

        # The test cursor prevents the use of another environnment while the current
        # transaction is not finished, leading to a deadlock when the report requests
        # an asset bundle during the execution of test scenarios. In this case, return
        # the html version.
        if isinstance(self.env.cr, TestCursor):
            return html

        html = html.decode('utf-8')  # Ensure the current document is utf-8 encoded.

        # Get the ir.actions.report.xml record we are working on.
        report = self._get_report_from_name(report_name)
        # Check if we have to save the report or if we have to get one from the db.
        save_in_attachment = self._check_attachment_use(docids, report)
        # Get the paperformat associated to the report, otherwise fallback on the company one.
        if not report.paperformat_id:
            user = self.env['res.users'].browse(self.env.uid)  # Rebrowse to avoid sudo user from self.env.user
            paperformat = user.company_id.paperformat_id
        else:
            paperformat = report.paperformat_id

        # Preparing the minimal html pages
        headerhtml = []
        contenthtml = []
        footerhtml = []
        irconfig_obj = self.env['ir.config_parameter'].sudo()
        base_url = irconfig_obj.get_param('report.url') or irconfig_obj.get_param('web.base.url')

        # Minimal page renderer
        view_obj = self.env['ir.ui.view']
        reportid = False
        render_minimal = partial(view_obj.with_context(context).render_template, 'report.minimal_layout')

        # The received html report must be simplified. We convert it in a xml tree
        # in order to extract headers, bodies and footers.
        try:
            root = lxml.html.fromstring(html)
            match_klass = "//div[contains(concat(' ', normalize-space(@class), ' '), ' {} ')]"

            for node in root.xpath(match_klass.format('header')):
                body = lxml.html.tostring(node)
                header = render_minimal(dict(subst=True, body=body, base_url=base_url))
                headerhtml.append(header)

            for node in root.xpath(match_klass.format('footer')):
                body = lxml.html.tostring(node)
                footer = render_minimal(dict(subst=True, body=body, base_url=base_url))
                footerhtml.append(footer)

            for node in root.xpath(match_klass.format('page')):
                # Previously, we marked some reports to be saved in attachment via their ids, so we
                # must set a relation between report ids and report's content. We use the QWeb
                # branding in order to do so: searching after a node having a data-oe-model
                # attribute with the value of the current report model and read its oe-id attribute
                if docids and len(docids) == 1:
                    reportid = docids[0]
                else:
                    oemodelnode = node.find(".//*[@data-oe-model='%s']" % report.model)
                    if oemodelnode is not None:
                        reportid = oemodelnode.get('data-oe-id')
                        if reportid:
                            reportid = int(reportid)
                    else:
                        reportid = False

                # Extract the body
                body = lxml.html.tostring(node)
                reportcontent = render_minimal(dict(subst=False, body=body, base_url=base_url))

                contenthtml.append(tuple([reportid, reportcontent]))

        except lxml.etree.XMLSyntaxError:
            contenthtml = []
            contenthtml.append(html)
            save_in_attachment = {}  # Don't save this potentially malformed document

        # Get paperformat arguments set in the root html tag. They are prioritized over
        # paperformat-record arguments.
        specific_paperformat_args = {}
        for attribute in root.items():
            if attribute[0].startswith('data-report-'):
                specific_paperformat_args[attribute[0]] = attribute[1]
        if reportid and report_name == 'mass_payment.report_checkbook':
            doc = self.env[report.model].browse(reportid)
            specific_paperformat_args['data-report-margin-top'] = doc.journal_id.top_margin
            specific_paperformat_args['data-report-margin-left'] = doc.journal_id.left_margin
            specific_paperformat_args['data-report-margin-right'] = doc.journal_id.right_margin
            specific_paperformat_args['data-report-margin-bottom'] = doc.journal_id.bottom_margin

        # Run wkhtmltopdf process
        return self._run_wkhtmltopdf(
            headerhtml, footerhtml, contenthtml, context.get('landscape'),
            paperformat, specific_paperformat_args, save_in_attachment,
            context.get('set_viewport_size'),
        )

    def _build_wkhtmltopdf_args(self, paperformat, specific_paperformat_args=None):
        """Build arguments understandable by wkhtmltopdf from a report.paperformat record.

        :paperformat: report.paperformat record
        :specific_paperformat_args: a dict containing prioritized wkhtmltopdf arguments
        :returns: list of string representing the wkhtmltopdf arguments
        """
        command_args = []
        if paperformat.format and paperformat.format != 'custom':
            command_args.extend(['--page-size', paperformat.format])

        if paperformat.page_height and paperformat.page_width and paperformat.format == 'custom':
            command_args.extend(['--page-width', str(paperformat.page_width) + 'mm'])
            command_args.extend(['--page-height', str(paperformat.page_height) + 'mm'])

        if specific_paperformat_args and specific_paperformat_args.get('data-report-margin-top'):
            command_args.extend(['--margin-top', str(specific_paperformat_args['data-report-margin-top'])])
        else:
            command_args.extend(['--margin-top', str(paperformat.margin_top)])

        if specific_paperformat_args and specific_paperformat_args.get('data-report-dpi'):
            command_args.extend(['--dpi', str(specific_paperformat_args['data-report-dpi'])])
        elif paperformat.dpi:
            if os.name == 'nt' and int(paperformat.dpi) <= 95:
                _logger.info("Generating PDF on Windows platform require DPI >= 96. Using 96 instead.")
                command_args.extend(['--dpi', '96'])
            else:
                command_args.extend(['--dpi', str(paperformat.dpi)])

        if specific_paperformat_args and specific_paperformat_args.get('data-report-header-spacing'):
            command_args.extend(['--header-spacing', str(specific_paperformat_args['data-report-header-spacing'])])
        elif paperformat.header_spacing:
            command_args.extend(['--header-spacing', str(paperformat.header_spacing)])

        if specific_paperformat_args and specific_paperformat_args.get('data-report-margin-left'):
            command_args.extend(['--margin-left', str(specific_paperformat_args['data-report-margin-left'])])
        else:
            command_args.extend(['--margin-left', str(paperformat.margin_left)])

        if specific_paperformat_args and specific_paperformat_args.get('data-report-margin-bottom'):
            command_args.extend(['--margin-bottom', str(specific_paperformat_args['data-report-margin-bottom'])])
        else:
            command_args.extend(['--margin-bottom', str(paperformat.margin_bottom)])

        if specific_paperformat_args and specific_paperformat_args.get('data-report-margin-right'):
            command_args.extend(['--margin-right', str(specific_paperformat_args['data-report-margin-right'])])
        else:
            command_args.extend(['--margin-right', str(paperformat.margin_right)])

        if paperformat.orientation:
            command_args.extend(['--orientation', str(paperformat.orientation)])
        if paperformat.header_line:
            command_args.extend(['--header-line'])

        return command_args
