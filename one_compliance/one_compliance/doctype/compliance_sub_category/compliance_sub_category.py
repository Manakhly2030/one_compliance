# Copyright (c) 2023, efeone and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.model.mapper import *
from frappe import _

class ComplianceSubCategory(Document):
	def validate(self):
		self.validate_rate()

	def validate_rate(self):
		""" Method to validate rate """
		if not self.rate and self.is_billable:
			frappe.throw(_('Please Enter Valid Rate'))

@frappe.whitelist()
def create_project_manually(customer, project_template, expected_start_date, expected_end_date):
	compliance_sub_category = frappe.db.get_value('Project Template', project_template, 'compliance_sub_category')
	today = frappe.utils.today()
	project_name = customer + '-' + compliance_sub_category + '-' + today
	if not frappe.db.exists('Project', { 'project_name':project_name }):
		project = frappe.new_doc('Project')
		project.project_name = project_name
		project.project_template = project_template
		project.customer = customer
		project.expected_start_date = expected_start_date
		project.expected_end_date = expected_end_date
		project.save()
		frappe.msgprint("Project Created",alert = 1)
	else:
		frappe.msgprint("Project already created!")

@frappe.whitelist()
def create_project_template_custom_button(source_name, target_doc = None):
	''' Method to get project template for custom button using mapdoc '''
	def set_missing_values(source, target):
		target.compliance_category= source.compliance_category
		target.compliance_sub_category = source.name
	doc = get_mapped_doc(
		'Compliance Sub Category',
		source_name,
		{
			'Compliance Sub Category': {
			'doctype': 'Project Template',
        },
		}, target_doc, set_missing_values)
	return doc

@frappe.whitelist()
def get_notification_details():
	doc = frappe.get_doc('Compliance Settings')
	return doc


@frappe.whitelist()
def set_filter_for_employee(doctype, txt, searchfield, start, page_len, filters):
    # Applied filter for employee in compliance_executive child table
    searchfields = frappe.get_meta(doctype).get_search_fields()
    searchfields = " or ".join("ce." + field + " like %(txt)s" for field in searchfields)
    if filters['compliance_category']:
        return frappe.db.sql(
            """SELECT
                ce.employee,ce.employee_name
            FROM
                `tabCompliance Executive` as ce,
                `tabCompliance Category` as cc
            WHERE
                ({key})
                and cc.name = ce.parent
                and cc.name = %(compliance_category)s
            """.format(
                key=searchfields,
            ),
            {
            "txt": "%" + txt + "%",
            'compliance_category': filters['compliance_category']
            }
        )
