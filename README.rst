------------------------
Development installation
------------------------

To install ckanext-orgportals for development, activate your CKAN virtualenv and
do::

    git clone https://github.com/ViderumGlobal/ckanext-orgportals.git
    cd ckanext-orgportals
    python setup.py develop
    pip install -r requirements.txt


---------------
Config settings
---------------

Add the extension to the plugins::

    ckanext.plugins = ... orgportals

Add storage path for uploading assets as well as storing temp images for Twitter::

    ckan.storage_path = /path/to/storage

Add entity name for organization (default is organization). This setting can either be set to ``country`` or ``organization``. If you set
it to ``country`` it will use text references for "Country/Countries" instead of
"Organization/Organizations" throughout the web interface. Though, this only
applies to certain parts of the UI. For some, you have to manually override/extend
the templates.
::

    ckanext.orgdashboards.organization_entity_name = country

Add entity name for group (default is group). This setting can either be set to ``group`` or ``topic``. If you set
it to ``topic`` it will use text references for "Topic/Topics" instead of
"Group/Groups" throughout the web interface. Though, this only applies to
certain parts of the UI. For some, you have to manually override/extend the
templates.::

    ckanext.orgdashboards.group_entity_name = topic

Add Facebook App ID to share a graph on Facebook::

    ckanext.orgportals.facebook_app_id = ...

Add Twitter consumer keys to share a graph on Twitter::

    ckanext.orgportals.twitter_consumer_key = ...
    ckanext.orgportals.twitter_consumer_secret = ...

Add email settings for contact form::

    ckanext.orgportals.smtp.mail.from = ...
    ckanext.orgportals.smtp.server = ...
    ckanext.orgportals.smtp.user = ...
    ckanext.orgportals.smtp.password = ...

Add number of datasets to show in data section in the portal (default is 5)::

    ckanext.orgdashboards.datasets_per_page = 10

Add ``ckanext.orgdashboards.custom_dns_active`` as a setting in the
config file::

    ckanext.orgdashboards.custom_dns_active = true

This setting enables functionality for adding custom domain for individual dashboards.

------------------------------
Installation of a new language
------------------------------

In order to use languages that are not supported by CKAN, you have to install
them manually. Open up a terminal inside the CKAN's source directory, and type
the following command to initialize a new catalog for a language::

    python setup.py init_catalog --locale YOUR_LANGUAGE

where ``YOUR_LANGUAGE`` is the locale of the language. This command will
create a ``.po`` file inside ``ckan/i18n/YOUR_LANGUAGE/LC_MESSAGES``
which contains the strings for the language.

Next you have to compile tha language into a binary format with the following
command::

    python setup.py compile_catalog --locale YOUR_LANGUAGE

where ``YOUR_LANGUAGE`` is the locale of the language. This command will
create a ``.mo`` file, and the one which CKAN will read the strings from.

------------------------
Language translation
------------------------

If you want to add additional strings for a certain language and translate
them, then follow these instructions:

1. Switch to the extension's directory and add a directory to store your
translations::

    mkdir ckanext/orgportals/i18n

2. Extract the strings from the extension with this
command::

    python setup.py extract_messages

This will create a template ``.po`` file named
``ckanext/orgportals/i18n/ckanext-orgportals.pot``

3. The next step is to create the translations. Let's say that you want to
translate strings for the ``de`` locale. Create the translation ``.po`` file
for the locale that you are translating for by running ``init_catalog``::

    python setup.py init_catalog -l de

This will generate a file called ``i18n/de/LC_MESSAGES/ckanext-orgportals.po``.
It contains every string extracted from the extension. For example, if you want
to translate the string ``Groups``, locate it in the ``.po`` file and type the
appropriate translation::

    msgid "Groups"
    msgstr "Gruppen"

A ``.po`` file can also be edited using a special program for translation called
`Poedit <https://poedit.net/>`_.

4. Once you are done with translation, next step is to compile the catalog with
the ``compile_catalog`` command::

    python setup.py compile_catalog -l de

This will create a binary ``.mo`` file named
``ckanext/orgportals/i18n/ckanext-orgportals.mo`` containing your
translations.

Once you have added the translated strings, you will need to inform CKAN that
your extension is translated by implementing the ``ITranslation`` interface in
your extension. Edit your ``plugin.py`` to contain the following::

    from ckan.lib.plugins import DefaultTranslation


    class YourPlugin(plugins.SingletonPlugin, DefaultTranslation):
        plugins.implements(plugins.ITranslation)

Restart the server and you should find that switching to the ``de`` locale in
the web interface should change the ``Groups`` string.

More information on translating extensions can be found on the offical
documentation on CKAN.

Additional flags for countries can be taken from http://flag-icon-css.lip.is

-----------------
Running the Tests
-----------------

Some of the tests require that you run a CKAN server, the one where the
orgdashboards extension is installed.

First create a new database called ``ckan_test`` if you haven't already, and
in the config file for the server change the ``sqlalchemy.url`` to point to the
database ``ckan_test``. This database will be used by the tests.

And second, set a storage path in the config file where uploaded resources will
be stored.

ckan.storage_path = /path/to/storage

Also, make sure to install the dev requirements for running the tests::

    pip install -r /usr/lib/ckan/default/src/ckan/dev-requirements.txt

To run the tests, change the current working directory to the extension and do::

    nosetests --ckan --with-pylons=test.ini
