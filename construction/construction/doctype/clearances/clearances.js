/*
cur_frm.add_fetch('sales_order',  'project',  'project');
cur_frm.add_fetch('purchase_order',  'project',  'project');
cur_frm.add_fetch('sales_order',  'advanced_payment_insurance_rate',  'advanced_payment_insurance_rate');
cur_frm.add_fetch('purchase_order',  'advanced_payment_insurance_rate',  'advanced_payment_insurance_rate');
cur_frm.add_fetch('sales_order',  'initial_delivery_payment_insurance_rate',  'initial_delivery_payment_insurance_rate');
cur_frm.add_fetch('purchase_order',  'initial_delivery_payment_insurance_rate',  'initial_delivery_payment_insurance_rate');
cur_frm.add_fetch('sales_order',  'taxes_and_charges',  'sales_taxes_and_charges_template');
cur_frm.add_fetch('purchase_order',  'taxes_and_charges',  'purchase_taxes_and_charges_template');
cur_frm.add_fetch('sales_order',  'clearance_type',  'clearance_type');
cur_frm.add_fetch('purchase_order',  'clearance_type',  'clearance_type');
*/

frappe.ui.form.on("Clearances", {
	setup: function(frm) {
		frm.set_query("purchase_order", function() {
			return {
				filters: [
					["Purchase Order","docstatus", "=", "1"]
				]
			};
		});
	}
});

frappe.ui.form.on("Clearances", {
	setup: function(frm) {
		frm.set_query("sales_order", function() {
			return {
				filters: [
					["Sales Order","docstatus", "=", "1"]
				]
			};
		});
	}
});


frappe.ui.form.on("Clearances", "sales_order", function(frm) {
    if(cur_frm.doc.clearance_type == "Outgoing"){
        frappe.call({ method: "frappe.client.get_value", args: {
            doctype: "Sales Order",
            fieldname: "project",
            filters: { 'name': cur_frm.doc.sales_order}
            },
        callback: function(r) { cur_frm.set_value("project", r.message.project); }
        });

        frappe.call({ method: "frappe.client.get_value", args: {
            doctype: "Sales Order",
            fieldname: "advanced_payment_insurance_rate",
            filters: { 'name': cur_frm.doc.sales_order}
            },
        callback: function(r) { cur_frm.set_value("advanced_payment_insurance_rate", r.message.advanced_payment_insurance_rate); }
        });

        frappe.call({ method: "frappe.client.get_value", args: {
            doctype: "Sales Order",
            fieldname: "initial_delivery_payment_insurance_rate",
            filters: { 'name': cur_frm.doc.sales_order}
            },
        callback: function(r) { cur_frm.set_value("initial_delivery_payment_insurance_rate", r.message.initial_delivery_payment_insurance_rate); }
        });
/*
        frappe.call({ method: "frappe.client.get_value", args: {
            doctype: "Sales Order",
            fieldname: "clearance_type",
            filters: { 'name': cur_frm.doc.sales_order}
            },
        callback: function(r) { cur_frm.set_value("clearance_type", r.message.clearance_type); }
        });
*/
        frappe.call({ method: "frappe.client.get_value", args: {
            doctype: "Sales Order",
            fieldname: "taxes_and_charges",
            filters: { 'name': cur_frm.doc.sales_order}
            },
        callback: function(r) { cur_frm.set_value("sales_taxes_and_charges_template", r.message.taxes_and_charges); }
        });
    }
});

frappe.ui.form.on('Clearances',  'sales_order',  function(frm) {
    cur_frm.clear_table("items");
    cur_frm.clear_table("taxes");
});

frappe.ui.form.on('Clearances', {
    sales_order: function(frm) {
        if(cur_frm.doc.sales_order){
            frappe.call({
                doc: frm.doc,
                  method: "get_sales_items",
                    callback: function(r) {
                    refresh_field("items");
                    }
            });
        }
	}
})

frappe.ui.form.on('Clearances', {
    sales_order: function(frm) {
		if(frm.doc.sales_taxes_and_charges_template){
			frappe.call({
				doc: frm.doc,
				method: "get_sales_taxes",
				    callback: function(r) {
                    refresh_field("taxes");
                    }
			});
		}
	}
})


frappe.ui.form.on('Clearances', {
    sales_taxes_and_charges_template: function(frm) {
		if(frm.doc.sales_taxes_and_charges_template){
			frappe.call({
				doc: frm.doc,
				method: "get_sales_taxes",
				    callback: function(r) {
                    refresh_field("taxes");
                    }
			});
		}
	}
})



frappe.ui.form.on("Clearances", "purchase_order", function(frm) {
    if(cur_frm.doc.clearance_type == "Incoming"){
        frappe.call({ method: "frappe.client.get_value", args: {
            doctype: "Purchase Order",
            fieldname: "project",
            filters: { 'name': cur_frm.doc.purchase_order}
            },
        callback: function(r) { cur_frm.set_value("project", r.message.project); }
        });

        frappe.call({ method: "frappe.client.get_value", args: {
            doctype: "Purchase Order",
            fieldname: "advanced_payment_insurance_rate",
            filters: { 'name': cur_frm.doc.purchase_order}
            },
        callback: function(r) { cur_frm.set_value("advanced_payment_insurance_rate", r.message.advanced_payment_insurance_rate); }
        });

        frappe.call({ method: "frappe.client.get_value", args: {
            doctype: "Purchase Order",
            fieldname: "initial_delivery_payment_insurance_rate",
            filters: { 'name': cur_frm.doc.purchase_order}
            },
        callback: function(r) { cur_frm.set_value("initial_delivery_payment_insurance_rate", r.message.initial_delivery_payment_insurance_rate); }
        });
/*
        frappe.call({ method: "frappe.client.get_value", args: {
            doctype: "Purchase Order",
            fieldname: "clearance_type",
            filters: { 'name': cur_frm.doc.purchase_order}
            },
        callback: function(r) { cur_frm.set_value("clearance_type", r.message.clearance_type); }
        });
*/
        frappe.call({ method: "frappe.client.get_value", args: {
            doctype: "Purchase Order",
            fieldname: "taxes_and_charges",
            filters: { 'name': cur_frm.doc.purchase_order}
            },
        callback: function(r) { cur_frm.set_value("purchase_taxes_and_charges_template", r.message.taxes_and_charges); }
        });
    }
});



frappe.ui.form.on('Clearances',  'purchase_order',  function(frm) {
    cur_frm.clear_table("items");
    cur_frm.clear_table("taxes");
});

frappe.ui.form.on('Clearances', {
    purchase_order: function(frm) {
        if(cur_frm.doc.purchase_order){
            frappe.call({
                doc: frm.doc,
                method: "get_purchase_items",
                    callback: function(r) {
                    refresh_field("items");
                    }
            });
        }
	}
})

frappe.ui.form.on('Clearances', {
    purchase_order: function(frm) {
		if(frm.doc.purchase_taxes_and_charges_template){
			frappe.call({
				doc: frm.doc,
				method: "get_purchase_taxes",
				    callback: function(r) {
                    refresh_field("taxes");
                    }
			});
		}
	}
})


frappe.ui.form.on('Clearances', {
    purchase_taxes_and_charges_template: function(frm) {
		if(frm.doc.purchase_taxes_and_charges_template){
			frappe.call({
				doc: frm.doc,
				method: "get_purchase_taxes",
				    callback: function(r) {
                    refresh_field("taxes");
                    }
			});
		}
	}
})


frappe.ui.form.on('Clearances',  'clearance_type',  function(frm) {
    if (cur_frm.doc.clearance_type != "Outgoing" && cur_frm.doc.sales_order) {
        cur_frm.set_value('sales_order', '');
        cur_frm.set_value('customer', '');
        cur_frm.set_value('sales_order_date', '');
        cur_frm.set_value('delivery_date', '');
        cur_frm.set_value('project', '');
        cur_frm.set_value('sales_taxes_and_charges_template', '');
        cur_frm.set_value('advanced_payment_insurance_rate', 0);
        cur_frm.set_value('initial_delivery_payment_insurance_rate', 0);
    }
    if (cur_frm.doc.clearance_type != "Incoming" && cur_frm.doc.purchase_order) {
        cur_frm.set_value('purchase_order', '');
        cur_frm.set_value('supplier', '');
        cur_frm.set_value('purchase_order_date', '');
        cur_frm.set_value('required_by_date', '');
        cur_frm.set_value('project', '');
        cur_frm.set_value('purchase_taxes_and_charges_template', '');
        cur_frm.set_value('advanced_payment_insurance_rate', 0);
        cur_frm.set_value('initial_delivery_payment_insurance_rate', 0);
    }
});


frappe.ui.form.on("Clearances", "before_submit", function(frm, cdt, cdn) {
    $.each(frm.doc.items || [], function(i, d) {
        /*
        if (d.current_qty == 0){
            frappe.throw("يرجاء إدخال الكمية الحالية");
        }
        */
        if (d.current_progress == 0){
            frappe.throw("يرجاء إدخال النسبة الحالية");
        }
    });
    $.each(frm.doc.taxes || [], function(i, d) {
        if (d.tax_amount == 0){
            frappe.throw("يرجاء إدخال قيمة الضريبة");
        }
    });
});

frappe.ui.form.on("Clearances", "validate", function(frm, cdt, cdn) {
    $.each(frm.doc.items || [], function(i, d) {
        d.current_qty = d.current_progress * d.qty / 100;
        d.current_amount = d.current_qty * d.rate;
        //d.current_progress = 100 * d.current_qty / d.qty;
        d.previous_progress = 100 * d.previous_qty / d.qty;
        d.completed_qty = d.current_qty + d.previous_qty;
        d.completed_amount = d.completed_qty * d.rate;
        d.completed_progress = 100 * d.completed_qty / d.qty;
        d.remaining_qty = d.qty - d.completed_qty;
        d.remaining_amount = d.remaining_qty * d.rate;
        d.remaining_progress = 100 * d.remaining_qty / d.qty;

        if (d.current_qty > d.qty){
            frappe.throw("الكمية الحالية لا يمكن أن تكون أكبر من كمية العقد");
        }
        else if ((d.current_qty + d.previous_qty) > d.qty){
            frappe.throw("الكمية الإجمالية لا يمكن أن تكون أكبر من كمية العقد");
        }
        /*else if (d.completed_qty > 100){
            frappe.throw("الكمية الإجمالية لا يمكن أن تكون أكبر من %100");
        }
*/
    });
});

frappe.ui.form.on("Clearances", {
    validate:function(frm, cdt, cdn){
        var dw = locals[cdt][cdn];
        var total = 0;
        frm.doc.items.forEach(function(dw) { total += dw.current_amount; });
        frm.set_value("total_current_amount", total);
        refresh_field("total_current_amount");
    },
});

frappe.ui.form.on("Clearances","validate", function(){
    for (var i = 0; i < cur_frm.doc.taxes.length; i++){
        cur_frm.doc.taxes[i].tax_amount = cur_frm.doc.taxes[i].rate * cur_frm.doc.total_current_amount / 100;
        cur_frm.doc.taxes[i].total = cur_frm.doc.taxes[i].tax_amount + cur_frm.doc.total_current_amount;
    }
    cur_frm.refresh_field('taxes');
});

frappe.ui.form.on("Clearances", {
    validate:function(frm, cdt, cdn){
        var dw = locals[cdt][cdn];
        var total = 0;
        frm.doc.taxes.forEach(function(dw) { total += dw.total; });
        frm.set_value("total_taxes_amount", total);
        refresh_field("total_taxes_amount");
    },

    refresh: function(frm) {
    if (cur_frm.doc.docstatus == 1 && cur_frm.doc.total_paid_amount < (cur_frm.doc.total_current_amount - cur_frm.doc.total_deduction_amount - cur_frm.doc.advanced_payment_insurance_amount - cur_frm.doc.initial_delivery_payment_insurance_amount)){
    frm.add_custom_button(__("Make Payment"), function() {
           frm.refresh();
		   frappe.call({
				doc: frm.doc,
				method: "make_payment",
			});
			frappe.msgprint("تم إنشاء قيد الدفع بنجاح ... برجاء الدخول على القيد وتوجيه حساب الدفع والمبلغ المدفوع");
		},
		).addClass("btn-primary").css({'color':'white'});
	}}
});

frappe.ui.form.on("Clearances", {
    before_submit:function(frm, cdt, cdn){
        var dw = locals[cdt][cdn];
        var total = 0;
        frm.doc.deductions_table.forEach(function(dw) { total += dw.amount; });
        frm.set_value("total_deduction_amount", total);
        refresh_field("total_deduction_amount");
        if (cur_frm.doc.total_deduction_amount > cur_frm.doc.total_taxes_amount){
            frappe.throw("مبلغ الخصومات لا يمكن أن يكون أكبر من المبلغ الإجمالي");
        }
    },
});

frappe.ui.form.on("Clearances","validate", function(){
        cur_frm.doc.advanced_payment_insurance_amount = cur_frm.doc.total_taxes_amount * cur_frm.doc.advanced_payment_insurance_rate / 100;
        cur_frm.doc.initial_delivery_payment_insurance_amount = cur_frm.doc.total_taxes_amount * cur_frm.doc.initial_delivery_payment_insurance_rate / 100;
});