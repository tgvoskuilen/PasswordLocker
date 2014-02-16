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

import wx
import wx.lib.intctrl as IC
import os
import random
import string
from PasswordData import *
from controls import StrengthGauge

###############################################################################
class EntranceDialog(wx.Dialog):
    """
    Initial dialog displayed to get password and select encrypted file
    """
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, wx.ID_ANY,
                           title='Select and decrypt password database', 
                           size=(-1,-1))
                           
        # The path to the last db file tried is saved in the '.history' file
        self.histFile = os.path.join(os.getcwd(),'.history')
        
        
        #Make Items
        self.dbFile = wx.TextCtrl(self, -1, value='', 
                                  style=wx.TE_READONLY, size=(500,-1))
                                  
        self.selectFile = wx.Button(self, wx.ID_ANY, 'Select File')
        
        self.password = wx.TextCtrl(self, -1, value='', 
                                    style=wx.TE_PASSWORD|wx.TE_PROCESS_ENTER, 
                                    size=(300,-1))
                                    
        self.password_txt = wx.TextCtrl(self, -1, value='', 
                                        style=wx.TE_PROCESS_ENTER, 
                                        size=(300,-1))
                                        
        self.password_txt.Hide()
        
        self.showText = wx.CheckBox(self, wx.ID_ANY, 'Show Password Text')
        self.newDb = wx.Button(self, wx.ID_ANY, 'Create New Database')
        self.cancel = wx.Button(self, wx.ID_CANCEL, 'Cancel')
        self.ok = wx.Button(self, wx.ID_OK, 'Decrypt')
        
        
        #Make Labels
        fileLabel = wx.StaticText(self, wx.ID_ANY, label='Database File:', 
                                  size=(150,-1))
                                  
        passLabel = wx.StaticText(self, wx.ID_ANY, label='Password:', 
                                  size=(150,-1))
        
        self.dbFile.SetBackgroundColour((200,200,200))
        
        self._load_state()
        
        if self.dbFile.Value:
            self.password.SetFocus()
        else:
            self.selectFile.SetFocus()
        
        #Layout items
        hBoxes = []

        hBoxes.append(wx.BoxSizer(wx.HORIZONTAL))
        hBoxes[-1].Add(fileLabel, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        hBoxes[-1].Add(self.dbFile, 1, wx.EXPAND|wx.ALL, 5)
        hBoxes[-1].Add(self.selectFile, 0, wx.ALL, 5)
        
        hBoxes.append(wx.BoxSizer(wx.HORIZONTAL))
        hBoxes[-1].Add(passLabel, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        hBoxes[-1].Add(self.password, 0, wx.ALL, 5)
        hBoxes[-1].Add(self.password_txt, 0, wx.ALL, 5)
        hBoxes[-1].Add(self.showText, 1, wx.EXPAND|wx.ALL, 5)

        hBoxes.append(wx.BoxSizer(wx.HORIZONTAL))
        hBoxes[-1].Add(self.newDb, 1, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        hBoxes[-1].Add(self.cancel, 1, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        hBoxes[-1].Add(self.ok, 1, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        
        vBox =  wx.BoxSizer(wx.VERTICAL)
        for hBox in hBoxes:
            vBox.Add(hBox, 0, wx.EXPAND|wx.ALL, 5)

        self.SetSizer(vBox)
        vBox.Fit(self)
        
        # Bind the set file button and new database button
        self.Bind(wx.EVT_BUTTON, self._get_file,  self.selectFile)
        self.Bind(wx.EVT_BUTTON, self._new_pdb, self.newDb)
        self.Bind(wx.EVT_TEXT_ENTER, self._close, self.password)
        self.Bind(wx.EVT_CHECKBOX, self._toggle_password, self.showText)
        
    #--------------------------------------------------------------------------
    def _toggle_password(self, event):
        """ Toggle whether dots or text are shown in password box """
        
        if self.showText.IsChecked():
            self.password_txt.Show(True)
            self.password.Show(False)
            self.password_txt.SetValue(self.password.GetValue())
            
        else:
            self.password.Show(True)
            self.password_txt.Show(False)
            self.password.SetValue(self.password_txt.GetValue())
            
        self.Layout()
    
    #-------------------------------------------------------------------------- 
    def _close(self, event):
        """ Treat an "enter" press as clicking 'ok' """
        self.EndModal(wx.ID_OK)
        
    #-------------------------------------------------------------------------- 
    def _get_file(self, event):
        """
        Select a file to open
        """
        dlg = wx.FileDialog(None, "Select a file", 
                            wildcard="Password Files (*.*)|*.*",
                            defaultDir=os.getcwd(), 
                            style=wx.FD_OPEN|wx.FD_FILE_MUST_EXIST)
        
        if dlg.ShowModal() == wx.ID_OK:
            newpath = dlg.GetPaths()[0]
            self.dbFile.Value = newpath
            self._save_state()
            
        dlg.Destroy()
        
        
    #-------------------------------------------------------------------------- 
    def _new_pdb(self, event):
        """
        Make a new password database file
        """
        
        dlg = NewDatabase(self)
        if dlg.ShowModal() == wx.ID_OK:
            # create the new db here
            password = dlg.password.GetValue()
            dbFile = dlg.dbFile.GetValue()
            db = PasswordData(password, dbFile, new=True)
            
            self.dbFile.Value = dbFile
            self._save_state()

        dlg.Destroy()
        
    #-------------------------------------------------------------------------- 
    def _save_state(self):
        """ Save the file selection to the program history file """
        with open(self.histFile,'wb') as hf:
            hf.write(self.dbFile.Value)

    #-------------------------------------------------------------------------- 
    def _load_state(self):
        """ Save the file selection to the program history file """
        
        if os.path.isfile(self.histFile):
            with open(self.histFile,'rb') as hf:
                oldFile = hf.read()
                
            if os.path.isfile(oldFile):
                self.dbFile.Value = oldFile
            
            
###############################################################################
class NewDatabase(wx.Dialog):
    """
    Dialog to make a new database file (empty)
    """
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, wx.ID_ANY,
                           title='Create new password database')
                           
        #Make Items
        self.dbFile = wx.TextCtrl(self, wx.ID_ANY, value='', size=(500,-1))
        self.selectFile = wx.Button(self, wx.ID_ANY, 'Select File')
        
        self.password = wx.TextCtrl(self, wx.ID_ANY, value='', 
                                    style=wx.TE_PASSWORD, size=(300,-1))
                                    
        self.password_txt = wx.TextCtrl(self, wx.ID_ANY, value='', 
                                        size=(300,-1))
        self.password_txt.Hide()
        
        self.password2 = wx.TextCtrl(self, -1, value='', 
                                     style=wx.TE_PASSWORD|wx.TE_PROCESS_ENTER, 
                                     size=(300,-1))
                                     
        self.password2_txt = wx.TextCtrl(self, -1, value='', 
                                         style=wx.TE_PROCESS_ENTER, 
                                         size=(300,-1))
        self.password2_txt.Hide()
        
        self.strength = StrengthGauge(self, size=(250,10),
                                      style=wx.GA_HORIZONTAL)
        
        self.genPassword = wx.Button(self, wx.ID_ANY, 'Password\nGenerator')

        self.showText = wx.CheckBox(self, wx.ID_ANY, 'Show Password Text')
        self.cancel = wx.Button(self, wx.ID_CANCEL, 'Cancel')
        self.ok = wx.Button(self, wx.ID_OK, 'Create New Database')
        
        #Make Labels
        fileLabel = wx.StaticText(self, -1, label='Database File:', 
                                  size=(130,-1))
                                  
        passLabel = wx.StaticText(self, -1, label='Password:', 
                                  size=(130,-1))
                                  
        pass2Label = wx.StaticText(self, -1, label='Repeat Password:', 
                                   size=(130,-1))
        
        #Layout items
        hBoxes = []

        hBoxes.append(wx.BoxSizer(wx.HORIZONTAL))
        hBoxes[-1].Add(fileLabel, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        hBoxes[-1].Add(self.dbFile, 1, wx.EXPAND|wx.ALL, 5)
        hBoxes[-1].Add(self.selectFile, 0, wx.ALL, 5)
        
        pvBox = wx.BoxSizer(wx.VERTICAL)
        pvBox.Add(self.password, 1, wx.EXPAND|wx.LEFT|wx.RIGHT, 0)
        pvBox.Add(self.password_txt, 1, wx.EXPAND|wx.LEFT|wx.RIGHT, 0)
        pvBox.Add(self.strength, 0, wx.EXPAND|wx.LEFT|wx.RIGHT, 0)
        
        topPwd = wx.BoxSizer(wx.HORIZONTAL)
        topPwd.Add(passLabel, 0, wx.ALL, 5)
        topPwd.Add(pvBox, 1, wx.EXPAND|wx.LEFT|wx.RIGHT, 5)
        
        bottomPwd = wx.BoxSizer(wx.HORIZONTAL)
        bottomPwd.Add(pass2Label,0,wx.LEFT|wx.RIGHT|wx.ALIGN_CENTER_VERTICAL,5)
        bottomPwd.Add(self.password2, 1, wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, 5)
        bottomPwd.Add(self.password2_txt,1,wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP,5)
        
        vPwds = wx.BoxSizer(wx.VERTICAL)
        vPwds.Add(topPwd, 0, wx.EXPAND|wx.ALL, 0)
        vPwds.Add(bottomPwd, 0, wx.EXPAND|wx.ALL, 0)
        
        vButton = wx.BoxSizer(wx.VERTICAL)
        vButton.Add(self.genPassword, 1, wx.EXPAND|wx.ALL, 0)
        
        hBoxes.append(wx.BoxSizer(wx.HORIZONTAL))
        hBoxes[-1].Add(vPwds, 1, wx.EXPAND|wx.ALL, 0)
        hBoxes[-1].Add(vButton, 0, wx.EXPAND|wx.LEFT|wx.RIGHT, 5)
                
        hBoxes.append(wx.BoxSizer(wx.HORIZONTAL))
        hBoxes[-1].AddSpacer((145,-1))
        hBoxes[-1].Add(self.showText, 1, wx.EXPAND|wx.ALL, 0)
        
        hBoxes.append(wx.BoxSizer(wx.HORIZONTAL))
        hBoxes[-1].Add(self.cancel, 1, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        hBoxes[-1].Add(self.ok, 1, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        
        vBox =  wx.BoxSizer(wx.VERTICAL)
        for hBox in hBoxes:
            vBox.Add(hBox, 0, wx.EXPAND|wx.ALL, 5)

        self.SetSizer(vBox)
        vBox.Fit(self)
        
        # Bind the set file button and new database button
        self.Bind(wx.EVT_BUTTON, self._get_file,  self.selectFile)
        self.Bind(wx.EVT_BUTTON, self._check_entries, self.ok)
        self.Bind(wx.EVT_TEXT_ENTER, self._check_entries, self.password2)
        self.Bind(wx.EVT_CHECKBOX, self._toggle_password, self.showText)
        self.Bind(wx.EVT_BUTTON, self._open_password_gen,  self.genPassword)
        self.password.Bind(wx.EVT_TEXT, self._update_strength)
        self.password_txt.Bind(wx.EVT_TEXT, self._update_strength)
        
    #--------------------------------------------------------------------------
    def _update_strength(self, event):
        """
        Update the progress bar showing password strength
        """
        if self.showText.IsChecked():
            password = self.password_txt.Value
        else:
            password = self.password.Value
    
        nd = calc_password_strength(password)
        self.strength.UpdateStrength(nd)
    
    #--------------------------------------------------------------------------
    def _open_password_gen(self, event):
        """ Open the random password generator dialog """
        
        # Generate passwords suitable for resistance to local cracking
        dlg = PasswordGenerator(self, LOCAL_SPEED)
        
        if dlg.ShowModal() == wx.ID_OK:
            newPass = dlg.password.GetValue()
            
            if newPass:
                # ok to overwrite?
                if self.password.Value:
                    dlg2 = wx.MessageDialog\
                           (
                               None,
                               'Replace existing password?',
                               'Overwrite Password?',
                               wx.YES_NO|wx.NO_DEFAULT|wx.ICON_QUESTION
                           )
                                       
                    if dlg2.ShowModal() == wx.ID_YES:
                        self.password.Value = newPass
                        self.password_txt.Value = newPass

                    dlg2.Destroy()
                    
                else:
                    self.password.Value = newPass
                    self.password_txt.Value = newPass
                
        dlg.Destroy()
    
    
    #--------------------------------------------------------------------------
    def _toggle_password(self, event):
        """ Toggle whether password fields show dots or text """
        
        if self.showText.IsChecked():
            self.password_txt.Show(True)
            self.password.Show(False)
            self.password_txt.SetValue(self.password.GetValue())
            self.password2_txt.Show(True)
            self.password2.Show(False)
            self.password2_txt.SetValue(self.password2.GetValue())
            
        else:
            self.password.Show(True)
            self.password_txt.Show(False)
            self.password.SetValue(self.password_txt.GetValue())
            self.password2.Show(True)
            self.password2_txt.Show(False)
            self.password2.SetValue(self.password2_txt.GetValue())
            
        self.Layout()
        
        
    #-------------------------------------------------------------------------- 
    def _check_entries(self, event):
        """ Check that entries are valid before allowing ok button press """
        
        # First check the password fields
        passwordEmpty = not self.password.Value
        passwordMatch = (self.password.Value == self.password2.Value)

        if not passwordMatch or passwordEmpty:
        
            if passwordEmpty:
                msg = 'Password field empty'
            else:
                msg = 'Passwords do not match'
                 
            dlg = wx.MessageDialog(None, msg,'Password Error', 
                                   wx.OK|wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        # Warn if the password is too short
        if len(self.password.Value) < 6:
            dlg = wx.MessageDialog\
                  (
                      None, 
                      'Password is too short and may be insecure, '+
                      'are you sure you want to proceed?',
                      'Password Warning', 
                      wx.YES_NO|wx.NO_DEFAULT|wx.ICON_QUESTION
                  )
                                   
            if dlg.ShowModal() != wx.ID_YES:
                dlg.Destroy()
                return
                
            dlg.Destroy()
            
        
        # check that file has ben specified and does not already exist
        dbFile = self.dbFile.Value
        fileExists = os.path.isfile(dbFile)
        noFile = len(dbFile) == 0
        
        if fileExists:
        
            if noFile:
                msg = 'No file entered'
            else:
                msg = 'File already exists'

            dlg = wx.MessageDialog(None, msg,'File Error', 
                                   wx.OK|wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            
            return
            
        self.EndModal(wx.ID_OK)
        
    #-------------------------------------------------------------------------- 
    def _get_file(self, event):
        """
        Select a file to save the password database
        """
        dlg = wx.FileDialog(None, "Select a file", 
                            wildcard="Password Files (*.*)|*.*",
                            defaultDir=os.getcwd(), 
                            style=wx.FD_SAVE)
        
        if dlg.ShowModal() == wx.ID_OK:
            newpath = dlg.GetPaths()[0]
            self.dbFile.Value = newpath
            
        dlg.Destroy()
        
###############################################################################
class EditEntryDialog(wx.Dialog):
    """
    Dialog to make a new database
    """
    def __init__(self, parent, okButtonText = 'Add', 
                 inputEntry = Entry("","","","None","")):
        
        wx.Dialog.__init__(self, parent, wx.ID_ANY,
                           title=okButtonText+' Entry', size=(-1,-1))
                           
        #Make Items
        self.name = wx.TextCtrl(self, wx.ID_ANY, value=inputEntry.name, 
                                size=(400,-1))
                                
        self.username = wx.TextCtrl(self, wx.ID_ANY, value=inputEntry.username, 
                                    size=(400,-1))
                                    
        self.password = wx.TextCtrl(self, wx.ID_ANY, value=inputEntry.password)
        
        self.strength = StrengthGauge(self,size=(250,10),style=wx.GA_HORIZONTAL)
        
        self.genPassword = wx.Button(self, wx.ID_ANY, 'Password Generator')
        
        self.comments = wx.TextCtrl(self, wx.ID_ANY, value=inputEntry.comments, 
                                    size=(400,-1))
                                    
        self.category = wx.TextCtrl(self, wx.ID_ANY, value=inputEntry.category, 
                                    size=(400,-1))
        
        self.ok = wx.Button(self, wx.ID_OK, okButtonText)
        
        self.cancel = wx.Button(self, wx.ID_CANCEL, 'Cancel')
        
        #Make Labels
        nameLabel = wx.StaticText(self, -1, label='Name:', size=(150,-1))
        usernameLabel = wx.StaticText(self, -1,label='Username:',size=(150,-1))
        passLabel = wx.StaticText(self, -1, label='Password:', size=(150,-1))
        commentLabel = wx.StaticText(self, -1, label='Comment:', size=(150,-1))
        categoryLabel = wx.StaticText(self, -1,label='Category:',size=(150,-1))
        
        #Layout items
        hBoxes = []

        hBoxes.append(wx.BoxSizer(wx.HORIZONTAL))
        hBoxes[-1].Add(nameLabel, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        hBoxes[-1].Add(self.name, 1, wx.EXPAND|wx.ALL, 5)
        
        hBoxes.append(wx.BoxSizer(wx.HORIZONTAL))
        hBoxes[-1].Add(usernameLabel, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        hBoxes[-1].Add(self.username, 1, wx.EXPAND|wx.ALL, 5)
        
        pvBox = wx.BoxSizer(wx.VERTICAL)
        pvBox.Add(self.password, 1, wx.EXPAND|wx.LEFT|wx.RIGHT, 0)
        pvBox.Add(self.strength, 0, wx.EXPAND|wx.LEFT|wx.RIGHT, 0)
        
        hBoxes.append(wx.BoxSizer(wx.HORIZONTAL))
        hBoxes[-1].Add(passLabel, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        hBoxes[-1].Add(pvBox, 1, wx.EXPAND|wx.ALL, 5)
        hBoxes[-1].Add(self.genPassword, 0, wx.ALL, 5)
        
        hBoxes.append(wx.BoxSizer(wx.HORIZONTAL))
        hBoxes[-1].Add(commentLabel, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        hBoxes[-1].Add(self.comments, 1, wx.EXPAND|wx.ALL, 5)
        
        hBoxes.append(wx.BoxSizer(wx.HORIZONTAL))
        hBoxes[-1].Add(categoryLabel, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        hBoxes[-1].Add(self.category, 1, wx.EXPAND|wx.ALL, 5)
        
        hBoxes.append(wx.BoxSizer(wx.HORIZONTAL))
        hBoxes[-1].Add(self.cancel, 1, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        hBoxes[-1].Add(self.ok, 1, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        
        vBox =  wx.BoxSizer(wx.VERTICAL)
        for hBox in hBoxes:
            vBox.Add(hBox, 0, wx.EXPAND|wx.ALL, 5)

        # Bind events
        self.Bind(wx.EVT_BUTTON, self._open_password_gen,  self.genPassword)
        self.password.Bind(wx.EVT_TEXT, self._update_strength)
        
        self.SetSizer(vBox)
        vBox.Fit(self)
        self._update_strength()
        
    #--------------------------------------------------------------------------
    def _update_strength(self, event=None):
        """
        Update the progress bar showing password strength
        """
        password = self.password.GetValue()
        nd = calc_password_strength(password, WEB_SPEED)
        self.strength.UpdateStrength(nd)
        
    #--------------------------------------------------------------------------
    def _open_password_gen(self, event):
        """
        Open the random password generator in 'web' mode
        """
        dlg = PasswordGenerator(self, WEB_SPEED)
        
        if dlg.ShowModal() == wx.ID_OK:
            newPass = dlg.password.GetValue()
            
            if newPass:
                # ok to overwrite?
                if self.password.Value:
                    dlg2 = wx.MessageDialog\
                           (
                               None,
                               'Replace existing password?',
                               'Overwrite Password?',
                               wx.YES_NO|wx.NO_DEFAULT|wx.ICON_QUESTION
                           )
                                       
                    if dlg2.ShowModal() == wx.ID_YES:
                        self.password.Value = newPass

                    dlg2.Destroy()
                    
                else:
                    self.password.Value = newPass
                
        dlg.Destroy()
      
    #-------------------------------------------------------------------------- 
    def GetNewItem(self):
        """
        Return the new item created in the dialog
        """
        if not self.category.Value:
            cat = 'None'
        else:
            cat = self.category.Value
            
        return Entry(self.name.Value, self.username.Value, self.password.Value, 
                     cat, self.comments.Value)

        
###############################################################################
class PasswordGenerator(wx.Dialog):
    """
    Dialog to generate random passwords. It can function in 'Local' mode, or
    'Web' mode. Local mode ranks password strength based on 1e12 guesses/sec
    while 'Web' mode ranks based on 1e6 guesses/second.
    """
    def __init__(self, parent, speed):
        
        wx.Dialog.__init__(self, parent, wx.ID_ANY, title='Password Generator')
                           
        self.punct = '!@#$%^&*~()<>'
        
        self.speed = speed
            
        #Make Items
        
        self.useLowerCase = wx.CheckBox(self, wx.ID_ANY, 
                                        label='Lower Case (a-z)',size=(150,-1))
                                        
        self.useUpperCase = wx.CheckBox(self, wx.ID_ANY, 
                                        label='Upper Case (A-Z)',size=(150,-1))
                                        
        self.useDigits = wx.CheckBox(self, wx.ID_ANY, 
                                     label='Digits (0-9)', size=(150,-1))
                                     
        self.usePunctuation = wx.CheckBox\
                              (
                                  self, 
                                  wx.ID_ANY, 
                                  label='Punctuation (e.g. %s)'%self.punct[0:4] 
                              )
                              
        self.excludeSimilar = wx.CheckBox\
                              (
                                  self, 
                                  wx.ID_ANY, 
                                  label='Exclude Similar Characters (1Il,S$)'
                              )
                              
        self.startWithLetter = wx.CheckBox(self, wx.ID_ANY, 
                                           label='Must start with a letter?')
        
        self.useLowerCase.SetValue(True)
        self.useUpperCase.SetValue(True)
        self.useDigits.SetValue(True)
        self.usePunctuation.SetValue(False)
        self.excludeSimilar.SetValue(True)
        self.startWithLetter.SetValue(False)
        
        self.numDigits = IC.IntCtrl(self, wx.ID_ANY, value=8, 
                                    min=6, max=None, limited=False)
        
        self.password = wx.TextCtrl(self, -1, value='', size=(250,-1), 
                                    style=wx.TE_READONLY)
                                    
        self.generate = wx.Button(self, wx.ID_ANY, 'Generate')
        
        self.password.SetBackgroundColour((200,200,200))
        
        self.strength = StrengthGauge(self,size=(250,10),style=wx.GA_HORIZONTAL)
        
        self.ok = wx.Button(self, wx.ID_OK, 'Use Password')
        self.cancel = wx.Button(self, wx.ID_CANCEL, 'Cancel')
        
        #Make Labels
        passLabel = wx.StaticText(self, -1, label='Password:')
        numDigitLabel = wx.StaticText(self, -1, label='Password Length:')
        
        #Layout items
        hBoxes = []
        
        hBoxes.append(wx.BoxSizer(wx.HORIZONTAL))
        hBoxes[-1].Add(numDigitLabel, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        hBoxes[-1].Add(self.numDigits, 0, wx.ALL, 5)
        
        hBoxes.append(wx.BoxSizer(wx.HORIZONTAL))
        hBoxes[-1].Add(self.useLowerCase, 0, wx.LEFT, 5)
        hBoxes[-1].Add(self.useUpperCase, 0, wx.LEFT, 20)
        
        hBoxes.append(wx.BoxSizer(wx.HORIZONTAL))
        hBoxes[-1].Add(self.useDigits, 0, wx.LEFT, 5)
        hBoxes[-1].Add(self.usePunctuation, 0, wx.LEFT, 20)
        
        hBoxes.append(wx.BoxSizer(wx.HORIZONTAL))
        hBoxes[-1].Add(self.excludeSimilar, 0, wx.LEFT, 5)

        hBoxes.append(wx.BoxSizer(wx.HORIZONTAL))
        hBoxes[-1].Add(self.startWithLetter, 0, wx.LEFT, 5)
        
        pvBox = wx.BoxSizer(wx.VERTICAL)
        pvBox.Add(self.password, 1, wx.EXPAND|wx.LEFT|wx.RIGHT, 0)
        pvBox.Add(self.strength, 0, wx.EXPAND|wx.LEFT|wx.RIGHT, 0)
        
        hBoxes.append(wx.BoxSizer(wx.HORIZONTAL))
        hBoxes[-1].Add(passLabel, 0, wx.ALL, 5)
        hBoxes[-1].Add(pvBox, 1, wx.EXPAND|wx.ALL, 5)
        hBoxes[-1].Add(self.generate, 0, wx.ALL, 5)
        
        
        hBoxes.append(wx.BoxSizer(wx.HORIZONTAL))
        hBoxes[-1].Add(self.cancel, 1, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        hBoxes[-1].Add(self.ok, 1, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        
        vBox =  wx.BoxSizer(wx.VERTICAL)
        for hBox in hBoxes:
            vBox.Add(hBox, 0, wx.EXPAND|wx.ALL, 5)

        self.Bind(wx.EVT_BUTTON, self._generate,  self.generate)
        
        self.SetSizer(vBox)
        vBox.Fit(self)
        

    #--------------------------------------------------------------------------
    def _generate(self, event):
        """
        Generate a random password based on the inputs
        """
        N = self.numDigits.GetValue()
        
        if not self.numDigits.IsInBounds():
            dlg = wx.MessageDialog\
                  (
                      None, 
                      'Password must be at least %s characters long' 
                      % str(self.numDigits.GetMin()),
                      'Password Generator Error', 
                      wx.OK|wx.ICON_ERROR
                  )
                  
            dlg.ShowModal()
            dlg.Destroy()
            return
    
        chars = ''
        
        if self.useLowerCase.IsChecked():
            chars = chars + string.ascii_lowercase
            
        if self.useUpperCase.IsChecked():
            chars = chars + string.ascii_uppercase
            
        if self.useDigits.IsChecked():
            chars = chars + string.digits
            
        if self.usePunctuation.IsChecked():
            chars = chars + self.punct
            
        if self.excludeSimilar.IsChecked():
            chars = chars.translate(None,'1IlS$')
        
        if not chars:
            dlg = wx.MessageDialog(None, 
                                   'No characters selected',
                                   'Password Generator Error', 
                                   wx.OK|wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return
    
        
        randgen = random.SystemRandom()

        if self.startWithLetter.IsChecked():
            firstchars = chars.translate(None, string.digits+self.punct)
            fc = randgen.choice(firstchars)
        else:
            fc = ''

        self.password.Value = fc + \
            ''.join(randgen.choice(chars) for i in range(N-len(fc)))
        
        # Calculate password strength and update bar
        nDays = calc_password_strength(self.password.Value, self.speed)
        self.strength.UpdateStrength(nDays)

        

