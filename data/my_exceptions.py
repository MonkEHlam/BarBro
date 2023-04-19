from flask import abort


class DBTypeError(Exception):
    def __init__(self, table):
        print(f"Type error in DB, table - {table}")
        abort(202)
