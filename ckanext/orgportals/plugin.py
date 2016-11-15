import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit


class OrgportalsPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IRoutes, inherit=True)
    plugins.implements(plugins.IActions)

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'orgportals')

    # IRoutes

    def before_map(self, map):
        ctrl = 'ckanext.orgportals.controllers.portals:OrgportalsController'

        map.connect('/organization/{name}/home', controller=ctrl,
                    action='homepage_show')
        map.connect('/organization/{name}/data', controller=ctrl,
                    action='datapage_show')
        map.connect('/organization/{name}/contact', controller=ctrl,
                    action='contactpage_show')
        map.connect('/organization/{name}/about', controller=ctrl,
                    action='aboutpage_show')
        map.connect('/organization/{name}/help', controller=ctrl,
                    action='helppage_show')
        map.connect('/organization/{name}/resources', controller=ctrl,
                    action='resourcespage_show')
        map.connect('/organization/{name}/glossary', controller=ctrl,
                    action='glossarypage_show')

        return map

    # IActions

    def get_actions(self):
        module_root = 'ckanext.orgportals.logic.action'
        action_functions = _get_logic_functions(module_root)

        return action_functions


def _get_logic_functions(module_root, logic_functions={}):
    module = __import__(module_root)

    for part in module_root.split('.')[1:]:
        module = getattr(module, part)

    for key, value in module.__dict__.items():
        if not key.startswith('_') and hasattr(value, '__call__')\
                and (value.__module__ == module_root):
                    logic_functions[key] = value

    return logic_functions
