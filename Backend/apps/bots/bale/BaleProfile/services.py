from apps.accounts.services.registeredbyphone import register_by_verified_phone


def sync_bale_basic_info_to_accounts(bale_profile):
    return register_by_verified_phone(
        account=bale_profile.account,
        phone_number=bale_profile.phone_number,
        first_name=bale_profile.profile_first_name,
        last_name=bale_profile.profile_last_name
    )
