

def is_account_registration_compelet(account):
    return bool(
        account.phone_number and account.is_phone_verified
    )





def is_account_registration_complete(account):
    return bool(
        account.phone_number and account.is_phone_verified
    )


def register_by_verified_phone(account, phone_number, first_name=None, last_name=None):
    if not phone_number:
        raise ValueError("phone_number is required")

    update_fields = []

    account.phone_number = phone_number
    update_fields.append("phone_number")

    account.is_phone_verified = True
    update_fields.append("is_phone_verified")

    if first_name and not account.first_name:
        account.first_name = first_name
        update_fields.append("first_name")

    if last_name and not account.last_name:
        account.last_name = last_name
        update_fields.append("last_name")

    account.is_registration_completed = is_account_registration_complete(account)
    update_fields.append("is_registration_completed")

    account.save(update_fields=update_fields)

    return account
