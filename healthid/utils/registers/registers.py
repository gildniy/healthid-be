def generate_register_id(outlet, register_id):
    register_id = (
        'RG'
        + ('0' if register_id < 10 else '')
        + str(register_id)
        + str(outlet.name[:2])
        + str(outlet.name[-1:])
    )
    return register_id.upper()
