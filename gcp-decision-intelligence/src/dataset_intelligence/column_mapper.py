class ColumnMapper:

    def __init__(self, columns):
        self.columns = columns

    def map_columns(self):

        standard_columns = {
            "customer_id": [
                "customer_id",
                "cust_id",
                "customerid",
                "customer id",
                "client_id",
                "buyer_id"
            ],

            "order_id": [
                "order_id",
                "orderid",
                "order id",
                "purchase_id",
                "transaction_id"
            ],

            "product_id": [
                "product_id",
                "productid",
                "product id",
                "item_id"
            ],

            "payment_value": [
                "payment_value",
                "payment",
                "amount",
                "price",
                "cost"
            ]
        }

        mapped_columns = {}

        lower_columns = [col.lower().strip() for col in self.columns]

        for standard_name, aliases in standard_columns.items():

            found = None

            for alias in aliases:

                if alias.lower() in lower_columns:
                    found = self.columns[lower_columns.index(alias.lower())]
                    break

            mapped_columns[standard_name] = found

        return mapped_columns