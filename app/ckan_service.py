__author__ = 'guillermo'
import ckanapi
import os
from parser import Parser


class ReceiverCKANService(object):
    """
    Service that gets the file input from the html request and uploads it to CKAN
    instance
    """
    def __init__(self, content, api_key):
        self.parser = Parser(content)
        self.api_key = api_key

    def run_service(self, file_, ckan_instance):
        ckan_site = ckanapi.RemoteCKAN(ckan_instance, apikey=self.api_key)
        org = self._create_organization(ckan_site)
        data_set = self._create_package(org=org, site=ckan_site)
        self._create_resource(data_set=data_set, file_=file_, site=ckan_site)

    def _create_organization(self, site):
        print "Creating organization ..."
        org_name = self.parser.get_organization().name
        org_uri = self.parser.get_organization().id.lower()
        org_desc = self.parser.get_organization().description
        organizations = site.action.organization_list(order_by="name")
        if org_uri not in organizations:
            site.action.organization_create(name=org_uri, title=org_name,
                                            description=org_desc)
        return org_uri

    def _create_package(self, org, site):
        print "Creating dataset ..."
        data_set_id = self.parser.get_dataset().id
        data_set_uri = self.parser.get_dataset().id.lower()
        data_sets = site.action.package_list()
        if org and data_set_uri not in data_sets:
            site.action.package_create(name=data_set_uri, title=data_set_id,
                                       owner_org=org)
        return data_set_uri

    def _create_resource(self, data_set, site, file_):
        print "Uploading file ..."
        file_name = file_.filename
        path = os.path.join('datasets', file_.filename)
        file_.save(path)
        url = self.parser.get_file_name()
        site.action.resource_create(package_id=data_set, upload=open(path),
                                    name=file_name, url=url)
