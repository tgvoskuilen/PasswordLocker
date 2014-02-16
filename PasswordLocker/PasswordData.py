"""
Copyright (c) 2014, Tyler Voskuilen
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met: 

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer. 
2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution. 

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

import os
import copy
import math
import csv
import re
from Crypto.Hash import SHA256
from Crypto.Cipher import AES
from Crypto import Random

# bytes to separate entries with
TOKEN1 = chr(30)
TOKEN2 = chr(29)
BUFFER = chr(0)
WEB_SPEED = 1e6
LOCAL_SPEED = 1e12

###############################################################################
class PasswordData(object):
    """
    This class contains a list of entries which comprise the password database,
    stores the encryption key (only while running), and handles encryption and
    decryption of the data.
    """
    def __init__(self, password, dbFile, new=False):
        self.valid = True
        self.dbFile = dbFile
        
        # Use SHA256 to generate encryption key from user password
        myhash = SHA256.new()
        myhash.update(password)
        self.key = myhash.digest()
        
        if new:
            # Write an empty db to a new file
            self.entries = []
            self.Write()
        else:
            # Read and decrypt the db file
            try:
                with open(dbFile,'rb') as df:
                    raw = df.read()
                    
                decrypter = AES.new\
                            (
                                self.key, 
                                AES.MODE_CBC, 
                                raw[0:AES.block_size]
                            )
                            
                dataStr = decrypter.decrypt(raw[AES.block_size:])
                self.entries = []

                try:
                    if dataStr and TOKEN1 not in dataStr:
                        raise IndexError
                        
                    strs = dataStr.split(TOKEN1)

                    for s in strs:
                        if s:
                            # String 's' must either be all BUFFER characters
                            # or be separable by TOKEN2 into 5 sub-strings
                            ss = s.split(TOKEN2)
                            if len(ss) == 5:
                                self.entries.append\
                                (
                                    Entry(ss[0],ss[1],ss[2],ss[3],ss[4])
                                )
                                
                            elif len(s) != s.count(BUFFER):
                                raise IndexError

                except IndexError:
                    self.valid = False
                    self.errMsg = 'File could not be decrypted, '+\
                                  'possibly due to an incorrect password'

            except IOError:
                self.errMsg = 'File could not be loaded'
                self.valid = False
                
        # create self-contained copy
        self.oldEntries = copy.deepcopy(self.entries)
        
    #--------------------------------------------------------------------------
    def ImportCSV(self, csvFile):
        """
        Read entries from an uncrypted CSV file and add to the current database,
        excluding duplicates
        """
        
        with open(csvFile,'r') as csvFile:
            reader = csv.reader(csvFile, delimiter=',', quotechar='"')
            
            for row in reader:
                newEntry = Entry(row[0],row[1],row[2],row[3],row[4])
                
                if newEntry not in self.entries:
                    self.entries.append(newEntry)

    
    #-------------------------------------------------------------------------- 
    def SaveChanges(self, asCSV=False, dest=None, newpassword=None):
        """ 
        Save the database, either to its original file, to an unencrypted
        csv file, or to a new encrypted file
        """
        if newpassword is not None:
            myhash = SHA256.new()
            myhash.update(newpassword)
            self.key = myhash.digest()
    
        if asCSV:
            self.Write(encrypt=False, dest=dest)
            
        else:
            if dest is not None:
                self.dbFile = dest
            self.Write()
            self.oldEntries = copy.deepcopy(self.entries)
    
    #-------------------------------------------------------------------------- 
    def HasChanged(self):
        """
        Check if the data in the database has changed since either loading or
        since the last encrypted save (CSV exports are ignored).
        """
        if len(self.entries) != len(self.oldEntries):
            return True
        else:
            return any([i != j for i,j in zip(self.entries, self.oldEntries)])
    
    
    #-------------------------------------------------------------------------- 
    def Write(self, encrypt=True, dest=None):
        """
        Write the password database, either to an encrypted file, or an
        unencrypted CSV file. The input 'dest' is only used if encrypt is false.
        """ 
        
        if encrypt:

            # generate string of entries
            es = TOKEN1.join\
                 (
                     [TOKEN2.join(e.col_strings()) for e in self.entries]
                 ) + TOKEN1
            
            iv = Random.new().read(AES.block_size)
            encrypter = AES.new(self.key, AES.MODE_CBC, iv)
            
            # make sure the string is a multiple of the block size by buffering
            # the end with the BUFFER character, which will be ignored when 
            # it is read
            bs = AES.block_size
            buff = (bs*(len(es) % bs > 0) - (len(es) % bs))*BUFFER
            
            # Encrypt the string
            ciphertext = encrypter.encrypt(es+buff)
            
            # Write the encrypted string to the dabase file along with the
            # initialization vector (iv)
            with open(self.dbFile,'wb') as df:
                df.write(iv)
                df.write(ciphertext)
                
        else:
        
            # Write a CSV file (no encryption)
            with open(dest,'w') as csvFile:
                writer = csv.writer(csvFile, delimiter=',',quotechar='"',
                                    quoting=csv.QUOTE_MINIMAL)
                                    
                for e in self.entries:
                    writer.writerow(e.col_strings())
                
                
    #-------------------------------------------------------------------------- 
    def UpdateEntry(self, tag, newEntry):
        """ 
        Update an entry in the database with a specified tag to match the
        input 'newEntry'. This is done rather than simply using replace so
        that the entry's tag is retained.
        """
        tags = [e.tag for e in self.entries]
        idx = tags.index(tag)
        self.entries[idx].Update(newEntry)
    
    #-------------------------------------------------------------------------- 
    def GetCategories(self):
        """ Get a list of category options for the GUI """
        return ['All'] + sorted(list(set([e.category for e in self.entries])))

    #-------------------------------------------------------------------------- 
    def GetEntries(self, cat):
        """ Get all entries of a specified category """
        if cat == 'All':
            return self.entries
        else:
            return [e for e in self.entries if e.category == cat]
            
        
###############################################################################
class Entry(object):
    """
    This is a basic class for storing each entry in the password database. It
    contains 5 strings, a unique tag, and some methods for displaying its
    data in the GUI and exporting it to a file
    """
    #-------------------------------------------------------------------------- 
    def __init__(self, name, username, password, category, comments):
        self.tag = id(self)
        self.name = name
        self.username = username
        self.password = password
        self.comments = comments
        self.category = category
        
    #-------------------------------------------------------------------------- 
    def col_strings(self):
        """ List of data strings, for display in GUI and saving to files """
        return [self.name, self.username, self.password, 
                self.category, self.comments]
        
    #-------------------------------------------------------------------------- 
    def sorting_name(self):
        """ String used for sorting the display in the GUI """
        return self.category +' '+ self.name
        
    #-------------------------------------------------------------------------- 
    def __eq__(self, other):
        """ Equality defined by all entries except tag """
        return self.name     == other.name     and \
               self.password == other.password and \
               self.comments == other.comments and \
               self.category == other.category and \
               self.username == other.username
         
    #--------------------------------------------------------------------------       
    def __ne__(self, other):
        """ Inequality opposite of equality """
        return not self.__eq__(other)
    
    #--------------------------------------------------------------------------       
    def Update(self, newEntry):
        """ Update the stored values from newEntry except tag """
        self.name = newEntry.name
        self.username = newEntry.username
        self.password = newEntry.password
        self.comments = newEntry.comments
        self.category = newEntry.category
    
###############################################################################
def calc_password_strength(password, speed=LOCAL_SPEED):
    """
    Evaluate the strength of a random password based on entropy and returns
    the average number of days to crack the password by brute force at the given
    speed in guesses/second. For web passwords, it uses 1e6 guesses/second, but
    for the database itself where it could be attempted locally it uses 1e12
    guesses/second
    
    THIS IS ONLY VALID FOR RANDOM PASSWORDS. A MODIFIED DICTIONARY WORD OR
    'abcABC123!' WOULD BE WEAKER THAN CALCULATED.
    """
    N = 0
    L = len(password)
    punct = '!@#$%^&*~()<>_-+=[]{};:?'
    
    if re.search('\d+',password):
        N = N + 10
        
    if re.search('[a-z]',password):
        N = N + 26
        
    if re.search('[A-Z]',password):
        N = N + 26
    
    if re.search('.,[,'+','.join([c for c in punct])+']',password):
        N = N + len(punct)
        
    if N > 0:
        H = L*math.log(N,2) # bits of entropy
        crackTime = 2**(H-1) / speed  # seconds
    else:
        crackTime = 0
        
    return crackTime/3600./24. # return crack time in days

        
