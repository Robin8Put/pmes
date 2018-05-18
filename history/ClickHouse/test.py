from jsonrpcclient.http_client import HTTPClient


history_host = "http://192.168.1.92:8002/api/history"

client = HTTPClient(history_host)

# client.request(method_name="create_table", table='new_test',
#                fields={'id': ['int(32, signed)', 'yes'], 'field1': ['string', 'no'], 'field2': ['float(32)', 'no']})


# client.request(method_name="integrity", table='orders', order_id=1)

# client.request(method_name="insert", table="new_test1",
#                fields={'id': '1241', 'uid': 32, 'coinid': 'QTUM', 'amount': 10.0})
#
client.request(method_name="refill_inc",  uid=12345, value=10, coinid="LTC")
#
#
# client.request(method_name="refill_from_history", uid=1, coinid="QTUM")

# client.request(method_name="select", fields="uid, amount", table="Refill", query="")
#
# client.request(method_name="drop", table="Refill")


# client.request(method_name="create_table", table='Refill',
#                     fields={'id': ['string', 'yes'], 'uid': ['int(32, signed)', 'no'],
#                         'coinid': ['string', 'no'], 'amount': ['float(32)', 'no']})

# client.request(method_name="insert", table="Refill",
#                fields={
#                     'id': sha256(str(datetime.datetime.now()).encode()).hexdigest(),
#                     'uid': 1,
#                     'coinid': "QTUM",
#                     'amount': 10.0
#                                 })

# import re
#
# list=['tx_bN_345121','a dog31','a yacht52','cats', 'tx_bN_341']
#
#
# tx_indexes = [list[i] for i, item in enumerate(list) if re.search(r"\btx\w*?\d+\b", item)]
#
# tx_idx = [re.findall('\d+', i)[0] for i in tx_indexes]

# import re
#
# fields = {'field': ['string', 'unique'], 'field1': ['int(32, signed)', 'yes'],
# 'field2': ['int(8, signed)', 'no'], 'field3': ['float(64)', 'yes']}

# query = '('
# indexed_fields = ''
# unique_field = ''
#
# for key, value in fields.items():
#     non_case_field = value[0][0:value[0].find('(')]
#
#     if non_case_field == 'int':
#         sign = value[0][value[0].find(',')+1:-1:].strip()
#         if sign == 'signed':
#             field_type = 'Int'
#         else:
#             field_type = 'UInt'
#
#         bits = re.findall('\d+', value[0])[0]
#         field = key + ' ' + field_type + bits
#         query += field + ','
#
#     elif non_case_field == 'strin':
#         field_type = 'String'
#         field = key + ' ' + field_type
#         query += field + ','
#
#     elif non_case_field == 'float':
#         field_type = 'Float'
#         bits = re.findall('\d+', value[0])[0]
#         field = key + ' ' + field_type + bits
#         query += field + ','
#
#     if value[1] == 'yes':
#         indexed_fields += key + ' '
#
#     elif value[1] == 'unique':
#         unique_field = key
#
# query = query[:-1:] + ')'
#
# print(indexed_fields)
# print(unique_field)
# print(query)

# import datetime
# fields = {'field': 'kek', 'field1': 1, 'field2': '123', 'field3': 1.0}
#
# query = '('
#
# for key in fields.keys():
#     query += key + ','
#
# date = datetime.datetime.now().date()
# query = query[:-1:] + ")"
# print(query)
