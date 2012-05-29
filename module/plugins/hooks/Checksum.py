# -*- coding: utf-8 -*-

"""
    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 3 of the License,
    or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
    See the GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program; if not, see <http://www.gnu.org/licenses/>.

    @author: zoidberg
"""
from __future__ import with_statement
import hashlib, zlib

from module.utils import save_join, fs_encode
from module.plugins.Hook import Hook

def computeChecksum(local_file, algorithm): 
    if algorithm in getattr(hashlib, "algorithms", ("md5", "sha1", "sha224", "sha256", "sha384", "sha512")):
        h = getattr(hashlib, algorithm)()
        chunk_size = 128 * h.block_size
        
        with open(local_file, 'rb') as f: 
            for chunk in iter(lambda: f.read(chunk_size), b''): 
                 h.update(chunk)
        
        return h.hexdigest()
         
    elif algorithm in ("adler32", "crc32"):
        hf = getattr(zlib, algorithm)
        last = 0
        
        with open(local_file, 'rb') as f: 
            for chunk in iter(lambda: f.read(8192), b''): 
                last = hf(chunk, last)
        
        return "%x" % last
    
    else:
        return None      

class Checksum(Hook):
    __name__ = "Checksum"
    __version__ = "0.02"
    __description__ = "Check downloaded file hash"
    __config__ = [("activated", "bool", "Activated", True),
                  ("action", "fail;retry;nothing", "What to do if check fails?", "retry"),
                  ("max_tries", "int", "Number of retries", 2)]
    __author_name__ = ("zoidberg")
    __author_mail__ = ("zoidberg@mujmail.cz")
             
    def downloadFinished(self, pyfile):
        """ 
        Compute checksum for the downloaded file and compare it with the hash provided by the hoster.
        pyfile.plugin.file_check should be a dictionary which can contain:
        a) if known, the exact filesize in bytes (e.g. "size": 123456789)
        b) hexadecimal hash string with algorithm name as key (e.g. "md5": "d76505d0869f9f928a17d42d66326307")    
        """
        if hasattr(pyfile.plugin, "file_check") and (isinstance(pyfile.plugin.file_check, dict)):
            
            download_folder = self.config['general']['download_folder']
            local_file = fs_encode(save_join(download_folder, pyfile.package().folder, pyfile.name))
            
            for key, value in sorted(pyfile.plugin.file_check.items(), reverse = True):                          
                if key == "size":
                    if value and value != pyfile.size:
                        self.logWarning("File %s has incorrect size: %d B (%d expected)" % (pyfile.size, value))
                        self.checkFailed(pyfile, "Incorrect file size")
                else:
                    checksum = computeChecksum(local_file, key.replace("-","").lower())                    
                    if checksum:
                        if checksum == value:
                            self.logInfo('File integrity of "%s" verified by %s checksum (%s).' % (pyfile.name, key.upper() , checksum))
                            return
                        else:
                            self.logWarning("%s checksum for file %s does not match (%s != %s)" % (key.upper(), pyfile.name, checksum, value))    
                            self.checkFailed(pyfile, "Checksums do not match")
                    else:
                        self.logWarning("Unsupported hashing algorithm: %s" % key.upper())  
            else:
                self.logWarning("Unable to validate checksum for file %s" % (pyfile.name))
    
    def checkFailed(self, pyfile, msg):
        action = self.getConfig("action")
        if action == "fail":
            pyfile.plugin.fail(reason = msg)
        elif action == "retry":
            pyfile.plugin.retry(reason = msg, max_tries = self.getConfig("max_tries"))