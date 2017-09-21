import ckan.plugins as p

def sysadmin(context, data_dict):
    return {'success':  False}

def org_admin(context, data_dict):
    is_authorized = p.toolkit.check_access('group_update', context, data_dict)

    if isinstance(is_authorized, bool):
        return {'success': is_authorized}
    else:
        return is_authorized

def anyone(context, data_dict):
    return {'success': True}

if p.toolkit.check_ckan_version(min_version='2.2'):
    anyone = p.toolkit.auth_allow_anonymous_access(anyone)


pages_show = anyone
pages_update = org_admin
pages_delete = org_admin
pages_list = anyone

subdashboards_show = anyone
subdashboards_update = org_admin
subdashboards_delete = org_admin
subdashboards_list = anyone
