__author__ = 'guillermo'
import ckanapi


class ReceiverCKANService(object):
    """
    Service that gets the file input from the html request and stores its content in
    CKAN instance
    """
    def upload_data_set(self, api_key, dataset_uri, dataset_title, dataset_files,
                        ckan_instance):
        ckan_site = ckanapi.RemoteCKAN(ckan_instance, apikey=api_key)
        ckan_site.action.package_create(name=dataset_uri, title=dataset_title)
        ckan_site.action.resource_create(package_id=dataset_uri,
                                         upload=open(dataset_files))

if __name__ == "__main__":
    ckan = 'http://localhost:1100/data/'
    key = '0ff3b240-181c-42fb-955b-66e9713d9012'
    uri = "_the_dataset"
    files = '../xml/test_file.xml'
    title = 'The Dataset Name'

    ReceiverCKANService().upload_data_set(ckan_instance=ckan, api_key=key,
                                          dataset_uri=uri, dataset_files=files,
                                          dataset_title=title)
