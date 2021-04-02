import argparse

import selenium.webdriver

import libs.files as files


# Constants
#=======================================================================================================================
u_PROG_NAME = u'ROM patcher CLI - v0.1.2020-02-16'
u_URL = u'https://www.marcrobledo.com/RomPatcher.js/'
u_GECKO_DRIVER_PATH = u'/opt/geckodriver/geckodriver'
u_CHROME_DRIVER_PATH = u'/opt/chromedriver/chromedriver'

u_BROWSER = 'chrome'


# Classes
#=======================================================================================================================
class CmdArgs:
    def __init__(self):
        self.u_rom = u''
        self.u_patch = u''
        self.u_patched = u''

        self._read()

    def __str__(self):
        return unicode(self).encode('utf8')

    def __unicode__(self):
        u_out = u'<CmdArgs>\n'
        u_out += u'  .u_rom:     %s\n' % self.u_rom
        u_out += u'  .u_patch:   %s\n' % self.u_patch
        u_out += u'  .u_patched: %s\n' % self.u_patched
        return u_out

    def _read(self):
        o_parser = argparse.ArgumentParser()
        o_parser.add_argument('rom',
                              action='store',
                              help='Path of the ROM to patch. e.g. /home/john/my_rom.sfc')
        o_parser.add_argument('patch',
                              action='store',
                              help='Path of the patch to apply. e.g. /home/john/my_patch.ipf')
        o_parser.add_argument('patched',
                              action='store',
                              help='Path of the output patched file. e.g. /home/john/final_result.sfc')

        o_args = o_parser.parse_args()

        o_rom_fp = files.FilePath(o_args.rom).absfile()
        if o_rom_fp.is_file():
            self.u_rom = o_rom_fp.u_path
        else:
            print 'ERROR: Can\'t open ROM file "%s"' % o_args.rom
            quit()

        o_patch_fp = files.FilePath(o_args.patch).absfile()
        if o_patch_fp.is_file():
            self.u_patch = o_patch_fp.u_path
        else:
            print 'ERROR: Can\'t open patch file "%s"' % o_args.patch
            quit()

        # TODO: check output dir exists for patched rom
        o_patched_fp = files.FilePath(o_args.patched).absfile()
        self.u_patched = o_patched_fp.u_path

    def nice_format(self):
        u_out = u''
        u_out += u'ROM:     %s\n' % self.u_rom
        u_out += u'PATCH:   %s\n' % self.u_patch
        u_out += u'PATCHED: %s' % self.u_patched
        return u_out


# Main functions
#=======================================================================================================================
def submit_selenium(po_cmd_args):
    import re
    import time

    from selenium import webdriver
    from selenium.webdriver.firefox.options import Options

    #options.headless = True

    if u_BROWSER == 'chrome':
        options = webdriver.ChromeOptions()
        options.headless = True
        prefs = {"download.default_directory": "/tmp/foo/",
                 "download.directory_upgrade": "true",
                 "download.prompt_for_download": "false",
                 "disable-popup-blocking": "true",
                 }

        options.add_experimental_option("prefs", prefs)
        o_web_driver = webdriver.Chrome(executable_path=u_CHROME_DRIVER_PATH, options=options)

    elif u_BROWSER == 'firefox':
        options = Options()
        options.set_preference("browser.download.dir", "/tmp/foo")
        options.set_preference("browser.download.folderList", 2)
        options.set_preference("browser.helperApps.neverAsk.saveToDisk", "true")

        o_web_driver = webdriver.Firefox(executable_path=u_GECKO_DRIVER_PATH, options=options)

    else:
        raise ValueError

    o_web_driver.get(u_URL)

    # Selecting the ROM
    #------------------
    o_element = o_web_driver.find_element_by_id('input-file-rom')
    o_element.send_keys(po_cmd_args.u_rom)

    # Waiting until the CRC32 of the ROM is calculated
    # TODO: Add a reasonable timeout to avoig getting stuck forever if any problem occurs.
    while True:
        o_crc32 = o_web_driver.find_element_by_id('crc32')
        u_text = o_crc32.text.lower().strip()
        if (len(u_text) == 8) and re.match(r'^[a-f0-9]{8}$', u_text):
            break

        else:
            time.sleep(1)

    # Selecting the patch
    #--------------------
    o_element = o_web_driver.find_element_by_id('input-file-patch')
    o_element.send_keys(po_cmd_args.u_patch)

    # Clicking on the apply patch button
    #-----------------------------------
    # Wait until the patch is uploaded (so the button becomes active)
    while True:
        o_element = o_web_driver.find_element_by_id('button-apply')
        u_class = o_element.get_attribute('class')
        u_class = u_class.strip().lower()

        if u_class != u'enabled':
            time.sleep(1)
        else:
            o_element.click()
            break

    # TODO: Wait until the file appears in the download dir, so the download finished.
    print 'PATCHED AND DOWNLOADED!!!'

    o_web_driver.save_screenshot(u'/tmp/foo.png')


# Main code
#=======================================================================================================================
if __name__ == '__main__':
    print u'%s\n%s' % (u_PROG_NAME, u'=' * len(u_PROG_NAME))
    o_cmd_args = CmdArgs()
    print o_cmd_args.nice_format()
    print u'%s' % u'-' * len(u_PROG_NAME)

    submit_selenium(o_cmd_args)