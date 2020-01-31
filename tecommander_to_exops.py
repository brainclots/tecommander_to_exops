# Script to allow running a TECommander command on ALL ExpertOps consoles
'''
Author:
            ___  ____ _ ____ _  _    _  _ _    ____ ___ ___
            |__] |__/ | |__| |\ |    |_/  |    |  |  |    /
            |__] |  \ | |  | | \|    | \_ |___ |__|  |   /__

            Tripwire MSE
            bklotz@tripwire.com

Originated: July 2019
Version 1.2
'''
import click
import subprocess
from  customer_dict import customer_dict
from pathlib import Path
import ctypes
import time
import tempfile
import os

tecmdr_windir = Path('C:/Program Files/Tripwire/tw-tecommander')
tecmdr = tecmdr_windir / 'bin' / 'tecommander.cmd'

@click.command()
@click.option('-c', '--customer', default='all', help='Name of customer or "all" is assumed')
@click.argument('script', type=click.File('r'))

def main(customer, script):
    '''
        This script will run a TECommander script against each ExpertOps console.
    '''
    start = time.time()
    # Read in the TECommander script they passed
    input = script.read().splitlines()
    # Loop through all customers
    if customer == 'all':
        customer_names = list(customer_dict.keys())
        customer_names.sort()
        # print(customer_names)
        for customer in customer_names:
                for line in input:
                    if "{CUSTOMER}" in line:
                        line = line.replace("{CUSTOMER}",customer)
                runtecmdr(customer, input)
    else:
        if customer in customer_dict.keys():
            for line in input:
                if "{CUSTOMER}" in line:
                    line = line.replace("{CUSTOMER}",customer)
            runtecmdr(customer, input)
        else:
            print(f'ERROR: \"{customer}\" is not a valid customer! \nRun \"customer_dict.py\" to see a list of valid customers.')
            exit(1)

    end = time.time()
    elapsed = str(round(end - start, 2))
    click.echo(f'Completed run in {elapsed} seconds.')


def runtecmdr(customer, input):
    cust_values = customer_dict[customer]
    auth_file = cust_values['auth_file']
    # Create a temporary file that will include the commands from the
    # TECommander script, each appended with the appropriate auth file
    # for that customer.
    with tempfile.TemporaryFile(mode='w+t', delete=False) as tf:
        for line in input:
            tf.write(f'{line} -M {auth_file} -q -Q\n')
        tf.close()
        try:
            # Run TECommander with the revised script
            subprocess.run(f'\"{tecmdr}\" @{tf.name} -q', shell=True)
            # Delete the temporary file
            os.remove(tf.name)
        except subprocess.CalledProcessError as err:
            print('Error: ', err)


if __name__ == '__main__':
    # Check to see if we are running as an administrator
    IsAdmin = ctypes.windll.shell32.IsUserAnAdmin()
    if IsAdmin == 0:
        click.echo('Please execute the script from an *Administrator* (elevated) command prompt')
        exit(1)

    main()
