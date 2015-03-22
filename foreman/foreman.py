'''
Created on 04.03.2015

@author: tkrah
'''

import json
import requests
# from requests.auth import HTTPBasicAuth
requests.packages.urllib3.disable_warnings()

FOREMAN_REQUEST_HEADERS = {'content-type': 'application/json', 'accept': 'application/json'}
FOREMAN_API_VERSION = 'v2'

ARCHITECTURES = 'architectures'
ARCHITECTURE = 'architecture'
COMMON_PARAMETERS = 'common_parameters'
COMMON_PARAMETER = 'common_parameter'
COMPUTE_ATTRIBUTES = 'compute_attributes'
COMPUTE_ATTRIBUTE = 'compute_attribute'
COMPUTE_PROFILES = 'compute_profiles'
COMPUTE_PROFILE = 'compute_profile'
COMPUTE_RESOURCES = 'compute_resources'
COMPUTE_RESOURCE = 'compute_resource'
CONFIG_TEMPLATES = 'config_templates'
CONFIG_TEMPLATE = 'config_template'
DOMAINS = 'domains'
DOMAIN = 'domain'
ENVIRONMENTS = 'environments'
ENVIRONMENT = 'environment'
HOSTS = 'hosts'
HOST = 'host'
HOSTGROUPS = 'hostgroups'
HOSTGROUP = 'hostgroups'
LOCATIONS = 'locations'
LOCATION = 'location'
MEDIA = 'media'
MEDIUM = 'medium'
OPERATINGSYSTEMS = 'operatingsystems'
OPERATINGSYSTEM = 'operatingsystem'
ORGANIZATIONS = 'organizations'
ORGANIZATION = 'organization'
PARTITION_TABLES = 'ptables'
PARTITION_TABLE = 'ptable'
SMART_PROXIES = 'smart_proxies'
SMART_PROXY = 'smart_proxy'
SUBNETS = 'subnets'
SUBNET = 'subnet'

class ForemanError(Exception):
    """ForemanError Class

    Simple class to handle exceptions while communicating to Foreman API
    """
    def __init__(self, url, request, status_code, message):
        self.url = url
        self.status_code = status_code
        self.message = message
        self.request = request
        super(ForemanError, self).__init__()

class Foreman:
    """Foreman Class

    Communicate with Foreman via API v2

    """
    def __init__(self, hostname, port, username, password):
        """Init
        """
        self.__auth = (username, password)
        self.hostname = hostname
        self.port = port
        self.url = 'https://' + self.hostname + ':' + self.port + '/api/' + FOREMAN_API_VERSION

    def _get_resource_url(self, resource_type, resource_id=None, component=None, component_id=None):
        """Create API URL path

        Args:
          resource_type (str): Name of resource to request
          resource_id (str): Resource identifier
          component (str): Component of a resource (e.g. images in /host/host01.example.com/images)
          component_id (str): Component identifier (e.g. nic01 in /host/host01.example.com/interfaces/nic1)
        """
        url = self.url + '/' + resource_type
        if resource_id:
            url = url + '/' + str(resource_id)
            if component:
                url = url + '/' + component
                if component_id:
                    url = url + '/' + str(component_id)
        return url

    def _get_request(self, url, data=None):
        """Execute a GET request agains Foreman API

        Args:
          resource_type (str): Name of resource to get
          component (str): Name of resource components to get
          component_id (str): Name of resource component to get
          data (dict): Dictionary to specify detailed data
        Returns:
          Dict
        """
        req = requests.get(url=url,
                           data=data,
                           auth=self.__auth,
                           verify=False)
        if req.status_code == 200:
            return json.loads(req.text)

        raise ForemanError(url=req.url,
                           status_code=req.status_code,
                           message=req.json().get('error').get('message'),
                           request=req.json())

    def _post_request(self, url, data):
        """Execute a POST request agains Foreman API

        Args:
          resource_type (str): Name of resource type to post
          component (str): Name of resource to post
          data (dict): Dictionary containing component details
        Returns:
          Dict
        """
        req = requests.post(url=url,
                            data=json.dumps(data),
                            headers=FOREMAN_REQUEST_HEADERS,
                            auth=self.__auth,
                            verify=False)
        if req.status_code in [200, 201]:
            return json.loads(req.text)

        request_json = req.json()
        if request_json.has_key('error'):
            request_error = req.json().get('error')
            if request_error.has_key('message'):
                error_message = request_error.get('message')
            elif request_error.has_key('full_messages'):
                error_message = ', '.join(request_error.get('full_messages'))
            else:
                error_message = request_error
        else:
            error_message = str(request_json)

        raise ForemanError(url=req.url,
                           status_code=req.status_code,
                           message=error_message,
                           request=req.json())

    def _put_request(self, url, data):
        """Execute a PUT request agains Foreman API

        Args:
          resource_type (str): Name of resource type to post
          resource_id (str): Resource identified
          data (dict): Dictionary of details
        Returns:
          Dict
        """
        req = requests.put(url=url,
                           data=json.dumps(data),
                           headers=FOREMAN_REQUEST_HEADERS,
                           auth=self.__auth,
                           verify=False)
        if req.status_code == 200:
            return json.loads(req.text)
        raise ForemanError(url=req.url,
                           status_code=req.status_code,
                           message=req.json().get('error').get('message'),
                           request=req.json())

    def _delete_request(self, url):
        """Execute a DELETE request agains Foreman API

        Args:
          resource_type (str): Name of resource type to post
          resource_id (str): Resource identified
        Returns:
          Dict
        """
        req = requests.delete(url=url,
                              headers=FOREMAN_REQUEST_HEADERS,
                              auth=self.__auth,
                              verify=False)
        if req.status_code == 200:
            return json.loads(req.text)
        raise ForemanError(url=req.url,
                           status_code=req.status_code,
                           message=req.json().get('error').get('message'),
                           request=req.json())

    def get_resources(self, resource_type):
        """ Return a list of all resources of the defined resource type

        Args:
           resource_type: Type of reesources to get
        Returns:
           list of dict
        """
        request_result = self._get_request(url=self._get_resource_url(resource_type=resource_type))
        return request_result.get('results')

    def get_resource(self, resource_type, resource_id, component=None, component_id):
        """ Get information about a resource

        If data contains id the resource will be get directly from the API.
        If id is not specified but name the resource will be searched within the database.
        If found the id of the research will be used. If not found None will be returned.

        Args:
           resource_type (str): Resource type
           resource_id (str): Resource identified
           component (str): Component name to request
           component_id (int): Component id to request
        Returns:
           dict
        """
        return self._get_request(url=self._get_resource_url(resource_type=resource_type,
                                                            resource_id=resource_id,
                                                            component=component,
                                                            component_id=component_id))

    def post_resource(self, resource_type, resource, data,
                      resource_id=None, component=None, additional_data=None):
        """ Execute a post request

        Execute a post request to create one <resource> of a <resource type>.
        Foreman expects usually the following content:

        {
          "<resource>": {
            "param1": "value",
            "param2": "value",
            ...
            "paramN": "value"
          }
        }

        <data> has to contain all parameters and values of the resource to be created.
        They are passed as {<resource>: data}.

        As not all resource types can be handled in this way <additional_data> can be
        used to pass more data in. All key/values pairs will be passed directly and
        not passed inside '{<resource>: data}.

        Args:
           data(dict): Hash containing parameter/value pairs
        """
        url = self._get_resource_url(resource_type=resource_type,
                                     resource_id=resource_id,
                                     component=component)
        resource_data = {}
        if additional_data:
            for key in additional_data.keys():
                resource_data[key] = additional_data[key]
        resource_data[resource] = data
        return self._post_request(url=url,
                                  data=resource_data)

    def put_resource(self, resource_type, resource_id, data, component=None):
        return self._put_request(url=self._get_resource_url(resource_type=resource_type,
                                                            resource_id=resource_id,
                                                            component=component),
                                 data=data)

    def delete_resource(self, resource_type, resource_id):
        return self._delete_request(url=self._get_resource_url(resource_type=resource_type,
                                                               resource_id=resource_id))

    def search_resource(self, resource_type, data=None):
        data = {}
        data['search'] = ''

        for key in data:
            if data['search']:
                data['search'] = data['search'] + ' AND '
            data['search'] = data['search'] + key + ' == '

            if isinstance(data[key], int):
                data['search'] = data['search'] + str(data[key])
            elif isinstance(data[key], str):
                data['search'] = data['search'] + '"' + data[key] + '"'

        results = self._get_request(url=self._get_resource_url(resource_type=resource_type), data=data)
        result = results.get('results')

        if len(result) == 1:
            return result[0]

        return result

    def get_architectures(self):
        return self.get_resources(resource_type=ARCHITECTURES)

    def get_architecture(self, id):
        return self.get_resource(resource_type=ARCHITECTURES, resource_id=id)

    def set_architecture(self, data):
        return self.post_resource(resource_type=ARCHITECTURES, resource=ARCHITECTURE, data=data)

    def create_architecture(self, data):
        return self.set_architecture(data=data)

    def delete_architecture(self, id):
        return self.delete_resource(resource_type=ARCHITECTURES, resource_id=id)

    def get_common_parameters(self):
        return self.get_resources(resource_type=COMMON_PARAMETERS)

    def get_common_parameter(self, id):
        return self.get_resource(resource_type=COMMON_PARAMETERS, resource_id=id)

    def set_common_parameter(self, data):
        return self.post_resource(resource_type=COMMON_PARAMETERS, resource=COMMON_PARAMETER, data=data)

    def create_common_parameter(self, data):
        return self.set_common_parameter(data=data)

    def delete_common_parameter(self, id):
        return self.delete_resource(resource_type=COMMON_PARAMETERS, resource_id=id)

    def get_compute_attributes(self, data):
        """
        Return the compute attributes of all compute profiles assigned to a compute resource

        Args:
           data(dict): Must contain the name of the compute resource in compute_resource.

        Returns:
           dict
        """
        compute_resource = self.get_compute_resource(data={'name': data.get(COMPUTE_RESOURCE)})
        if compute_resource:
            return compute_resource.get(COMPUTE_ATTRIBUTES)
        return None

    def get_compute_attribute(self, data):
        """
        Return the compute attributes of a compute profile assigned to a compute resource.

        Args:
           data (dict): Must contain the name of the compute profile in compute_profile
                        as well as the name of the compute_resource in compute_resource.

        Returns:
           dict
        """
        compute_attributes = self.get_compute_attributes(data=data)
        compute_profile = self.get_compute_profile(data={'name': data.get(COMPUTE_PROFILE)})

        return filter(lambda item: item.get('compute_profile_id') == compute_profile.get('id'), compute_attributes)

    def create_compute_attribute(self, data):
        """ Create compute attributes for a compute profile in a compute resource

        Args:
           data(dict): Must contain compute_resource_id, compute_profile_id and vm_attrs
        """
        addition_data = {}
        addition_data['compute_resource_id'] = data.get('compute_resource_id')
        addition_data['compute_profile_id'] = data.get('compute_profile_id')

        resource_data = {}
        resource_data['vm_attrs'] = data.get('vm_attrs')

        return self.post_resource(resource_type=COMPUTE_ATTRIBUTES, resource=COMPUTE_ATTRIBUTE,
                           data=resource_data,
                           additional_data=addition_data)

    def update_compute_attribute(self, data):
        return self.put_resource(resource_type=COMPUTE_ATTRIBUTES,
                                 resource_id=data.get('id'),
                                 data={'vm_attrs': data.get('vm_attrs')})

    def get_compute_profiles(self):
        return self.get_resources(resource_type=COMPUTE_PROFILES)

    def get_compute_profile(self, id):
        return self.get_resource(resource_type=COMPUTE_PROFILES, resource_id=id)

    def set_compute_profile(self, data):
        return self.post_resource(resource_type=COMPUTE_PROFILES, resource=COMPUTE_PROFILE, data=data)

    def create_compute_profile(self, data):
        return self.set_compute_profile(data=data)

    def delete_compute_profile(self, id):
        return self.delete_resource(resource_type=COMPUTE_PROFILES, resource_id=id)

    def get_compute_resources(self):
        return self.get_resources(resource_type=COMPUTE_RESOURCES)

    def get_compute_resource(self, id):
        return self.get_resource(resource_type=COMPUTE_RESOURCES, resource_id=id)

    def set_compute_resource(self, data):
        return self.post_resource(resource_type=COMPUTE_RESOURCES, resource=COMPUTE_RESOURCE, data=data)

    def create_compute_resource(self, data):
        return self.set_compute_resource(data=data)

    def delete_compute_resource(self, id):
        return self.delete_resource(resource_type=COMPUTE_RESOURCES, resource_id=id)

    def get_config_templates(self):
        return self.get_resources(resource_type=CONFIG_TEMPLATES)

    def get_config_template(self, id):
        return self.get_resource(resource_type=CONFIG_TEMPLATES, resource_id=id)

    def set_config_template(self, data):
        return self.post_resource(resource_type=CONFIG_TEMPLATES, resource=CONFIG_TEMPLATE, data=data)

    def create_config_template(self, data):
        return self.set_config_template(data=data)

    def delete_config_template(self, id):
        return self.delete_resource(resource_type=CONFIG_TEMPLATES, resource_id=id)

#    def get_compute_resource_images(self, name):
#        return self.get_compute_resource(name=name, component='images').get('results')

    def get_domains(self):
        return self.get_resources(resource_type=DOMAINS)

    def get_domain(self, id):
        return self.search_resource(resource_type=DOMAINS, resource_id=id)

    def set_domain(self, data):
        return self.post_resource(resource_type=DOMAINS, resource=DOMAIN, data=data)

    def create_domain(self, data):
        return self.set_domain(data=data)

    def delete_domain(self, id):
        return self.delete_resource(resource_type=DOMAINS, resource_id=id)

    def get_environments(self):
        return self.get_resources(resource_type=ENVIRONMENTS)

    def get_environment(self, id):
        return self.search_resource(resource_type=ENVIRONMENTS, resource_id=id)

    def set_environment(self, data):
        return self.post_resource(resource_type=ENVIRONMENTS, resource=ENVIRONMENT, data=data)

    def create_environment(self, data):
        return self.set_environment(data=data)

    def delete_environment(self, id):
        return self.delete_resource(resource_type=ENVIRONMENTS, resource_id=id)

    def get_hosts(self):
        return self.get_resources(resource_type=HOSTS)

    def get_host(self, id):
        return self.search_resource(resource_type=HOSTS, resource_id=id)

    def set_host(self, data):
        return self.post_resource(resource_type=HOSTS, resource=HOST, data=data)

    def create_host(self, data):
        return self.set_host(data=data)

    def delete_host(self, id):
        return self.delete_resource(resource_type=HOSTS, resource_id=id)

    def get_host_power(self, host_id):
        return self.put_resource(resource_type=HOSTS,
                                 resource_id=host_id,
                                 component='power',
                                 data={'power_action': 'state', HOST: {}})

    def poweron_host(self, host_id):
        return self.set_host_power(host_id=host_id, action='start')

    def poweroff_host(self, host_id):
        return self.set_host_power(host_id=host_id, action='stop')

    def reboot_host(self, host_id):
        return self.set_host_power(host_id=host_id, action='reboot')

#    def get_host_component(self, name, component, component_id=None):
#        return self.get_host(name=name, component=component, component_id=component_id)

#    def get_host_interfaces(self, name):
#        return self.get_host_component(name=name,
#                                       component='interfaces')

#    def get_host_interface(self, name, interface_id):
#        return self.get_host_component(name=name,
#                                       component='interfaces',
#                                       component_id=interface_id)

    def set_host_power(self, host_id, action):
        return self.put_resource(resource_type=HOSTS,
                                 resource_id=host_id,
                                 component='power',
                                 data={'power_action': action, HOST: {}})

    def get_host_parameters(self, host_id):
        parameters = self.get_resource(resource_type=HOSTS, resource_id=host_id, component='parameters')
        if parameters:
            return parameters.get('results')
        return None

    def create_host_parameter(self, host_id, data):
        return self.post_resource(resource_type=HOSTS,
                                  resource_id=host_id,
                                  resource='parameter',
                                  data=data,
                                  component='parameters')

    def get_hostgroups(self):
        return self.get_resources(resource_type=HOSTGROUPS)

    def get_hostgroup(self, id):
        return self.search_resource(resource_type=HOSTGROUPS, resource_id=id)

    def set_hostgroup(self, data):
        return self.post_resource(resource_type=HOSTGROUPS, resource=HOSTGROUP, data=data)

    def create_hostgroup(self, data):
        return self.set_hostgroup(data=data)

    def delete_hostgroup(self, id):
        return self.delete_resource(resource_type=HOSTGROUPS, resource_id=id)

    def get_locations(self):
        return self.get_resources(resource_type=LOCATIONS)

    def get_location(self, id):
        return self.search_resource(resource_type=LOCATIONS, resource_id=id)

    def set_location(self, data):
        return self.post_resource(resource_type=LOCATIONS, resource=LOCATION, data=data)

    def create_location(self, data):
        return self.set_location(data=data)

    def delete_location(self, id):
        return self.delete_resource(resource_type=LOCATIONS, resource_id=id)

    def get_media(self):
        return self.get_resources(resource_type=MEDIA)

    def get_medium(self, id):
        return self.search_resource(resource_type=MEDIA, resource_id=id)

    def set_medium(self, data):
        return self.post_resource(resource_type=MEDIA, resource=MEDIUM, data=data)

    def create_medium(self, data):
        return self.set_medium(data=data)

    def delete_medium(self, id):
        return self.delete_resource(resource_type=MEDIA, resource_id=id)

    def get_organizations(self):
        return self.get_resources(resource_type=ORGANIZATIONS)

    def get_organization(self, id):
        return self.search_resource(resource_type=ORGANIZATIONS, resource_id=id)

    def set_organization(self, data):
        return self.post_resource(resource_type=ORGANIZATIONS, resource=ORGANIZATION, data=data)

    def create_organization(self, data):
        return self.set_organization(data=data)

    def delete_organization(self, id):
        return self.delete_resource(resource_type=ORGANIZATIONS, resource_id=id)

    def get_operatingsystems(self):
        return self.get_resources(resource_type=OPERATINGSYSTEMS)

    def get_operatingsystem(self, id):
        return self.search_resource(resource_type=OPERATINGSYSTEMS, resource_id=id)

    def set_operatingsystem(self, data):
        return self.post_resource(resource_type=OPERATINGSYSTEMS, resource=OPERATINGSYSTEM, data=data)

    def create_operatingsystem(self, data):
        return self.set_operatingsystem(data=data)

    def delete_operatingsystem(self, id):
        return self.delete_resource(resource_type=OPERATINGSYSTEMS, resource_id=id)

    def get_partition_tables(self):
        return self.get_resources(resource_type=PARTITION_TABLES)

    def get_partition_table(self, id):
        return self.search_resource(resource_type=PARTITION_TABLES, resource_id=id)

    def set_partition_table(self, data):
        return self.post_resource(resource_type=PARTITION_TABLES, resource=PARTITION_TABLE, data=data)

    def create_partition_table(self, data):
        return self.set_partition_table(data=data)

    def delete_partition_table(self, id):
        return self.delete_resource(resource_type=PARTITION_TABLES, resource_id=id)

    def get_smart_proxies(self):
        return self.get_resources(resource_type=SMART_PROXIES)

    def get_smart_proxy(self, id):
        return self.search_resource(resource_type=SMART_PROXIES, resource_id=id)

    def set_smart_proxy(self, data):
        return self.post_resource(resource_type=SMART_PROXIES, resource=SMART_PROXY, data=data)

    def create_smart_proxy(self, data):
        return self.set_smart_proxy(data=data)

    def delete_smart_proxy(self, id):
        return self.delete_resource(resource_type=SMART_PROXIES, resource_id=id)

    def get_subnets(self):
        return self.get_resources(resource_type=SUBNETS)

    def get_subnet(self, id):
        return self.search_resource(resource_type=SUBNETS, resource_id=id)

    def set_subnet(self, data):
        return self.post_resource(resource_type=SUBNETS, resource=SUBNET, data=data)

    def create_subnet(self, data):
        return self.set_subnet(data=data)

    def delete_subnet(self, id):
        return self.delete_resource(resource_type=SUBNETS, resource_id=id)
