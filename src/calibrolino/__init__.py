from varboxes import VarBox


varbox = VarBox('calibrolino')
if not hasattr(varbox, 'last_push_date'):
    varbox.last_push_date = 0

