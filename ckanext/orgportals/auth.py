import ckan.plugins as p

def sysadmin(context, data_dict):
    return {'success':  False}

def org_admin(context, data_dict):
    return p.toolkit.check_access('group_update', context, data_dict)


pages_show = org_admin
pages_update = org_admin
pages_delete = org_admin
pages_list = org_admin