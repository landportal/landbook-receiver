__author__ = 'guillermo'
import ckanapi
import os
from parser import Parser


class ReceiverCKANService(object):
    """
    Service that gets the file input from the html request and uploads it to CKAN
    instance
    """
    def __init__(self, content):
        self.parser = Parser(content)

    def run_service(self, api_key, _file, ckan_instance):
        path = os.path.join('datasets', _file.filename)
        dataset_uri = self.parser.get_file_name().replace("._xml", "")
        org_name = self.parser.get_organization().name
        org_uri = self.parser.get_organization().id
        _file.save(path)
        ckan_site = ckanapi.RemoteCKAN(ckan_instance, apikey=api_key)
        ckan_site.action.organization_create(name=org_uri,
                                             title=org_name)
        ckan_site.action.package_create(name=dataset_uri,
                                        title=self.parser.get_dataset().id,
                                        notes="Dataset Description",
                                        owner_org=org_uri)

        ckan_site.action.resource_create(package_id=dataset_uri,
                                         upload=open(path), name="ResourceName")

