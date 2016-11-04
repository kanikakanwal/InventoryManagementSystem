# -*- coding: utf-8 -*-
db.define_table('category',
                Field('Bed'),
                Field('Chair'),
                Field('Tables'),
                Field('Almirah'),
                Field('Sofa'))



db.define_table('item',
                Field('item_name',requires=IS_IN_SET(['Bed', 'Chair','Tables','Almirah','Sofa'])),
                Field('item_category',requires=IS_IN_DB(db,db.category.Bed)),
                Field('cost_price',type='double',requires=IS_NOT_EMPTY()),
                Field('selling_price',type='double',requires=IS_NOT_EMPTY()),
                Field('vendor', requires=IS_IN_SET(['Vendor1', 'Vendor2','Vendor3','Vendor4','Vendor5']))
                )

db.define_table('orders',
                Field('item_id', db.item, requires=IS_NOT_EMPTY()),
                Field('purchase_date', type='datetime' ,requires=IS_NOT_EMPTY()),
                Field('status',requires=IS_IN_SET(['Stock_Ordered', 'Stock_Received','Stock_Added'])),
                Field('vendor', requires=IS_NOT_EMPTY())
                )

db.define_table('stock',
                Field('item_id', db.item, requires=IS_NOT_EMPTY()),
                Field('order_placing_flag', type='string', default='OFF'),
                Field('quantity', type='integer',requires=IS_NOT_EMPTY()),
                Field('item_threshold',type='integer',requires=IS_NOT_EMPTY()),
                )

db.define_table('bill',
                Field('bill_id', type='integer', requires=IS_NOT_EMPTY()),
                Field('item_id', db.item, requires=IS_NOT_EMPTY()),
                Field('price',type='double',requires=IS_NOT_EMPTY()),
                Field('bill_date', type='datetime' ,requires=IS_NOT_EMPTY()),
                Field('qty', type='integer' ,requires=IS_NOT_EMPTY()),
                Field('profitLossItem',type='double',requires=IS_NOT_EMPTY()),
               )

db.define_table('billCalculation',
                Field('bill_id', type='integer', requires=IS_NOT_EMPTY()),
                Field('bill_amount',type='double',requires=IS_NOT_EMPTY()),
                Field('bill_date', type='datetime' ,requires=IS_NOT_EMPTY()),
                Field('profitLossBill',type='double',requires=IS_NOT_EMPTY()),
                Field('customer', requires=IS_NOT_EMPTY())
               )
