from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
import frappe, json
from frappe.model.document import Document
from frappe import _
from frappe.desk.search import sanitize_searchfield
from frappe.utils import (flt,rounded, getdate, get_url, now,
	nowtime, get_time, today, get_datetime, add_days)
from frappe.utils import add_to_date, now, nowdate
from frappe.model.document import Document
from frappe.utils import get_datetime, time_diff_in_hours
from frappe import _

class Clearances(Document):
	@frappe.whitelist()
	def on_submit(self):
		self.make_journal_entry()
		if self.sales_order:
			self.update_so_item_on_submit()
		elif self.purchase_order:
			self.update_po_item_on_submit()

	@frappe.whitelist()
	def on_cancel(self):
		if self.sales_order:
			self.update_so_item_on_cancel()
		elif self.purchase_order:
			self.update_po_item_on_cancel()

	@frappe.whitelist()
	def make_journal_entry(self):
		receivable_advanced_payments_account = frappe.db.get_value("Company", self.company, "receivable_advanced_payments_account")
		third_party_insurances_account = frappe.db.get_value("Company", self.company, "third_party_insurances_account")
		payable_advanced_payments_account = frappe.db.get_value("Company", self.company, "payable_advanced_payments_account")
		insurances_for_others_account = frappe.db.get_value("Company", self.company, "insurances_for_others_account")
		default_receivable_account = frappe.db.get_value("Company", self.company, "default_receivable_account")
		default_payable_account = frappe.db.get_value("Company", self.company, "default_payable_account")
		default_income_account = frappe.db.get_value("Company", self.company, "default_income_account")
		default_expense_account = frappe.db.get_value("Company", self.company, "default_expense_account")

		tax_account = ""
		tax_amount = 0
		values = frappe.db.sql("""select
											account_head as account_head,
											tax_amount as tax_amount
											from `tabClearance Taxes Table` where `tabClearance Taxes Table`.parent = %s
					""",self.name,as_dict=1)


		for y in values:
			tax_account = y.account_head
			tax_amount = y.tax_amount

		if self.clearance_type == "Outgoing":
			accounts = [
				{
					"doctype": "Journal Entry Account",
					"account": default_receivable_account,
					"party_type": "Customer",
					"party": self.customer,
					"project": self.project,
					"debit": round((round(self.total_taxes_amount, 2) - round(self.advanced_payment_insurance_amount, 2) - round(self.initial_delivery_payment_insurance_amount, 2)), 2),
					"credit": 0,
					"debit_in_account_currency": round((round(self.total_taxes_amount, 2) - round(self.advanced_payment_insurance_amount, 2) - round(self.initial_delivery_payment_insurance_amount, 2)), 2),
					"user_remark": self.name
				},
				{
					"doctype": "Journal Entry Account",
					"account": receivable_advanced_payments_account,
					"project": self.project,
					"debit": round(self.advanced_payment_insurance_amount, 2),
					"credit": 0,
					"debit_in_account_currency": round(self.advanced_payment_insurance_amount, 2),
					"user_remark": self.name
				},
				{
					"doctype": "Journal Entry Account",
					"account": third_party_insurances_account,
					"project": self.project,
					"debit": round(self.initial_delivery_payment_insurance_amount, 2),
					"credit": 0,
					"debit_in_account_currency": round(self.initial_delivery_payment_insurance_amount, 2),
					"user_remark": self.name
				},
				{
					"doctype": "Journal Entry Account",
					"account": default_income_account,
					"project": self.project,
					"debit": 0,
					"credit": round(self.total_current_amount, 2),
					"credit_in_account_currency": round(self.total_current_amount, 2),
					"user_remark": self.name
				},
				{
					"doctype": "Journal Entry Account",
					"account": tax_account,
					"project": self.project,
					"debit": 0,
					"credit": round(tax_amount,2),
					"credit_in_account_currency": round(tax_amount, 2),
					"user_remark": self.name
				}
			]
			doc = frappe.get_doc({
				"doctype": "Journal Entry",
				"voucher_type": "Journal Entry",
				"company": self.company,
				"posting_date": self.clearance_date,
				"reference_doctype": "Clearances",
				"reference_link": self.name,
				"accounts": accounts,
				"cheque_no": self.name,
				"cheque_date": self.clearance_date,
				"user_remark": self.notes,
				"remark": _('Clearance  {0}').format(self.name)

			})
			doc.insert()
			doc.submit()

		if self.clearance_type == "Incoming":
			accounts = [
				{
					"doctype": "Journal Entry Account",
					"account": default_expense_account,
					"project": self.project,
					"credit": 0,
					"debit": round(self.total_current_amount, 2),
					"debit_in_account_currency": round(self.total_current_amount, 2),
					"user_remark": self.name
				},
				{
					"doctype": "Journal Entry Account",
					"account": tax_account,
					"project": self.project,
					"credit": 0,
					"debit": round(tax_amount, 2),
					"debit_in_account_currency": round(tax_amount, 2),
					"user_remark": self.name
				},
				{
					"doctype": "Journal Entry Account",
					"account": default_payable_account,
					"party_type": "Supplier",
					"party": self.supplier,
					"project": self.project,
					"credit": round((round(self.total_taxes_amount, 2) - round(self.advanced_payment_insurance_amount, 2) - round(self.initial_delivery_payment_insurance_amount, 2)), 2),
					"debit": 0,
					"credit_in_account_currency": round((round(self.total_taxes_amount, 2) - round(self.advanced_payment_insurance_amount, 2) - round(self.initial_delivery_payment_insurance_amount, 2)), 2),
					"user_remark": self.name
				},
				{
					"doctype": "Journal Entry Account",
					"account": payable_advanced_payments_account,
					"project": self.project,
					"credit": round(self.advanced_payment_insurance_amount, 2),
					"debit": 0,
					"credit_in_account_currency": round(self.advanced_payment_insurance_amount, 2),
					"user_remark": self.name
				},
				{
					"doctype": "Journal Entry Account",
					"account": insurances_for_others_account,
					"project": self.project,
					"credit": round(self.initial_delivery_payment_insurance_amount, 2),
					"debit": 0,
					"credit_in_account_currency": round(self.initial_delivery_payment_insurance_amount, 2),
					"user_remark": self.name
				}
			]
			doc = frappe.get_doc({
				"doctype": "Journal Entry",
				"voucher_type": "Journal Entry",
				"company": self.company,
				"reference_doctype": "Clearances",
				"reference_link": self.name,
				"posting_date": self.clearance_date,
				"accounts": accounts,
				"cheque_no": self.name,
				"cheque_date": self.clearance_date,
				"user_remark": self.notes,
				"remark": _('Clearance  {0}').format(self.name)

			})
			doc.insert()
			doc.submit()

	@frappe.whitelist()
	def get_purchase_items(self):
		process = frappe.get_doc("Purchase Order", self.purchase_order)
		if process:
			if process.items:
				self.add_po_item_in_table(process.items, "items")

	@frappe.whitelist()
	def get_purchase_taxes(self):
		process = frappe.get_doc("Purchase Taxes and Charges Template", self.purchase_taxes_and_charges_template)
		if process:
			if process.taxes:
				self.add_po_taxes_in_table(process.taxes, "taxes")

	@frappe.whitelist()
	def get_sales_items(self):
		process = frappe.get_doc("Sales Order", self.sales_order)
		if process:
			if process.items:
				self.add_so_item_in_table(process.items, "items")

	@frappe.whitelist()
	def get_sales_taxes(self):
		process = frappe.get_doc("Sales Taxes and Charges Template", self.sales_taxes_and_charges_template)
		if process:
			if process.taxes:
				self.add_so_taxes_in_table(process.taxes, "taxes")

	@frappe.whitelist()
	def add_po_item_in_table(self, table_value, table_name):
		self.set(table_name, [])
		for item in table_value:
			po_item = self.append(table_name, {})
			po_item.name1 = item.name
			po_item.item_code = item.item_code
			po_item.item_name = item.item_name
			po_item.description = item.description
			po_item.uom = item.uom
			po_item.qty = item.qty
			po_item.rate = item.rate
			po_item.amount = item.amount
			po_item.previous_qty = item.current_qty
			po_item.previous_amount = item.current_amount

	@frappe.whitelist()
	def add_po_taxes_in_table(self, table_value, table_name):
		self.set(table_name, [])
		for tax in table_value:
			po_tax = self.append(table_name, {})
			po_tax.charge_type = tax.charge_type
			po_tax.account_head = tax.account_head
			po_tax.description = tax.description
			po_tax.rate = tax.rate
			po_tax.tax_amount = tax.tax_amount
			po_tax.total = tax.total

	@frappe.whitelist()
	def add_so_item_in_table(self, table_value, table_name):
		self.set(table_name, [])
		for item in table_value:
			so_item = self.append(table_name, {})
			so_item.name1 = item.name
			so_item.item_code = item.item_code
			so_item.item_name = item.item_name
			so_item.description = item.description
			so_item.uom = item.uom
			so_item.qty = item.qty
			so_item.rate = item.rate
			so_item.amount = item.amount
			so_item.previous_qty = item.current_qty
			so_item.previous_amount = item.current_amount

	@frappe.whitelist()
	def add_so_taxes_in_table(self, table_value, table_name):
		self.set(table_name, [])
		for tax in table_value:
			so_tax = self.append(table_name, {})
			so_tax.charge_type = tax.charge_type
			so_tax.account_head = tax.account_head
			so_tax.description = tax.description
			so_tax.rate = tax.rate
			so_tax.tax_amount = tax.tax_amount
			so_tax.total = tax.total

	@frappe.whitelist()
	def make_payment(self):
		default_receivable_account = frappe.db.get_value("Company", self.company, "default_receivable_account")
		default_payable_account = frappe.db.get_value("Company", self.company, "default_payable_account")
		default_cash_account = frappe.db.get_value("Company", self.company, "default_cash_account")

		if self.clearance_type == "Outgoing" and self.total_deduction_amount > 0:
			accounts = [
				{
					"doctype": "Journal Entry Account",
					"account": default_cash_account,
					"debit": 0,
					"project": self.project,
					"credit": round((round(self.total_taxes_amount, 2) + round(self.total_deduction_amount, 2) - round(self.advanced_payment_insurance_amount, 2) - round(self.initial_delivery_payment_insurance_amount, 2) - round(self.total_paid_amount, 2)), 2),
					"credit_in_account_currency": round((round(self.total_taxes_amount, 2) + round(self.total_deduction_amount, 2) - round(self.advanced_payment_insurance_amount, 2) - round(self.initial_delivery_payment_insurance_amount, 2) - round(self.total_paid_amount, 2)), 2),
					"user_remark": self.name
				},
				{
					"doctype": "Journal Entry Account",
					"account": default_receivable_account,
					"debit": round((round(self.total_taxes_amount, 2) - round(self.advanced_payment_insurance_amount, 2) - round(self.initial_delivery_payment_insurance_amount, 2) - round(self.total_paid_amount, 2)), 2),
					"party_type": "Customer",
					"party": self.customer,
					"project": self.project,
					"credit": 0,
					"debit_in_account_currency": round((round(self.total_taxes_amount, 2) - round(self.advanced_payment_insurance_amount, 2) - round(self.initial_delivery_payment_insurance_amount, 2) - round(self.total_paid_amount, 2)), 2),
					"user_remark": self.name
				}
			]
			deductions_table = frappe.db.sql(""" select 
			account as account ,
			amount as amount,
			description as description,
			cost_center as cost_center
			from `tabPayment Entry Deduction` where parent = %s
			""",self.name,as_dict=1)

			for x in deductions_table:
				accounts1 = {
					"doctype": "Journal Entry Account",
					"account": x.account,
					"debit": round(x.amount, 2),
					"project": self.project,
					"cost_center": x.cost_center,
					"credit": 0,
					"debit_in_account_currency": round(x.amount, 2),
					"user_remark": x.description
				},
				accounts.extend(accounts1)

			doc = frappe.get_doc({
				"doctype": "Journal Entry",
				"voucher_type": "Journal Entry",
				"clearance_payment": 1,
				"company": self.company,
				"reference_doctype": "Clearances",
				"reference_link": self.name,
				"posting_date": self.clearance_date,
				"accounts": accounts,
				"cheque_no": self.name,
				"cheque_date": self.clearance_date,
				"user_remark": self.notes,
				"remark": _('Clearance  {0}').format(self.name)
					})
			doc.insert()

		if self.clearance_type == "Outgoing" and self.total_deduction_amount == 0:
			accounts = [
				{
					"doctype": "Journal Entry Account",
					"account": default_receivable_account,
					"debit": round((round(self.total_taxes_amount, 2) - round(self.advanced_payment_insurance_amount, 2) - round(self.initial_delivery_payment_insurance_amount, 2) - round(self.total_paid_amount, 2)), 2),
					"party_type": "Customer",
					"party": self.customer,
					"project": self.project,
					"credit": 0,
					"debit_in_account_currency": round((round(self.total_taxes_amount, 2) - round(self.advanced_payment_insurance_amount, 2) - round(self.initial_delivery_payment_insurance_amount, 2) - round(self.total_paid_amount, 2)), 2),
					"user_remark": self.name
				},
				{
					"doctype": "Journal Entry Account",
					"account": default_cash_account,
					"debit": 0,
					"project": self.project,
					"credit": round((round(self.total_taxes_amount, 2) - round(self.advanced_payment_insurance_amount, 2) - round(self.initial_delivery_payment_insurance_amount, 2) - round(self.total_paid_amount, 2)), 2),
					"credit_in_account_currency": round((round(self.total_taxes_amount, 2) - round(self.advanced_payment_insurance_amount, 2) - round(self.initial_delivery_payment_insurance_amount, 2) - round(self.total_paid_amount, 2)), 2),
					"user_remark": self.name
				}
			]

			doc = frappe.get_doc({
				"doctype": "Journal Entry",
				"voucher_type": "Journal Entry",
				"clearance_payment": 1,
				"company": self.company,
				"reference_doctype": "Clearances",
				"reference_link": self.name,
				"posting_date": self.clearance_date,
				"accounts": accounts,
				"cheque_no": self.name,
				"cheque_date": self.clearance_date,
				"user_remark": self.notes,
				"remark": _('Clearance  {0}').format(self.name)
					})
			doc.insert()

		if self.clearance_type == "Incoming" and self.total_deduction_amount > 0:
			accounts = [
				{
					"doctype": "Journal Entry Account",
					"account": default_cash_account,
					"project": self.project,
					"debit": round((round(self.total_taxes_amount, 2) + round(self.total_deduction_amount, 2) - round(self.advanced_payment_insurance_amount, 2) - round(self.initial_delivery_payment_insurance_amount, 2) - round(self.total_paid_amount, 2)), 2),
					"credit": 0,
					"debit_in_account_currency": round((round(self.total_taxes_amount, 2) + round(self.total_deduction_amount, 2) - round(self.advanced_payment_insurance_amount, 2) - round(self.initial_delivery_payment_insurance_amount, 2) - round(self.total_paid_amount, 2)), 2),
					"user_remark": self.name
				},
				{
					"doctype": "Journal Entry Account",
					"account": default_payable_account,
					"party_type": "Supplier",
					"party": self.supplier,
					"project": self.project,
					"debit": 0,
					"credit": round((round(self.total_taxes_amount, 2) - round(self.advanced_payment_insurance_amount, 2) - round(self.initial_delivery_payment_insurance_amount, 2) - round(self.total_paid_amount, 2)) ,2),
					"credit_in_account_currency": round((round(self.total_taxes_amount, 2) - round(self.advanced_payment_insurance_amount, 2) - round(self.initial_delivery_payment_insurance_amount, 2) - round(self.total_paid_amount, 2)) ,2),
					"user_remark": self.name
				}
			]
			deductions_table = frappe.db.sql(""" select 
			account as account ,
			amount as amount,
			description as description,
			cost_center as cost_center
			from `tabPayment Entry Deduction` where parent = %s
			""", self.name, as_dict=1)

			for x in deductions_table:
				accounts1 = {
					"doctype": "Journal Entry Account",
					"account": x.account,
					"credit": round(x.amount, 2),
					"project": self.project,
					"cost_center": x.cost_center,
					"debit": 0,
					"credit_in_account_currency": round(x.amount, 2),
					"user_remark": x.description
				},
				accounts.extend(accounts1)

			doc = frappe.get_doc({
				"doctype": "Journal Entry",
				"voucher_type": "Journal Entry",
				"company": self.company,
				"reference_doctype": "Clearances",
				"reference_link": self.name,
				"clearance_payment": 1,
				"posting_date": self.clearance_date,
				"accounts": accounts,
				"cheque_no": self.name,
				"cheque_date": self.clearance_date,
				"user_remark": self.notes,
				"remark": _('Clearance  {0}').format(self.name)
					})
			doc.insert()

		if self.clearance_type == "Incoming" and self.total_deduction_amount == 0:
			accounts = [
				{
					"doctype": "Journal Entry Account",
					"account": default_cash_account,
					"project": self.project,
					"debit": round((round(self.total_taxes_amount, 2) - round(self.advanced_payment_insurance_amount, 2) - round(self.initial_delivery_payment_insurance_amount, 2) - round(self.total_paid_amount, 2)), 2),
					"credit": 0,
					"debit_in_account_currency": round((round(self.total_taxes_amount, 2) - round(self.advanced_payment_insurance_amount, 2) - round(self.initial_delivery_payment_insurance_amount, 2) - round(self.total_paid_amount, 2)), 2),
					"user_remark": self.name
				},
				{
					"doctype": "Journal Entry Account",
					"account": default_payable_account,
					"party_type": "Supplier",
					"party": self.supplier,
					"project": self.project,
					"debit": 0,
					"credit": round((round(self.total_taxes_amount, 2) - round(self.advanced_payment_insurance_amount,2) - round(self.initial_delivery_payment_insurance_amount, 2) - round(self.total_paid_amount, 2)), 2),
					"credit_in_account_currency": round((round(self.total_taxes_amount, 2) - round(self.advanced_payment_insurance_amount, 2) - round(self.initial_delivery_payment_insurance_amount, 2) - round(self.total_paid_amount, 2)), 2),
					"user_remark": self.name
				}
			]

			doc = frappe.get_doc({
				"doctype": "Journal Entry",
				"voucher_type": "Journal Entry",
				"company": self.company,
				"reference_doctype": "Clearances",
				"reference_link": self.name,
				"clearance_payment": 1,
				"posting_date": self.clearance_date,
				"accounts": accounts,
				"cheque_no": self.name,
				"cheque_date": self.clearance_date,
				"user_remark": self.notes,
				"remark": _('Clearance  {0}').format(self.name)
			})
			doc.insert()

	@frappe.whitelist()
	def update_so_item_on_submit(self):
		for x in self.items:
			frappe.db.set_value('Sales Order Item', x.name1, 'current_qty', x.completed_qty)
			frappe.db.set_value('Sales Order Item', x.name1, 'current_amount', x.completed_amount)


	@frappe.whitelist()
	def update_po_item_on_submit(self):
		for x in self.items:
			frappe.db.set_value('Purchase Order Item', x.name1, 'current_qty', x.completed_qty)
			frappe.db.set_value('Purchase Order Item', x.name1, 'current_amount', x.completed_amount)

	@frappe.whitelist()
	def update_so_item_on_cancel(self):
		for x in self.items:
			so_current_qty = frappe.db.get_value('Sales Order Item', x.name1, 'current_qty')
			so_current_amt = frappe.db.get_value('Sales Order Item', x.name1, 'current_amount')
			frappe.db.set_value('Sales Order Item', x.name1, 'current_qty', so_current_qty - x.current_qty)
			frappe.db.set_value('Sales Order Item', x.name1, 'current_amount', so_current_amt - x.current_amount)

	@frappe.whitelist()
	def update_po_item_on_cancel(self):
		for x in self.items:
			po_current_qty = frappe.db.get_value('Purchase Order Item', x.name1, 'current_qty')
			po_current_amt = frappe.db.get_value('Purchase Order Item', x.name1, 'current_amount')
			frappe.db.set_value('Purchase Order Item', x.name1, 'current_qty', po_current_qty - x.current_qty)
			frappe.db.set_value('Purchase Order Item', x.name1, 'current_amount', po_current_amt - x.current_amount)






