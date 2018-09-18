from motor import MotorClient


class DatabaseClient:

    def __init__(self):
        self.client = MotorClient()

        self.withdraw_db = self.client.withdraw_db

        self.available_tokens = self.withdraw_db.available_tokens
        self.withdraw_requests = self.withdraw_db.withdraw_requests
        self.withdraw_custom_token_requests = self.withdraw_db.withdraw_custom_token_requests
        self.create_token_requests = self.withdraw_db.create_token_requests

        self.executed_withdraws = self.withdraw_db.executed_withdraws

        self.withdraw_db["tokens"].create_index("contract_address", unique=True)
