import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit


class OrgportalsPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IRoutes, inherit=True)

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'orgportals')

    # IRoutes

    def before_map(self, map):
        ctrl = 'ckanext.orgportals.controllers.portals:OrgportalsControler'

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
