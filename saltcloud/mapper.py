'''
Read in a vm map file. The map file contains a mapping of profiles to names
allowing for individual vms to be created in a more stateful way
'''

# Import python libs
import os
import copy
import multiprocessing

# Import salt libs
import saltcloud.cloud
import salt.client

# Import third party libs
import yaml


class Map(object):
    '''
    Create a vm stateful map execution object
    '''
    def __init__(self, opts):
        self.opts = opts
        self.cloud = saltcloud.cloud.Cloud(self.opts)
        self.map = self.read()

    def read(self):
        '''
        Read in the specified map file and return the map structure
        '''
        if not self.opts['map']:
            return {}
        if not os.path.isfile(self.opts['map']):
            return {}
        try:
            with open(self.opts['map'], 'rb') as fp_:
                map_ = yaml.load(fp_.read())
        except Exception:
            return {}
        if 'include' in map_:
            map_ = salt.config.include_config(map_, self.opts['map'])
        return map_

    def run_map(self):
        '''
        Execute the contents of the vm map
        '''
        for profile in self.map:
            for name in self.map[profile]:
                for vm_ in self.opts['vm']:
                    if vm_['profile'] == profile:
                        tvm = copy.deepcopy(vm_)
                        tvm['name'] = name
                        if self.opts['parallel']:
                            multiprocessing.Process(
                                    target=lambda: self.cloud.create(tvm)
                                    ).start()
                        else:
                            self.cloud.create(tvm)
