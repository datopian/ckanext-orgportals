import ckan.logic.action.create as create_core


def organization_create(context, data_dict):

    return create_core.organization_create(context, data_dict)
