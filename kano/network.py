#!/usr/bin/env python

# network.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License:   http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# This script benefits from the great work by Ovidiu Ciule, ovidiu.ciule@gmail.com
# PyWilist, a Python class module to parse wireless scanning
# information as returned by GNU/Linux iwlist tool.
# https://code.google.com/p/pywilist/   (Released under the MIT license)
#
# Common module for wireless support functions
#

'''
Common functions used by kano-wifi and kano-connect to get wireless networking up
'''

import os
import sys
import time
import subprocess
import shlex
import json
import re
import shutil
from kano.utils import run_cmd, get_user_unsudoed, run_bg, write_file_contents
from kano.logging import logger

DNS_FILE = '/etc/resolvconf/resolv.conf.d/base'
DNS_INTERFACES_FILE = '/etc/resolvconf/interface-order'
DNS_INTERFACES_BACKUP_FILE = '/etc/resolvconf/interface-order.backup'


class IWList():
    def __init__(self, interface, iwlist=None):
        '''
        For testing, <iwlist> can point to a file name which contains
        the output of a "iwlist" command, very useful to test remote complex network neighbourhoods.
        '''
        self.data = {}
        self.interface = interface
        self.refresh(iwlist=iwlist)

    def refresh(self, iwlist=None):

        def getRawData(interface, iwlist=None):
            '''
            Runs iwlist and gets WiFi data in a string
            Developped, tested with Wireless Extension v29 English translation, Nov 2007
            If iwlist points to a file, you can mimic iwlist from a response file for testing
            '''

            # Make sure the wlan interface is up, otherwise the network scan will not proceed
            run_cmd('ifconfig %s up' % interface)
            if iwlist:
                outdata = open(iwlist, 'r').read()
            else:
                # Contemplate those seldom cases where the dongle driver returns an empty list
                cstring = "iwlist " + interface + " scan"
                outdata, _, _ = run_cmd(cstring)

            return outdata

        def parseRawData(rawdata):
            # Parses a string containing the data printed by iwlist
            # Pre-condition: rawdata is not empty
            rawdatas = rawdata.split("\n")
            # Strip blanks
            # Let's separate by cells
            cellDataL = []
            #currentCell = None
            for s in rawdatas:
                # skip empty lines
                if not s.strip():
                    continue
                # If new cell:
                if s.lstrip().startswith("Cell "):
                    # log.debug("parseRawData: new cell")
                    cellDataL.append([])
                if len(cellDataL) > 0 and len(s) > 0:
                    cellDataL[len(cellDataL) - 1].append(s)

            # Data is separated by cells, now we'll parse each cell's data
            parsedCellData = {}
            for s in cellDataL:
                cellNumber, cellData = parseCellData("\n".join(s))
                parsedCellData[cellNumber] = cellData
            #log.debug("parseRawData: parsed "+str(len(cellDataL))+" cells")
            return parsedCellData

        def parseCellData(rawCellData):
            # Parses a string containing raw cell data
            # @return a tuble containing the cell's number and a dictionary with the data

            def getCellExtra(s):
                s = s.split(":")
                if len(s) > 2:
                    ret = ":".join(s[1:]).strip()
                else:
                    ret = s[1].strip()
                return ret

            def getCellIE(s):
                s = s.split(":")
                if len(s) > 2:
                    ret = ":".join(s[1:]).strip()
                else:
                    ret = s[1].strip()
                return ret

            def getCellNumber(s):
                return s.strip().split(" ")[1]

            def getCellFrequency(s):
                s = s.split(":")[1]
                return s.strip().split(" ")[0]

            def getCellChannel(s):
                return s.strip().split(" ")[3][0:-1]

            def getCellEncryption(s):
                return s.strip().split(":")[1]

            def getCellSignal(s):
                s = s.split("Signal level=")[1]
                return s.strip().split(" ")[0]

            def getCellNoise(s):
                try:
                    s = s.split("Noise level:")[1]
                    return s.strip().split(" ")[0]
                except:
                    return 0

            def getCellQuality(s):
                s = s.split("=")[1]
                return s.strip().split(" ")[0]

            def getCellMAC(s):
                return s.strip().split(" ")[4]

            def getCellESSID(s):
                return s.strip().split(":\"")[1][0:-1]

            def getCellProtocol(s):
                return s.strip().split(":")[1][-1]

            def getCellMode(s):
                return s.strip().split(":")[1]

            splitRawData = rawCellData.split("\n")

            # Provide default values for dongle drivers
            # which do not report all attributes that kano-wifi expects
            cellData = { 'ESSID':'', 'Channel':'', 'Signal':'0', 'Quality':'' }
            for s in splitRawData:
                if s.strip().startswith("Cell "):
                    cellData["Number"] = getCellNumber(s)
                    cellData["MAC"] = getCellMAC(s)
                if s.strip().startswith("ESSID:\""):
                    cellData["ESSID"] = getCellESSID(s)
                if s.strip().startswith("Protocol:"):
                    cellData["Protocol"] = getCellProtocol(s)
                if s.strip().startswith("Mode:"):
                    cellData["Mode"] = getCellMode(s)
                if s.strip().startswith("Mode:"):
                    cellData["Mode"] = getCellMode(s)
                if s.strip().startswith("Frequency:"):
                    cellData["Frequency"] = getCellFrequency(s)
                    cellData["Channel"] = getCellChannel(s)
                if s.strip().startswith("Quality="):
                    cellData["Quality"] = getCellQuality(s)
                    cellData["Signal"] = getCellSignal(s)
                    cellData["Noise"] = getCellNoise(s)
                if s.strip().startswith("Encryption key:"):
                    cellData["Encryption"] = getCellEncryption(s)

                if s.strip().startswith("IE"):
                    try:
                        ie = cellData["IE"]
                    except KeyError:
                        ie = []
                    ie.append(getCellIE(s))
                    cellData["IE"] = ie

                if s.strip().startswith("Extra:"):
                    try:
                        extra = cellData["Extra"]
                    except KeyError:
                        extra = []
                    extra.append(getCellExtra(s))
                    cellData["Extra"] = extra

            return cellData["Number"], cellData

        # keep scanning until at least one valid network is found
        tries = 0
        start_time = time.time()
        while not self.data and time.time() - start_time < 5:
            tries += 1

            # Get raw data as a string
            rawdata = getRawData(self.interface, iwlist)

            # Parse raw data into a dictionary
            if rawdata:
                self.data = parseRawData(rawdata)
                logger.debug('found {} networks in scanning loop'.format(len(self.data)))
            else:
                logger.debug('not found any networks in scanning loop'.format(len(self.data)))
                time.sleep(0.2)

        logger.error('found {} networks in {} tries in {} seconds'.format(len(self.data), tries, time.time() - start_time))

    def getList(self, unsecure=False, first=False, debug=False):
        '''
        Return a comfortable list of wireless networks
        sorted by signal strength (strongest first)
        '''

        def sortNetworks(adict):
            x, z = adict['quality'].split('/')
            factor = int(x) / float(z)
            return factor

        def add_wnet(wlist, new_wnet):
            for i, old_wnet in enumerate(wlist):
                if old_wnet["essid"] == new_wnet["essid"]:
                    try:
                        if int(old_wnet["signal"]) < int(new_wnet["signal"]):
                            wlist[i] = new_wnet
                    except:
                        # The signal format is not an integer, keep the old network
                        pass
                    # The network is duplicated, do not add it again
                    return
            # Add the network as it is not duplicated
            wlist.append(new_wnet)

        if debug:
            import pprint
            pp = pprint.PrettyPrinter(indent=4, depth=6)
            print 'Debug on: Dumping parsed wireless info:'
            pp.pprint(self.data)

        iwnets = []
        for number, ww in self.data.iteritems():

            # Basic signal information, excluding hidden SSIDs
            if 'ESSID' in ww:
                wnet = {
                    'essid': ww['ESSID'],
                    'channel': ww['Channel'],
                    'signal': ww['Signal'],
                    'quality': ww['Quality']
                }

                # Identify security information
                if ww['Encryption'] == 'off':
                    enc = 'off'
                else:
                    enc = 'wep'

                    # Look through Extra information data in search for WPA encryption flag
                    if 'Extra' in ww:
                        for xtra in ww['Extra']:
                            if xtra.upper().find('WPA') != -1:
                                enc = 'wpa'

                    # Same with the IE data chunks
                    if 'IE' in ww:
                        for ie in ww['IE']:
                            if ie.upper().find('WPA') != -1:
                                enc = 'wpa'

                if unsecure and enc != 'off':
                    pass
                else:
                    wnet['encryption'] = enc
                    add_wnet(iwnets, wnet)

        iwnets = sorted(iwnets, key=sortNetworks, reverse=True)
        if first:
            return iwnets[0:1]
        else:
            return iwnets


def is_device(iface):
    '''
    Returns True if wireless dongle is connected, False otherwise
    '''
    with open('/proc/net/dev', 'r') as f:
        read_data = f.read()
        if read_data.find(iface) != -1:
            return True

    return False


def is_ethernet_plugged(eth_device='eth0'):
    plugged = False
    try:
        with open('/sys/class/net/%s/operstate' % (eth_device), 'r') as f:
            if f.read().strip('\n').lower() == 'up':
                plugged = True
    except:
        pass

    return plugged


def is_connected(iface):
    '''
    Returns details on which wireless network we are currently associated.
    The linked variable tells us if Internet is reachable.
    '''
    essid = mode = ap = None
    linked = False

    out, err, _ = run_cmd("iwgetid %s --raw" % iface)
    essid = out.strip()

    out, err, _ = run_cmd("iwgetid %s --raw --ap" % iface)
    ap = out.strip()

    # mode 2 = Managed
    out, err, _ = run_cmd("iwgetid %s --raw --mode" % iface)
    out = out.strip()
    if out == '2':
        mode = 'Managed'
    else:
        mode = out

    # Association status can be queried via ifplugstatus,
    # but we are returning linked=True if Internet is actually up.
    linked = is_internet()

    return (essid, mode, ap, linked)


def is_gateway(iface):
    '''
    Find the default route gateway, try to contact it. Return True if responding
    '''
    out, _, _ = run_cmd("ip route show")
    guess_ip = re.match('^default via ([0-9\.]*) dev {}'.format(iface), out)
    if guess_ip:
        return True
    else:
        return False


def is_internet():
    '''
    Returns True if Internet is available, False otherwise
    '''
    _, _, rc = run_cmd('/usr/bin/is_internet')
    return rc == 0


def wpa_conf(essid, psk, confile, wep=False):
    '''
    Prepare and save a configuration file for WPA Supplicant daemon
    '''

    # Prepare settings section for WEP or WPA
    if wep is True:
        # If the key starts with "hex" lowercase, what follows is the Hexadecimal form
        # Otherwise it is in string form. Double quotes is how wpa_supplicant distinguishes.
        if psk.startswith('hex'):
            psk=psk[3:]
        else:
            # Escape single & double quotes manually
            psk = psk.replace ("'", "\'")
            psk = psk.replace ('"', '\"')
            psk='"%s"' % psk

        lines_wpa_conf = '''
          ctrl_interface=/var/run/wpa_supplicant
          network={
             ssid="%s"
             scan_ssid=1
             key_mgmt=NONE
             wep_key0=%s
             wep_tx_keyidx=0
             auth_alg=OPEN SHARED
         }
        ''' % (essid, psk)
    else:
        wpa_epilog = '''
          scan_ssid=1
          key_mgmt=WPA-EAP WPA-PSK IEEE8021X NONE
          pairwise=CCMP TKIP
         }
         ctrl_interface=/var/run/wpa_supplicant
        '''

        if psk.startswith('hex'):
            # In WPA hex mode, the provided key needs to go as is
            lines_wpa_conf = '''
             network={
               ssid="%s"
               psk=%s
               %s\n
            ''' % (essid, psk[3:], wpa_epilog)
        else:
            # In plain text form, the wpa_passphrase tool will give us
            # the passphrase and essid encoded correctly
            # and it carefully takes care of escaping single/double quotes for us
            try:
                wpa_conf = subprocess.check_output(['wpa_passphrase', essid, psk])
                wpa_conf += wpa_epilog
                lines_wpa_conf = []
                for line in wpa_conf.split('\n'):
                    if line.startswith('}'):
                        pass
                    else:
                        lines_wpa_conf.append(line + '\n')
            except:
                logger.error('Error calling wpa_passphrase to translate essid/psk pair')
                return False

    # save the WPA configuration file
    f=open(confile, 'wt')
    for k in lines_wpa_conf:
        f.write(k)
    f.close()
    return True


def reload_kernel_module(device_vendor='148f', device_product='5370', module='rt2800usb'):
    '''
    If the Kano USB deviceID is connected to the system, reload the kernel module. Returns True if reloaded.
    Works silently and ok even if the module is not currently loaded in the kernel.
    FIXME: This procedure should be called prior to connect() to circumvent current kernel module random problems.
    '''
    reloaded = False

    # Terminate wpa_supplicant daemon
    run_cmd('wpa_cli terminate')
    time.sleep(0.5)
    logger.info('wpa_cli has been terminated')

    _, _, rc = run_cmd('lsusb -d %s:%s' % (device_vendor, device_product))
    if rc == 0:
        # The device id is matched, reload the kernel driver
        rc_load = 0

        _, _, rc = run_cmd('rmmod "{}"'.format(module))
        time.sleep(0.5)
        rc_load += rc

        _, _, rc = run_cmd('modprobe "{}"'.format(module))
        time.sleep(5)
        rc_load += rc

        logger.info('Reloading wifi dongle kernel module "%s" for deviceID %s:%s rc=%d' %
                    (module, device_vendor, device_product, rc_load))
        if rc_load == 0:
            reloaded = True
    else:
        logger.info('Not reloading kernel module because device not found (%s:%s)' % (device_vendor, device_product))

    return reloaded


def connect(iface, essid, encrypt='off', seckey=None, wpa_custom_file=None):
    '''
    Attempts a wireless association with provided parameters.

    If wpa_custom_file is provided, it will point to a wpa_supplication configuration file.
    Essid, encrypt and seckey should be empty, and all parameters will be
    delegated to the WPA daemon with this configuration file.

    encrypt can either be "off", "wep" or "wpa"
    in the latter 2 cases, seckey should be the encryption key
    of the wireless network AP.
    '''

    if os.access('/var/run/kano-connect.pid', os.R_OK):
        client_module=sys.argv[0]
        if client_module.find('kano-connect') == -1:
            logger.info ('Cancelling kano-connect to give control to %s' % sys.argv[0])
            run_cmd('pkill -f kano-connect')
            time.sleep(1)

    udhcpc_cmdline = 'udhcpc -S -t 70 -A 20 -n -a --script=/etc/udhcpc/kano.script -i %s' % iface
    time.sleep(1)

    # kill previous connection daemons
    run_cmd("pkill -f '%s'" % (udhcpc_cmdline))

    # and wpa supllicant daemon, politely through wpa_cli
    run_cmd("wpa_cli terminate")

    #
    # Set the ESSID of the wireless network to associate
    # escaping single / double quotation marks
    #
    escaped_essid = essid.replace("'", "\'")
    escaped_essid = escaped_essid.replace('"', '\"')

    run_cmd("iwconfig %s power off" % iface)
    run_cmd("ifconfig %s down" % iface)
    run_cmd("iwconfig %s essid \"%s\"" % (iface, escaped_essid))
    run_cmd("iwconfig %s mode managed" % iface)
    run_cmd("ifconfig %s up" % iface)

    if wpa_custom_file:
        logger.info("Starting wpa_supplicant with custom config: %s" % wpa_custom_file)
        # wpa_supplicant might complain even if it goes ahead doing its job
        run_cmd("wpa_supplicant -D nl80211,wext -t -d -c%s -i%s -f /var/log/kano_wpa.log -B" % (wpa_custom_file, iface))

    elif encrypt == 'wep':

        # WEP encryption key length has to be 5, 13 or 58 (ASCII) or 10, 26, 116 in HEX form.
        # We will accept both forms in plain text and decide which to choose based on its length.
        # Additionally, if the key starts with "hex" we will also assume it is in HEX form.
        # Note that routers should accept both forms regardless of which one was used to configure it.
        if not seckey.startswith('hex'):
            # it can be either in hex or ascii form. decide based on length
            if len(seckey) in (5, 13, 58):
                # Good, this is the correct length for an ASCII key
                pass
            elif len(seckey) in (10, 26, 116):
                # Good, this is the correct length for a HEX key.
                # Prepend "hex" internally so supplicant settings can be applied.
                seckey='hex' + seckey
            else:
                logger.error("The WEP key lenght is incorrect (%d) should be 5/13/58 (ASCII) or 10/26/116 (HEX)" % (len(seckey)))
                return False
        elif len(seckey) not in (10+3, 26+3, 116+3):
            # For keys that start with "hex", make sure their length is also correct.
            logger.error("The HEX WEP key lenght is incorrect (%d) should 10/26/116" % (len(seckey)))
            return False

        logger.info("Starting wpa_supplicant for WEP network '%s' to interface %s" % (essid, iface))
        wpafile = '/etc/kano_wpa_connect.conf'
        associated = False
        if not wpa_conf(essid, seckey, confile=wpafile, wep=True):
            return False

        # wpa_supplicant might complain even if it goes ahead doing its job
        run_cmd("wpa_supplicant -D nl80211,wext -t -d -c%s -i%s -f /var/log/kano_wpa.log -B" % (wpafile, iface))

        # Wait for wpa_supplicant to become associated to the AP - key validation.
        # For WEP Open networks it will always proceed, beacuse there is no real authentication,
        # connection will fail during DHCP process. For WEP Shared networks it will fail here if the key is wrong.
        assoc_timeout = 20  # seconds
        assoc_start = time.time()
        while (time.time() - assoc_start) < assoc_timeout:
            out, _, _ = run_cmd('wpa_cli -p /var/run/wpa_supplicant/ status|grep wpa_state')
            wpa_state = out.strip('\n')
            if len(wpa_state) and wpa_state.split('=')[1] == 'COMPLETED':
                associated = True
                break
            time.sleep(0.5)

        if not associated:
            return False

    elif encrypt == 'wpa':

        if not seckey.startswith('hex'):
            wpalen=len(seckey)
            if wpalen < 8 or wpalen > 63:
                # WPA passphrases lenght is not correct
                logger.error("The WPA key lenght is incorrect " \
                                 "(%d) should be between 8 and 63 chars" % wpalen)
                return False

        logger.info("Starting wpa_supplicant for network '%s' to interface %s" % (essid, iface))
        wpafile = '/etc/kano_wpa_connect.conf'
        associated = False
        if not wpa_conf(essid, seckey, confile=wpafile):
            return False

        # wpa_supplicant might complain even if it goes ahead doing its job
        run_cmd("wpa_supplicant -D nl80211,wext -t -d -c%s -i%s -f /var/log/kano_wpa.log -B" % (wpafile, iface))

        # Wait for wpa_supplicant to become associated to the AP
        # or give up if it takes too long
        assoc_timeout = 20  # seconds
        assoc_start = time.time()
        while (time.time() - assoc_start) < assoc_timeout:
            out, _, _ = run_cmd('wpa_cli -p /var/run/wpa_supplicant/ status|grep wpa_state')
            wpa_state = out.strip('\n')
            if len(wpa_state) and wpa_state.split('=')[1] == 'COMPLETED':
                associated = True
                break
            time.sleep(0.5)

        if not associated:
            return False

    logger.info("Starting UDHCPC client '%s'" % (udhcpc_cmdline))
    out, err, rc = run_cmd(udhcpc_cmdline)
    return rc == 0


def disconnect(iface, clear_cache=False):
    # Stop the Kano reconnecting to the internet
    run_cmd('wpa_cli terminate')

    if clear_cache:
        k = KwifiCache()
        k.empty()

    run_cmd('iwconfig "%s" essid off' % iface)
    run_cmd('iwconfig "%s" mode managed' % iface)
    time.sleep(3)
    return


def is_redirected():
    '''
    Returns true if there is a url redirection
    We don't use execute() to avoid an exception
    '''

    cmdline = shlex.split("curl -Is 'www.google.com'")
    p = subprocess.Popen(cmdline, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (out, err) = p.communicate()
    return (out.find("http://www.google.") == -1)


class KwifiCache:
    '''
    Class to manage a cache of the last successful wireless connection.
    Call save() when the connection succeeds, return True on success.
    Call get(essid) to know if a neighbouring network is cached, returns None otherwise
    Call get_latest() to get currently cached network if any, returns None otherwise

    Data is written in plain json format.
    '''
    def __init__(self, cache_file='/etc/kwifiprompt-cache.conf'):
        self.cache_file = cache_file

    def save(self, essid, encryption, enckey, wpaconf=None):
        return self._save_cache_(essid, encryption, enckey, wpaconf)

    def empty(self):
        try:
            os.unlink(self.cache_file)
            return True
        except:
            return False

    def get(self, essid):
        wdata = self._get_cache_()
        try:
            if wdata['essid'] == essid:
                return wdata
        except:
            return None

    def get_latest(self):
        return self._get_cache_()

    def _save_cache_(self, essid, encryption, enckey, wpaconf):
        wdata = json.dumps({'essid': essid, 'encryption': encryption, 'enckey': enckey, 'conf': wpaconf},
                           sort_keys=True, indent=4, separators=(',', ': '))
        with open(self.cache_file, 'w') as f:
            f.write(wdata)
            f.write('\n')
        return True

    def _get_cache_(self):
        if not os.access(self.cache_file, os.R_OK):
            return None
        with open(self.cache_file, 'r') as f:
            lastknown = f.read()
        wdata = json.loads(lastknown)
        return wdata


def launch_browser(*args):
    # TODO: Set the default system browser setting somewhere
    # if you are not root, you will get a "su" prompt that would misteriously stall you
    if not os.getuid() == 0:
        return

    launch_chromium(args)


def launch_chromium(*args):
    user_name = get_user_unsudoed()
    arguments=''.join(*args)
    run_bg('su - ' + user_name + ' -c "chromium {}"'.format(arguments))


def launch_midori(*args):
    user_name = get_user_unsudoed()
    arguments=''.join(*args)
    run_bg('su - ' + user_name + ' -c "midori {}"'.format(arguments))


def network_info():
    out, _, _ = run_cmd('ip route show')
    network_dict = dict()

    for line in out.splitlines():
        if line.startswith('default'):
            continue

        interface = line.split('dev ')[1].split()[0]

        data = dict()

        if interface.startswith('wlan'):
            command_network = "/sbin/iwconfig wlan0"
            out, _, _ = run_cmd(command_network)

            essid_match = re.match(r'.*ESSID:"(.*)"\ .*', out, re.MULTILINE)
            essid = essid_match.groups()[0] \
                if essid_match else 'Wireless Network'

            data['ESSID'] = essid
            data['nice_name'] = 'Wireless: {}'.format(essid)
        else:
            data['nice_name'] = 'Ethernet'

        data['address'] = line.split('src ')[1].split()[0]

        network_dict[interface] = data

    return network_dict


def set_dns(servers):
    server_str = '\n'.join(
        ['nameserver {}'.format(server) for server in servers])

    write_file_contents(DNS_FILE, server_str)


def clear_dns_interfaces():
    if os.path.exists(DNS_INTERFACES_BACKUP_FILE):
        # Already cleared
        return

    shutil.move(DNS_INTERFACES_FILE, DNS_INTERFACES_BACKUP_FILE)

    with open(DNS_INTERFACES_FILE, 'w') as f:
        f.close()


def restore_dns_interfaces():
    if os.path.exists(DNS_INTERFACES_BACKUP_FILE):
        shutil.move(DNS_INTERFACES_BACKUP_FILE, DNS_INTERFACES_FILE)


def refresh_resolvconf():
    run_bg('resolvconf -u')
