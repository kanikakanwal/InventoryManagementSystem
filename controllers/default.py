# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a sample controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
#########################################################################
def checkmembership():

    if auth.has_membership(group_id='admin_group'):
        redirect(URL('default', 'adminHome'))
    if auth.has_membership(group_id='Manager'):
        redirect(URL('default', 'managerHome'))
    if auth.has_membership(group_id='Cashier'):
        redirect(URL('default', 'cashierHome',vars=dict(from1='login')))

def index():
#    SQLFORM.factory(Field('category, requires=IS_IN_DB(db,'x'))
    return locals()

@auth.requires(checkmembership)
def index2():
#    SQLFORM.factory(Field('category, requires=IS_IN_DB(db,'x'))
    return locals()

def my_signup():
    return dict(form=auth.register())

@auth.requires_membership('admin_group')
def adminHome():
    grid=SQLFORM.grid(db.item)
    if request.args(0)=='stockAdded':
        response.flash=T("Added the selected stocks.")
    return locals()


@auth.requires(auth.has_membership('admin_group') or auth.has_membership('Cashier'))
def cashierHome():
    src = request.vars['from1']

    if src =='mailSent':
        response.flash=T("Mail sent Successfully..")
    elif src =='login':
        response.flash=T("Welcome! Cashier, Below are the bill details of the Inventory...")
    elif src =='error':
        response.flash=T("PLease Enter a valid Month Number...")
    try:
        f_max=db.bill.bill_id.max()
        rows = db(db.bill.bill_id).select(f_max)
        bill_id_max=rows[0][f_max]+1
    except TypeError:
        bill_id_max=10002

    return locals()

@auth.requires_membership('admin_group')
def updateToStock():
    rows=db(db.orders).select()
    return locals()



@auth.requires(auth.has_membership('admin_group') or auth.has_membership('Manager'))
def managerHome():
    rows=db(db.stock).select()
    response.flash=T("Welcome!, Following are the stock below their threshold...")

    if request.args(0)=='orderPlaced':
        response.flash=T("Order placed successfully..")
    return locals()

@auth.requires(auth.has_membership('admin_group') or auth.has_membership('Manager'))
def orderStock():
    grid=SQLFORM.grid(db.stock)
    return locals()

@auth.requires(auth.has_membership('admin_group') or auth.has_membership('Manager'))
def allOrderStock():
    response.flash=T(" Please verify and delete the items, already added to stock...")
    grid=SQLFORM.grid(db.orders)
    return locals()
@auth.requires(auth.has_membership('admin_group') or auth.has_membership('Manager'))
def placeOrder():

    flag=0
    orderplacing_dict = request.vars
#    length=len(orderplacing_dict['entrySelect'])

    try:
        item_selectionsList=int(orderplacing_dict['entrySelect'])
    except TypeError:
        flag=1
        item_selectionsList=[]
        item_selectionsList=orderplacing_dict['entrySelect']

    if flag==1:
        for elem in item_selectionsList:
            itemRow = db.stock[elem]
            db.orders.purchase_date.default=request.now
            ven_dict=getVendor(itemRow.item_id)
#insert to order table

            db.orders.insert(item_id=itemRow.item_id)
            db.orders.update_or_insert(db.orders.item_id== itemRow.item_id, status = "Stock_Ordered" , vendor = ven_dict['ven'])

            db(db.stock.id == elem).update(order_placing_flag='ON')

    elif flag==0:
        itemRow = db.stock[item_selectionsList]
        db.orders.purchase_date.default=request.now
        ven_dict=getVendor(itemRow.item_id)
#insert to order table

        db.orders.insert(item_id=itemRow.item_id)
        db.orders.update_or_insert(db.orders.item_id== itemRow.item_id, status = "Stock_Ordered" , vendor = ven_dict['ven'])

        db(db.stock.id == item_selectionsList).update(order_placing_flag='ON')

    redirect(URL('default', 'managerHome', args=('orderPlaced')))

    return locals()

def getVendor(elem):
    itemRow = db.item[elem]
    ven=itemRow.vendor
    return locals()

@auth.requires_membership('admin_group')
def addToStock():
    flag=0

    addingTostk_dict={}
    addingTostk_dict = request.vars

    try:
        item_selectionsList=int(addingTostk_dict['entrySelect'])
    except TypeError:
        flag=1
        item_selectionsList=[]
        item_selectionsList=addingTostk_dict['entrySelect']

    if flag==1:
        for elem in item_selectionsList:
            record = db(db.stock.item_id==elem).select()
            for row in record:
                quantity = row.quantity
                threshold = row.item_threshold
                new_quantity = quantity + threshold
                db(db.stock.item_id==elem).update(quantity=new_quantity)
                db(db.stock.item_id==elem).update(order_placing_flag='OFF')
                db(db.orders.item_id==elem).update(status='Stock_Added')


    elif flag==0:
        record = db(db.stock.item_id==item_selectionsList).select()
        for row in record:
            quantity = row.quantity
            threshold = row.item_threshold
            new_quantity = quantity + threshold
            db(db.stock.item_id==item_selectionsList).update(quantity=new_quantity)
            db(db.stock.item_id==item_selectionsList).update(order_placing_flag='OFF')
            db(db.orders.item_id==item_selectionsList).update(status='Stock_Added')

    redirect(URL('default', 'adminHome',args=('stockAdded')))

    return locals()

@auth.requires(auth.has_membership('admin_group') or auth.has_membership('Cashier'))
def placeBill():
    bill_id_max=request.args(0)
    src = request.vars['from1']

    if src =='cshrHome':
        response.flash=T("Place your bill here..")
    elif src =='moreBt':
        response.flash=T("Added item to Bill..")
    elif src=='noStock':
         response.flash=T("Sorry.. We are out of Stock!")
    return locals()

@auth.requires(auth.has_membership('admin_group') or auth.has_membership('Cashier'))
def createBill():
    billdetails_dict=request.vars

    quantity_entered=billdetails_dict['qty']
    customer_entered=billdetails_dict['customer']
    selected_item=billdetails_dict['itemList']
    selected_category=billdetails_dict['categoryList']

    record = db(db.item.item_name==selected_item).select()
    for row in record:
        if  row.item_category==selected_category:
            curr_item_id = row.id

# code to check if quantity entered is less than stock available
            stock_rec = db(db.stock.item_id==curr_item_id).select()
            for rec in stock_rec:
                if  rec.item_id==curr_item_id:
                    stk_qty = rec.quantity
                    quantity_entered=int(quantity_entered)
                    if  quantity_entered<stk_qty:
                        new_qty=stk_qty-quantity_entered
                        db(db.stock.item_id==curr_item_id).update(quantity=new_qty)
                        sp = row.selling_price
                        cp = row.cost_price

                        temp=float(quantity_entered)*(sp-cp)

                        dy_sp=float(quantity_entered)*sp
                        db.bill.bill_date.default=request.now
                        bill_id_max=request.args(0)

                        val_id=db.bill.insert(bill_id=bill_id_max)
                        db.bill.update_or_insert(db.bill.id==val_id, item_id=curr_item_id , price=dy_sp, qty=quantity_entered,profitLossItem=temp)

# code for bill calculation starts here
                        bill_record = db(db.billCalculation.bill_id==bill_id_max).select()
                        if len(bill_record) == 0:
                            db.billCalculation.bill_date.default=request.now
                            db.billCalculation.insert(bill_id=bill_id_max)
                            customer_entered="Customer_" + str(bill_id_max)
                            bill_amt=dy_sp
                            bill_pl=temp
                            db.billCalculation.update_or_insert(db.billCalculation.bill_id==bill_id_max, bill_amount=bill_amt, profitLossBill=bill_pl, customer=customer_entered)
                        else:
                            for billrow in bill_record:
                                data_bill_amt = billrow.bill_amount
                                data_bill_pl = billrow.profitLossBill
                                bill_amt=float(data_bill_amt) + dy_sp
                                bill_pl=float(data_bill_pl) + temp
                                db.billCalculation.update_or_insert(db.billCalculation.bill_id==bill_id_max, bill_amount=bill_amt, profitLossBill=bill_pl)

# code for bill calculation ends here
                        redirect(URL('default', 'placeBill', args=[bill_id_max], vars=dict(from1='moreBt')))
                    else:
                        bill_id_max=request.args(0)
                        redirect(URL('default', 'placeBill', args=[bill_id_max], vars=dict(from1='noStock')))

    return locals()

@auth.requires(auth.has_membership('admin_group') or auth.has_membership('Cashier'))
def mailonBillCalc():
    bill_id_max=request.args(0)
    receive=request.vars['customer']
#     print receive
    bill_record = db(db.billCalculation.bill_id==bill_id_max).select()
    for billrow in bill_record:
        data_bill_amt = billrow.bill_amount
        time=billrow.bill_date
        amt=billrow.bill_amount
    mail.send(receive,'Your bill summary!','Hello Customer!,\nCustomer id: Customer_'+bill_id_max+'\nFollowing is your bill summary:\nBill No: '+bill_id_max+'\nTime: '+str(time)+'\n\nTotal expenditure: '+str(amt)+'\n\n')
    redirect(URL('default', 'cashierHome',vars=dict(from1='mailSent')))
    return dict(name='Cashier')

@auth.requires(auth.has_membership('admin_group') or auth.has_membership('Cashier'))
def generateReport():
    bill_month_dict=request.vars
    selected_month=bill_month_dict['mon_txt']
    redirect(URL('default', 'monthlyBillSummary', args=[selected_month]))
    return locals()

@auth.requires(auth.has_membership('admin_group') or auth.has_membership('Cashier'))
def monthlyBillSummary():
    selected_month=request.args(0)
    curr_year=request.now.year
#     (db.table.field1==x)&(db.table.field2==y)
    try:
        rows = db((db.billCalculation.bill_date.month()==selected_month)&(db.billCalculation.bill_date.year()==curr_year)).select()
    except ValueError:
        redirect(URL('default', 'cashierHome',vars=dict(from1='error')))

    return locals()

def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/manage_users (requires membership in
    http://..../[app]/default/user/bulk_register
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    return dict(form=auth())

@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()
