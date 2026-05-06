from varboxes import VarBox


default_values = dict(
    last_push_date=0,
    patches={},
    revision='',
)
varbox = VarBox('calibrolino')
for key, value in default_values.items():
    if not hasattr(varbox, key):
        setattr(varbox, key, value)
