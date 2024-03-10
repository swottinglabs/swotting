
def determine_platform_name_from_slug_code(slug_code: str):
    return slug_code.capitalize().replace('-', ' ').replace('_', ' ')