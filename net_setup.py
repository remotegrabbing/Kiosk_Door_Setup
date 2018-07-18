#!/usr/bin/env python

import logging
import logging.handlers
import os
import re
import shutil
import sys

# Set up logging.
log_file = '/var/log/bis/net_setup.log'
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.handlers.WatchedFileHandler(log_file)
handler.setLevel(logging.INFO)
formatter = logging.Formatter(
    '%(asctime)s %(name)s %(levelname)s: %(message)s',
    '%b %d %H:%M:%S'
)
handler.setFormatter(formatter)
logger.addHandler(handler)

def get_hostname():
    hostname = raw_input('Please enter the hostname: ')
    confirm = raw_input('Is %s correct [y,n]? ' % (hostname,))
    while confirm != 'y':
        hostname = raw_input('Please enter the hostname: ')
        confirm = raw_input('Is %s correct [y,n]? ' % (hostname,))
    return hostname

def get_ip_address():
    ip_pattern = re.compile(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$')
    address = raw_input('IP address: ')
    while not ip_pattern.match(address):
        address = raw_input('Please enter a valid IP address: ')
    return address

def get_netmask():
    nm_pattern = re.compile(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$')
    netmask = raw_input('Netmask: ')
    while not nm_pattern.match(netmask):
        netmask = raw_input('Please enter a valid netmask: ')
    return netmask

def get_gateway():
    gw_pattern = re.compile(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$')
    gateway = raw_input('Default gateway: ')
    while not gw_pattern.match(gateway):
        gateway = raw_input('Please enter a valid default gateway: ')
    return gateway

if __name__ == '__main__':
    from optparse import OptionParser
    usage = '%prog'
    version = '%prog v0.10'
    parser = OptionParser(usage=usage, version=version)
    (options, args) = parser.parse_args()

    # Regex that matches basic IP structure.
    ip_pattern = re.compile(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$')

    # Checking if directories and files exist.
    if not os.path.isdir('/var/log/bis'):
        try:
            os.makedirs('/var/log/bis/')
        except OSError, e:
            print e

    # Question user for county / destination configuration.
    logger.info('-------[Start]------')
    logger.info('Starting location configuration')

    hostname = get_hostname()
    logger.info('Hostname Generated: %s', hostname)

    # Write hostname to file.
    hostname_file = open('applicants/hostname', 'w')
    hostname_file.write('%s\n' % (hostname,))
    hostname_file.close()

    # Network Configuration block.
    logger.info('Starting network configuration')
    print('Network Setup')
    print('(i) Please key in and press [ENTER] for each blank and category.')

    #Question user for network configuration | 'ip_cmp' is the regex | u/address u/netmask u/gateway is user input
    address = get_ip_address()
    logger.info('%s %s', '[USER INPUT] address: ', address)

    netmask = get_netmask()
    logger.info('%s %s', '[USER INPUT] netmask: ', netmask)

    gateway = get_gateway()
    logger.info('%s %s', '[USER INPUT] gateway: ', gateway)

    #Application of network settings.
    def check():
        interfaces_file = open('applicants/interfaces', 'r')
        found = False
        for line in interfaces_file:
            if "address" in line:
                found = True
                break
        return found
    found = check()

    if check():
        interfaces_file = open('applicants/interfaces', 'a')
        os.system("sudo cp -rv applicants/interfaces.new /etc/network/interfaces")
        interfaces_file.write('    address %s\n' % (address,))
        interfaces_file.write('    netmask %s\n' % (netmask,))
        interfaces_file.write('    gateway %s\n' % (gateway,))
        interfaces_file.close()
        os.system('cp -rv applicants/interfaces /etc/network/interfaces')
        logger.info('[NOTICE] Appended network properties')
    else:
        interfaces_file = open('applicants/interfaces', 'a')
        interfaces_file.write('    address %s\n' % (address,))
        interfaces_file.write('    netmask %s\n' % (netmask,))
        interfaces_file.write('    gateway %s\n' % (gateway,))
        interfaces_file.close()
        os.system('cp -rv applicants/interfaces /etc/network/interfaces')
        logger.info('[NOTICE] Appended network properties')

    #Copy the Iptables rules over.
    try:
        os.system('sudo iptables-restore < applicants/rules.v4')
        logger.info('[NOTICE] Appended iptables rules')
    except:
        pass
