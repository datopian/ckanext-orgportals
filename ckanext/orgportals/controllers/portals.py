from ckan.controllers.package import PackageController
from ckan import plugins


class OrgportalsControler(PackageController):
    def homepage_show(self, name):
        return plugins.toolkit.render('portals/pages/home.html')

    def datapage_show(self, name):
        return plugins.toolkit.render('portals/pages/data.html')

    def aboutpage_show(self, name):
        return plugins.toolkit.render('portals/pages/about.html')

    def contactpage_show(self, name):
        return plugins.toolkit.render('portals/pages/contact.html')

    def glossarypage_show(self, name):
        return plugins.toolkit.render('portals/pages/glossary.html')

    def helppage_show(self, name):
        return plugins.toolkit.render('portals/pages/help.html')

    def resourcespage_show(self, name):
        return plugins.toolkit.render('portals/pages/resources.html')
