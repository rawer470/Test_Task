from ninja import Schema


class RegisterIn(Schema):
    username: str
    password: str


class TokenOut(Schema):
    token: str
    username: str


class LoginIn(Schema):
    username: str
    password: str


class MessageOut(Schema):
    detail: str


class ErrorOut(Schema):
    detail: str
