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

import os
import time
import subprocess
from kano.logging import logger
import shlex
import json
import re


class IWList():
    def __init__(self, interface, iwlist=None):
        '''
        For testing, <iwlist> can point to a file name which contains
        the output of a "iwlist" command, very useful to test remote complex network neighbourhoods.
        '''
        self.rawdata = ""
        self.data = {}
        self.interface = interface
        self.refresh(iwlist=iwlist)

    def refresh(self, iwlist=None):
        # Get raw data as a string
        self.rawdata = self.getRawData(self.interface, iwlist)
        # Parse raw data into a dictionary
        if self.rawdata is not None and len(self.rawdata.strip()):
            self.data = self.parseRawData(self.rawdata)

    def getRawData(self, interface, iwlist=None):
        '''
        Runs iwlist and gets WiFi data in a string
        Developped, tested with Wireless Extension v29 English translation, Nov 2007
        If iwlist points to a file, you can mimic iwlist from a response file for testing
        '''
        outdata = ''
        retries = 3

        # Make sure the wlan interface is up, otherwise the network scan will not proceed
        os.system ('ifconfig %s up' % interface)
        if iwlist:
            outdata = open(iwlist, 'r').read()
        else:
            # Contemplate those seldom cases where the dongle driver returns an empty list
            while len(outdata) < 80 and retries:
                cstring = "iwlist " + interface + " scan 2>/dev/nul"
                outdata = os.popen(cstring).read()
                retries -= 1

        return outdata

    def parseRawData(self, rawdata):
        # Parses a string containing the data printed by iwlist
        # Pre-condition: rawdata is not empty
        rawdatas = rawdata.split("\n")
        # Strip blanks
        # Let's separate by cells
        cellDataL = []
        #currentCell = None
        for s in rawdatas:
            # If new cell:
            if s.lstrip().startswith("Cell "):
                # log.debug("parseRawData: new cell")
                cellDataL.append([])
            if len(cellDataL) > 0 and len(s) > 0:
                cellDataL[len(cellDataL) - 1].append(s)
        # Data is separated by cells, now we'll parse each cell's data
        parsedCellData = {}
        for s in cellDataL:
            if s is not None:
                (cellNumber, cellData) = self.parseCellData("\n".join(s))
                parsedCellData[cellNumber] = cellData
        #log.debug("parseRawData: parsed "+str(len(cellDataL))+" cells")
        return parsedCellData

    def printData(self):
        # Debugging print
        for s in self.data:
            print s, self.data[s]

    def parseCellData(self, rawCellData):
        # Parses a string containing raw cell data
        # @return a tuble containing the cell's number and a dictionary with the data

        splitRawData = rawCellData.split("\n")
        cellData = {}
        for s in splitRawData:
            if s.strip().startswith("Cell "):
                cellData["Number"] = self.getCellNumber(s)
                cellData["MAC"] = self.getCellMAC(s)
            if s.strip().startswith("ESSID:\""):
                cellData["ESSID"] = self.getCellESSID(s)
            if s.strip().startswith("Protocol:"):
                cellData["Protocol"] = self.getCellProtocol(s)
            if s.strip().startswith("Mode:"):
                cellData["Mode"] = self.getCellMode(s)
            if s.strip().startswith("Mode:"):
                cellData["Mode"] = self.getCellMode(s)
            if s.strip().startswith("Frequency:"):
                cellData["Frequency"] = self.getCellFrequency(s)
                cellData["Channel"] = self.getCellChannel(s)
            if s.strip().startswith("Quality="):
                cellData["Quality"] = self.getCellQuality(s)
                cellData["Signal"] = self.getCellSignal(s)
                cellData["Noise"] = self.getCellNoise(s)
            if s.strip().startswith("Encryption key:"):
                cellData["Encryption"] = self.getCellEncryption(s)

            if s.strip().startswith("IE"):
                try:
                    ie = cellData["IE"]
                except KeyError:
                    ie = []
                ie.append(self.getCellIE(s))
                cellData["IE"] = ie

            if s.strip().startswith("Extra:"):
                try:
                    extra = cellData["Extra"]
                except KeyError:
                    extra = []
                extra.append(self.getCellExtra(s))
                cellData["Extra"] = extra

        return cellData["Number"], cellData

    def getCellExtra(self, s):
        s = s.split(":")
        if len(s) > 2:
            ret = ":".join(s[1:]).strip()
        else:
            ret = s[1].strip()
        return ret

    def getCellIE(self, s):
        s = s.split(":")
        if len(s) > 2:
            ret = ":".join(s[1:]).strip()
        else:
            ret = s[1].strip()
        return ret

    def getCellBitRates(self, s, rawdatas):
        # Pre-condition: s is in rawdatas, and bit rates are described in 3 lines
        ixBitRate = rawdatas.index(s)
        rawBitRate = rawdatas[ixBitRate].split(":")[1].strip() + "; " + rawdatas[ixBitRate + 1].strip() + "; " + \
            rawdatas[ixBitRate + 2].strip()
        return rawBitRate

    def getCellNumber(self, s):
        return s.strip().split(" ")[1]

    def getCellFrequency(self, s):
        s = s.split(":")[1]
        return s.strip().split(" ")[0]

    def getCellChannel(self, s):
        return s.strip().split(" ")[3][0:-1]

    def getCellEncryption(self, s):
        return s.strip().split(":")[1]

    def getCellSignal(self, s):
        s = s.split("Signal level=")[1]
        return s.strip().split(" ")[0]

    def getCellNoise(self, s):
        try:
            s = s.split("Noise level:")[1]
            return s.strip().split(" ")[0]
        except:
            return 0

    def getCellQuality(self, s):
        s = s.split("=")[1]
        return s.strip().split(" ")[0]

    def getCellMAC(self, s):
        return s.strip().split(" ")[4]

    def getCellESSID(self, s):
        return s.strip().split(":\"")[1][0:-1]

    def getCellProtocol(self, s):
        return s.strip().split(":")[1][-1]

    def getCellMode(self, s):
        return s.strip().split(":")[1]

    def getData(self):
        return self.data

    def sortNetworks(self, adict):
        x, z = adict['quality'].split('/')
        factor = int(x) / float(z)
        return factor

    def getList(self, unsecure=False, first=False, debug=False):
        '''
        Return a comfortable list of wireless networks
        sorted by signal strength (strongest first)
        '''

        if debug:
            import pprint
            pp = pprint.PrettyPrinter(indent=4, depth=6)
            print 'Debug on: Dumping parsed wireless info:'
            pp.pprint(self.data)

        self.iwnets = []
        for w in self.data:
            ww = self.data[w]

            # Basic signal information, excluding hidden SSIDs
            if len(ww['ESSID']):
                wnet = {
                    'essid': ww['ESSID'] if len(ww['ESSID']) else ww['MAC'],
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
                    self.iwnets.append(wnet)

        self.iwnets = sorted(self.iwnets, key=self.sortNetworks, reverse=True)
        if first and len(self.iwnets) > 1:
            return [self.iwnets[0]]
        else:
            return self.iwnets


def remove_pid(filename):
    try:
        os.unlink(filename)
    except:
        pass


def execute(cmdline):
    '''
    Executes command. If it fails with return code an exception is raised.
    If successful returns True
    '''
    args = shlex.split(cmdline)
    p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (out, err) = p.communicate()
    rc = p.returncode
    if not rc == 0:
        logger.error('FAIL: "%s" rc=%s, out="%s", err="%s"' % (cmdline, rc, out, err))
        raise Exception(cmdline, 'rc=%s, out="%s", err="%s"' % (rc, out, err))
    else:
        return out, err


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
    Returns data as returned by <iwconfig device>
    or None if device is not present or non-operative
    '''
    essid = mode = ap = None
    time.sleep(1)
    try:
        out, err = execute("iwgetid %s --raw" % iface)
        essid = out.strip()

        out, err = execute("iwgetid %s --raw --ap" % iface)
        ap = out.strip()

        # mode 2 = Managed
        out, err = execute("iwgetid %s --raw --mode" % iface)
        out = out.strip()
        if out == '2':
            mode = 'Managed'
        else:
            mode = out

    except:
        pass

    return (essid, mode, ap)


def is_gateway():
    '''
    Find the default route gateway, try to contact it. Return True if responding
    '''
    responds = False
    out, err = execute("ip route show")
    guess_ip = re.match('^default via ([0-9\.]*) .*', out)
    if guess_ip:
        gway_ip = guess_ip.group(1)
        try:
            rc = os.system('ping -c 1 %s > /dev/null 2>&1' % gway_ip)
            if rc == 0:
                responds = True
        except:
            pass

    return responds


def is_internet():
    '''
    Returns True if Internet is available, False otherwise
    '''
    try:
        rc = os.system('/usr/bin/is_internet')
        return rc == 0
    except:
        return False


def wpa_conf(essid, psk, confile):
    wpa_conf = '''
      ctrl_interface=/var/run/wpa_supplicant
      network={
             ssid="%s"
             scan_ssid=1
             key_mgmt=WPA-EAP WPA-PSK IEEE8021X NONE
             pairwise=CCMP TKIP
             psk="%s"
      }
    ''' % (essid, psk)

    f = open(confile, 'w')
    f.write(wpa_conf)
    f.close()

def reload_kernel_module (device_vendor='148f', device_product='5370', module='rt2800usb'):
    '''
    If the Kano USB deviceID is connected to the system, reload the kernel module. Returns True if reloaded.
    Works silently and ok even if the module is not currently loaded in the kernel.
    FIXME: This procedure should be called prior to connect() to circumvent current kernel module random problems.
    '''
    reloaded = False

    # Terminate wpa_supplicant daemon
    try:
        rc = os.system('wpa_cli terminate ; sleep .5 > /dev/null 2>&1')
        logger.info ('wpa_cli has been terminated')
    except:
        logger.error ('wpa_cli terminate failed - probably supplicant is not running rc=%d' % rc)
        pass


    rc = os.system('lsusb -d %s:%s > /dev/null 2>&1' % (device_vendor, device_product))
    if rc == 0:
        # The device id is matched, reload the kernel driver
        rc_load = os.system ('rmmod "%s" > /dev/null 2>&1 ; sleep .5 ; modprobe "%s" > /dev/null 2>&1 ; sleep 5' % (module, module))
        logger.info ('Reloading wifi dongle kernel module "%s" for deviceID %s:%s rc=%d' % 
                     (module, device_vendor, device_product, rc_load))
        if rc_load == 0:
            reloaded = True
    else:
        logger.info ('Not reloading kernel module because device not found (%s:%s)' % (device_vendor, device_product))

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

    udhcpc_cmdline = 'udhcpc -S -t 70 -A 20 -n -a --script=/etc/udhcpc/kano.script -i %s' % iface
    time.sleep(1)

    #
    # kill previous connection daemons
    #
    try:
        execute("pkill -f '%s' > /dev/null 2>&1" % (udhcpc_cmdline))
    except:
        logger.error ('could not kill udhcpc daemon')
        pass

    # and wpa supllicant daemon, politely through wpa_cli
    try:
        execute("wpa_cli terminate > /dev/null 2>&1")
    except:
        logger.error ('could not kill wpa_supplicant daemon')
        pass

    #
    # Set the ESSID of the wireless network to associate
    #
    escaped_essid = essid.replace('\'', '\\\'')
    escaped_essid = escaped_essid.replace('\"', '\\\"')

    execute("iwconfig %s power off" % iface)
    execute("ifconfig %s down" % iface)
    execute("iwconfig %s essid \"%s\"" % (iface, escaped_essid))
    execute("iwconfig %s mode managed" % iface)
    execute("ifconfig %s up" % iface)

    if wpa_custom_file:
        logger.info("Starting wpa_supplicant with custom config: %s" % wpa_custom_file)
        try:
            # wpa_supplicant might complain even if it goes ahead doing its job
            execute("wpa_supplicant -t -d -c%s -i%s -f /var/log/kano_wpa.log -B" % (wpa_custom_file, iface))
        except:
            pass

    elif encrypt == 'wep':
        # WEP encryption keys have to be either 5, 13 or 58 ASCII chars in length (40/104/232 bits)
        # plus 24 bits for IV giving 64,128,256-bit encryption modes
        if len(seckey) not in (5, 13, 58):
            logger.error("WEP encryption key lenght incorrect (%d) has to be one of 5/13/58 chars" % (len(seckey)))
            return False
        else:
            try:
                logger.info("Setting WEP encryption key for network '%s' to interface %s" % (essid, iface))
                execute("iwconfig %s key 's:%s'" % (iface, seckey))
            except:
                pass

    elif encrypt == 'wpa':
        logger.info("Starting wpa_supplicant for network '%s' to interface %s" % (essid, iface))
        wpafile = '/etc/kano_wpa_connect.conf'
        associated = False
        wpa_conf(essid, seckey, confile=wpafile)

        try:
            # wpa_supplicant might complain even if it goes ahead doing its job
            execute("wpa_supplicant -t -d -c%s -i%s -f /var/log/kano_wpa.log -B" % (wpafile, iface))

            # Wait for wpa_supplicant to become associated to the AP
            # or give up if it takes too long
            assoc_timeout = 20 # seconds
            assoc_start = time.time()
            while (time.time() - assoc_start) < assoc_timeout:
                r = os.popen('wpa_cli -p /var/run/wpa_supplicant/ status|grep wpa_state')
                wpa_state = r.read().strip('\n')
                if wpa_state.split('=')[1] == 'COMPLETED':
                    associated = True
                    break
            
                r.close()
                time.sleep (0.5)
        except:
            pass

        if not associated:
            return False

    try:
        logger.info("Starting UDHCPC client '%s'" % (udhcpc_cmdline))        
        execute(udhcpc_cmdline)
        return True
    except:
        return False


def disconnect(iface):
    execute('iwconfig "%s" essid off' % iface)
    execute('iwconfig "%s" mode managed' % iface)
    time.sleep(3)
    return


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


if __name__ == '__main__':
    import sys
    import pprint

    pp = pprint.PrettyPrinter(indent=4, depth=6)
    wiface = 'wlan0'

    print 'Read wireless networks from a dump file (iwlist scan output)'
    if len(sys.argv) < 2:
        print 'Syntax: network.py <iwlist dump file>'
        sys.exit(1)
    else:
        iwlist = sys.argv[1]

    print 'Parsing info from file: %s\n' % iwlist
    iwl = IWList(wiface, iwlist=iwlist)

    print '>>> Raw parsed data follows:'
    pp.pprint(iwl.data)

    print '>>> Compact parsed data follows:'
    pp.pprint(iwl.getList())

    sys.exit(0)
