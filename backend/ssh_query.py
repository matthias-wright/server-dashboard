import paramiko
import socket
import time
import json
import yaml
import multiprocessing
from pebble import ProcessPool, ProcessExpired
from concurrent.futures import TimeoutError


class SSHQuery:

    def __init__(self, path_to_key, username, path_to_server_conf, proc_timeout=10, ssh_timeout=5, only_gpu_processes=True, num_threads=None):
        self.path_to_key = path_to_key
        self.username = username
        self.server_conf = yaml.safe_load(open(path_to_server_conf))
        self.proc_timeout = proc_timeout
        self.ssh_timeout = ssh_timeout
        self.num_threads = multiprocessing.cpu_count() if num_threads is None else num_threads
        self.only_gpu_processes = only_gpu_processes

    def query_gpus(self):
        
        with ProcessPool(max_workers=self.num_threads) as pool:
            future = pool.map(self._query_gpus_worker, self.server_conf.keys(), timeout=self.proc_timeout)
            
            iterator = future.result()
            server_list = []

            while True:
                try:
                    result = next(iterator)
                    if result is not None:
                        server_list.append(result)
                except StopIteration:
                    break
                except TimeoutError as error:
                    pass
                except Exception as e:
                    print(e)

            return server_list

    def query_processes(self):

        with ProcessPool(max_workers=self.num_threads) as pool:
            future = pool.map(self._query_processes_worker, self.server_conf.keys(), timeout=self.proc_timeout)
            iterator = future.result()
            processes_list = []

            while True:
                try:
                    result = next(iterator)
                    if result is not None:
                        processes_list.extend(result)
                except StopIteration:
                    break
                except TimeoutError as error:
                    pass
                except Exception as e:
                    print(e)

            return processes_list
       
    def query_users(self):
        server_list = self.query_gpus()
        users_dict = {}
        for server in server_list:
            for gpu in server['gpus']:
                user_set = set()
                for proc in gpu['processes']:
                    if not proc['username'] in users_dict:
                        users_dict[proc['username']] = {}
                        users_dict[proc['username']]['username'] = proc['username']
                        users_dict[proc['username']]['num_gpus'] = 0
                        users_dict[proc['username']]['gpu_ram'] = 0
                    
                    user_set.add(proc['username'])
                    users_dict[proc['username']]['gpu_ram'] += proc['gpu_memory_usage']
                for username in user_set:
                    users_dict[username]['num_gpus'] += 1

        users_list = list(users_dict.values())
        return users_list

    def _query_gpus_worker(self, server_name):
        if not self.server_conf[server_name]['active']:
            # server not active, don't connect
            return

        key = paramiko.RSAKey(filename=self.path_to_key)
        client = paramiko.SSHClient()
        client.load_system_host_keys()
        client.get_host_keys().add('key', 'ssh-rsa', key)
        try:
            client.connect(self.server_conf[server_name]['hostname'], 
                           username=self.username, 
                           timeout=self.ssh_timeout,
                           banner_timeout=self.ssh_timeout,
                           auth_timeout=self.ssh_timeout)
            stdin, stdout, stderr = client.exec_command('gpustat --json')
            stdin.close()

            json_str = ''
            for line in stdout:
                json_str += line
            json_obj = json.loads(json_str)

            # replace dots in keys with underscores
            server_dict = {}
            for server_key in json_obj.keys():
                if server_key == 'gpus':
                    gpu_list = []
                    for gpu in json_obj['gpus']:
                        gpu_new = {}
                        for gpu_key in gpu.keys():
                            gpu_new[gpu_key.replace('.', '_')] = gpu[gpu_key] if gpu[gpu_key] is not None else 'None'
                        # sort processes according to their gpu memory usage
                        gpu_new['processes'].sort(key=lambda x : x['gpu_memory_usage'], reverse=True)
                        gpu_list.append(gpu_new)
                    server_dict[server_key] = gpu_list
                else:
                    server_dict[server_key] = json_obj[server_key]
            
            client.close()
            return server_dict 
        except:
            pass
        client.close()

    def _query_processes_worker(self, server_name):
        if not self.server_conf[server_name]['active']:
            # server not active, don't connect
            return

        key = paramiko.RSAKey(filename=self.path_to_key)
        client = paramiko.SSHClient()
        client.load_system_host_keys()
        client.get_host_keys().add('key', 'ssh-rsa', key)
        try:
            client.connect(self.server_conf[server_name]['hostname'], 
                           username=self.username, 
                           timeout=self.ssh_timeout,
                           banner_timeout=self.ssh_timeout,
                           auth_timeout=self.ssh_timeout)

            if self.only_gpu_processes:
                # collect the PIDs from all processes that are executed on GPUs
                stdin, stdout, stderr = client.exec_command('gpustat --json')
                stdin.close()

                json_str = ''
                for line in stdout:
                    json_str += line
                json_obj = json.loads(json_str)
                pid_set = set()
                for gpu in json_obj['gpus']:
                    for proc in gpu['processes']:
                        pid_set.add(proc['pid'])

            stdin, stdout, stderr = client.exec_command('ps aux')
            stdin.close()

            header = next(stdout)
            header = [x for x in header.strip().lower().split(' ') if x != '']
            header[2] = header[2][1:]
            header[3] = header[3][1:]

            process_list = []
            for line in stdout:
                cols = line.strip().split(None, 10)
                if self.only_gpu_processes:
                    if not int(cols[1]) in pid_set:
                        continue

                process_dict = {}
                process_dict['server'] = server_name
                for i in range(len(header)):
                    process_dict[header[i]] = cols[i]
                process_list.append(process_dict)
            
            client.close()
            return process_list 
        except:
            pass
        client.close()
