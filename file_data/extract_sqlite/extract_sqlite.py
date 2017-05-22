#!/usr/bin/env python
#############################################################
# Copyright 2017 Jason Pruitt <jrspruitt@gmail.com>

# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without
# restriction, including without limitation the rights to use,
# copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
# BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
# ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#############################################################


import os
import re
import sys
import struct

SQLITE_MAGIC_NUMBER = '\x53\x51\x4C\x69\x74\x65\x20\x66\x6F\x72\x6D\x61\x74\x20\x33\x00' # 'SQLite format3\x00'
SQLITE_HDR_FORMAT = '>16shbbbbbbIIIIIIIIIIII20sII'
SQLITE_HDR_FIELDS = ['magic',           # Header string 'SQLite format3\x00'.
                    'page_size',        # DB page size in bytes power of 2 between 512 - 32768 inclusive, 1 = 655536.
                    'write_ver',        # File format write version 1 Legacy, 2 WAL.
                    'read_ver',         # File format read version 1 Legacy, 2 WAL.
                    'page_reserve',     # Bytes of unused reserve space at end of page.
                    'max_payload',      # Max embedded payload fraction. Must be 64.
                    'min_payload',      # Min embedded payload fraction. Must be 32.
                    'leaf_payload',     # Leaf payload fraction. Must be 32.
                    'change_counter',   # File change counter.
                    'db_size',          # Database file size in pages.
                    'first_freelist',   # Page number of first freelist trunk page.
                    'freelist_pages',   # Total number of freelist pages.
                    'schema_cookie',    # Schema cookie.
                    'schema_format',    # Schema format cookie. (1, 2, 3, 4)
                    'cache_page_size',  # Default cache page size.
                    'rb_tree_page',     # Page number of the largest root b-tree page.
                    'db_encoding',      # 1 (UTF-8), 2 (UTF-16le), 3 (UTF16-be)
                    'user_version',     # User version as set by user_version.pragma
                    'zero',             # True (non-zero) auto-vac mode, False (zero) otherwise.
                    'app_id',           # Application ID.
                    'reserved',         # Reserved space for expansion. Must be 0x00
                    'valid_for',        # version-valid-for number.
                    'version_num',      # SQLite version number.
                    ]
SQLITE_HDR_SZ = struct.calcsize(SQLITE_HDR_FORMAT)

class sqlite_hdr(object):
    def __init__(self, buf):
        fields = dict(zip(SQLITE_HDR_FIELDS, struct.unpack(SQLITE_HDR_FORMAT, buf)))
        for key in fields:
            setattr(self, key, fields[key])

        setattr(self,'errors', [])
        setattr(self, 'file_size', 0)

        if self.db_size == 1:
            self.db_size = 65536
        if self.db_size != 0 and self.valid_for == self.change_counter:
            self.file_size = self.db_size * self.page_size
        else:
            self.errors.append('file_size')

    def __repr__(self):
        return 'SQLite DB File Header'

    def __iter__(self):
        for key in dir(self):
            if not key.startswith('_') and key not in ['display']:
                yield key, getattr(self, key)

    def display(self, tab=''):
        buf = '%sSQLite DB File Header\n' % tab
        buf += '%s----------------------\n' % tab
        for k, v in self:
            buf += '\t%s%s: %s\n' % (tab, k, v)
        return buf

def extract_files(fpath, opath):
    file_sz = os.path.getsize(fpath)

    with open(fpath, 'rw') as fi:
        buf = fi.read()
        locs = [m.start() for m in re.finditer(SQLITE_MAGIC_NUMBER, buf)]
        locs.append(file_sz)
        buf = ''

        for loc in range(0, len(locs)-1):     
            with open('%s/sqlite_%s.db' % (opath, loc), 'wb') as fo:
                fi.seek(locs[loc])
                hdr = sqlite_hdr(fi.read(SQLITE_HDR_SZ))
                fi.seek(locs[loc])
                buf = fi.read(hdr.file_size)
                #buf = fi.read(locs[loc+1] - locs[loc])
                print '\n-------------------------------------------'
                print '\t%s %s' % (locs[loc], locs[loc+1])
                print '\tcalc size %s' % (hdr.db_size * hdr.page_size)
                print '\tguess size %s' % (locs[loc+1] - locs[loc])
                print '\t', hdr.errors
                print hdr.display()
                fo.write(buf)

    print 'sqlite dbs found at %s' % (', '.join([str(l) for l in locs]))

if __name__ == '__main__':

    if len(sys.argv) < 3:
        print """
    Usage:
        extract_sqlite.py sqlite.file <output_dir>
            Attempts to extract sqlite database from
            random data, displays header info found.
        """
        sys.exit(1)
    fpath = sys.argv[1]
    opath = sys.argv[2]

    if not os.path.exists(fpath):
        print '%s does not exist.' % fpath
        sys.exit(1)

    if not os.path.exists(opath):
        os.mkdir(opath)
    else:
        a = raw_input('Output directory "%s" already exists. Merge/Overwrite contents? [y/N]:  ' % opath)

        if not a.lower() in ['yes', 'y']:
            print 'Exiting program.'
            sys.exit(0)
        print 'Merging and Overwriting "%s"' % opath

    extract_files(fpath, opath)
