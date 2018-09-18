import functools

from jsonrpcserver.aio import methods
from handlers.withdraw import Withdraw
from handlers.withdraw_validator import WithdrawValidator
from handlers.signature_validator import SignatureValidator
from config import private_key, public_key, check_sig

withdraw_handler = Withdraw()


def sig_verify(func):

    signature_validator = SignatureValidator(private_key, public_key)

    @functools.wraps(func)
    async def func_wrapper(*args, **kwargs):

        if check_sig:
            try:
                signature_validator.verify(kwargs)
            except:
                return WithdrawValidator.error_403('Invalid signature')

            kwargs = signature_validator.hex_to_json(kwargs['message'])
            return signature_validator.sign(await func(*args, **kwargs))
        else:
            return await func(*args, **kwargs)
    return func_wrapper


@methods.add
@sig_verify
async def withdraw(*args, **kwargs):
    try:
        WithdrawValidator.validate_withdraw(kwargs)
    except Exception as e:
        return WithdrawValidator.error_400(str(e))

    try:
        request = await withdraw_handler.withdraw(*args, **kwargs)
    except Exception as e:
        return WithdrawValidator.error_500(str(e))
    return request


@methods.add
@sig_verify
async def withdraw_bulk(*args, **kwargs):
    try:
        WithdrawValidator.validate_withdraw(kwargs)
    except Exception as e:
        return WithdrawValidator.error_400(str(e))

    try:
        request = await withdraw_handler.withdraw_bulk(*args, **kwargs)
    except Exception as e:
        return WithdrawValidator.error_500(str(e))
    return request


@methods.add
@sig_verify
async def withdraw_custom_token(*args, **kwargs):

    try:
        WithdrawValidator.validate_withdraw_custom_token(kwargs)
    except Exception as e:
        return WithdrawValidator.error_400(str(e))

    try:
        request = await withdraw_handler.withdraw_custom_token(*args, **kwargs)
    except Exception as e:
        return WithdrawValidator.error_500(str(e))
    return request


@methods.add
@sig_verify
async def create_token(*args, **kwargs):

    try:
        WithdrawValidator.validate_create_token(kwargs)
    except Exception as e:
        return WithdrawValidator.error_400(str(e))

    try:
        request = await withdraw_handler.create_token(*args, **kwargs)
    except Exception as e:
        return WithdrawValidator.error_500(str(e))
    return request


@methods.add
async def is_valid_address(*args, **kwargs):
    try:
        WithdrawValidator.validate_is_valid_address(kwargs)
    except Exception as e:
        return WithdrawValidator.error_400(str(e))

    try:
        request = await withdraw_handler.is_valid_address(*args, **kwargs)
    except Exception as e:
        return WithdrawValidator.error_500(str(e))

    return request


@methods.add
@sig_verify
async def register_token(*args, **kwargs):
    try:
        WithdrawValidator.validate_register_token(kwargs)

    except Exception as e:
        return WithdrawValidator.error_400(str(e))

    try:
        request = await withdraw_handler.register_token(*args, **kwargs)
    except Exception as e:
        return WithdrawValidator.error_500(str(e))

    return request


@methods.add
async def available_tokens(*args, **kwargs):
    try:
        request = await withdraw_handler.available_tokens(*args, **kwargs)
    except Exception as e:
        return WithdrawValidator.error_500(str(e))

    return request


@methods.add
@sig_verify
async def send_to_cold_wallet(*args, **kwargs):
    try:
        WithdrawValidator.validate_withdraw(kwargs)
        WithdrawValidator.validate_cold_wallet_address(kwargs)
    except Exception as e:
        return WithdrawValidator.error_400(str(e))

    try:
        request = await withdraw_handler.withdraw(*args, **kwargs)
    except Exception as e:
        return WithdrawValidator.error_500(str(e))
    return request


@methods.add
async def hot_wallet_history(*args, **kwargs):
    try:
        request = await withdraw_handler.hot_wallet_history(*args, **kwargs)
    except Exception as e:
        return WithdrawValidator.error_500(str(e))

    return request

