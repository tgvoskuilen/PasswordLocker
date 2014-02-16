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
import os
from PasswordData import *
from controls import *
from dialogs import *
                     
###############################################################################
class MainFrame(wx.Frame):
    """
    The main frame contains the data, menus, and main panel
    """
    #----------------------------------------------------------------------
    def __init__(self):        
        wx.Frame.__init__(self, None, -1, "Password Locker", size=(1000,650))
        
        # Select db file
        dlg = EntranceDialog(self)
        if dlg.ShowModal() == wx.ID_OK:
            dbFile = dlg.dbFile.GetValue()
            password = dlg.password.GetValue()
        else:
            quit()
            
        dlg.Destroy()

        #Attempt to decrypt and load the password database
        self.data = PasswordData(password, dbFile)
        
        # Die here if password or file were invalid
        if not self.data.valid:
            dlg = wx.MessageDialog\
                  (
                      None, 
                      self.data.errMsg,
                      'Decryption Error', 
                      wx.OK|wx.ICON_ERROR
                  )

            dlg.ShowModal()
            dlg.Destroy()
            quit()
        
        #Create Menu bar and menus
        self.topMenu = wx.MenuBar()
        self.fileMenu = wx.Menu()
        self.aboutMenu = wx.Menu()
        
        #File Menu
        self.mSave = self.fileMenu.Append(-1, '&Encrypt and Save',
                                          'Save changes')
        self.mSaveAs = self.fileMenu.Append(-1, '&Encrypt and Save As',
                                            'Save changes to new file')
        self.mSaveCSV = self.fileMenu.Append(-1, '&Export Unencrypted CSV',
                                             'Save unencrypted copy')
        self.mImportCSV = self.fileMenu.Append(-1, '&Import Unencrypted CSV',
                                               'Load unencrypted copy')
        self.fileMenu.AppendSeparator()
        self.mQuit = self.fileMenu.Append(-1, '&Exit', 'Quit program')
        

        #About menu
        self.mAbout = self.aboutMenu.Append(-1, '&About', 'About')
        
        #Add Menus to Menu Bar and create a status bar
        self.topMenu.Append(self.fileMenu, '&File')
        self.topMenu.Append(self.aboutMenu, '&Help')
        self.SetMenuBar(self.topMenu)
                                          
        # Create the main display panel
        self.panel = MainPanel(self)
        self.Show()
        
        # Define event bindings
        self.Bind(wx.EVT_CLOSE, self.ShutDown)
        self.Bind(wx.EVT_MENU, self.DoSave, self.mSave)
        self.Bind(wx.EVT_MENU, self.DoSaveAs, self.mSaveAs)
        self.Bind(wx.EVT_MENU, self.DoSaveCSV, self.mSaveCSV)
        self.Bind(wx.EVT_MENU, self.DoImportCSV, self.mImportCSV)
        self.Bind(wx.EVT_MENU, self.ShutDown, self.mQuit)
        self.Bind(wx.EVT_MENU, self.ShowAbout, self.mAbout)
        self.mSave.Enable(False)
       
    #----------------------------------------------------------------------
    def ShowAbout(self, event):
        """
        Show the dialog about the program
        """
                
        description = "Password Locker is a program for storing a list of"+\
                      " your web passwords in a securely encrypted file.\n\n"+\
                      "The password database file is encrypted with AES "+\
                      "encryption using PyCrypto."
        
        license = """Password Locker is free software.

Redistribution and use in source and binary forms, with or without modification, 
are permitted provided that the following conditions are met: 

1. Redistributions of source code must retain the above copyright notice, 
   this list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright 
   notice, this list of conditions and the following disclaimer in the 
   documentation and/or other materials provided with the distribution. 

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS 
"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT 
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS 
FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE 
COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, 
INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, 
BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; 
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER 
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT 
LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN 
ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE 
POSSIBILITY OF SUCH DAMAGE."""
        
        info = wx.AboutDialogInfo()

        info.SetIcon(wx.Icon(os.path.join('PasswordLocker','lock.png'), 
                             wx.BITMAP_TYPE_PNG))
        info.SetName('Password Locker')
        info.SetVersion('1.0')
        info.SetDescription(description)
        info.SetCopyright('(C) 2014 Tyler Voskuilen')
        info.SetWebSite('http://www.github.com/tgvoskuilen/PasswordLocker')
        info.SetLicence(license)
        info.AddDeveloper('Tyler Voskuilen')
        info.AddDocWriter('Tyler Voskuilen')

        wx.AboutBox(info)

    #----------------------------------------------------------------------
    def CheckSave(self):
        """ Check if the save button should be enabled or disabled """
        self.mSave.Enable(self.data.HasChanged())

    #----------------------------------------------------------------------
    def DoSave(self, event):
        """ Save the data using standard encryption """
        self.data.SaveChanges()
        self.CheckSave()
        
    #----------------------------------------------------------------------
    def DoSaveAs(self, event):
        """ Save the data to a new file using standard encryption """
        dlg = NewDatabase(self)
        
        if dlg.ShowModal() == wx.ID_OK:
            password = dlg.password.GetValue()
            dbFile = dlg.dbFile.GetValue()
        
            # Associate the currently loaded data with the new file
            self.data.SaveChanges(dest=dbFile, newpassword=password)
            self.CheckSave()

        dlg.Destroy()
        
    #----------------------------------------------------------------------
    def DoSaveCSV(self, event):
        """ Save the data to a user-specified CSV file with no encryption """
        
        dlg = wx.MessageDialog\
              (
                  None, 
                  'This will save your password database as an unencrypted '+
                  'csv file, are you sure you want to proceed?',
                  'Export Warning', 
                  wx.OK|wx.CANCEL|wx.ICON_QUESTION
              )
                                   
        if dlg.ShowModal() == wx.ID_OK:
            # pick the destination csv file
            fdlg = wx.FileDialog(None, "Select CSV File Location", 
                                 wildcard="CSV Files (*.csv)|*.csv",
                                 defaultDir=os.getcwd(), 
                                 style=wx.FD_SAVE)
            
            if fdlg.ShowModal() == wx.ID_OK:
                csvFile = fdlg.GetPaths()[0]
                self.data.SaveChanges(asCSV=True, dest=csvFile)
                
            fdlg.Destroy()
             
        dlg.Destroy()

    #----------------------------------------------------------------------
    def DoImportCSV(self, event):
        """ Read a CSV file and add its entries to the currently open data """

        # pick csv file
        fdlg = wx.FileDialog(None, "Select CSV File", 
                             wildcard="CSV Files (*.csv)|*.csv",
                             defaultDir=os.getcwd(), 
                             style=wx.FD_OPEN|wx.FD_FILE_MUST_EXIST)
        
        if fdlg.ShowModal() == wx.ID_OK:
            csvFile = fdlg.GetPaths()[0]
            self.data.ImportCSV(csvFile)
            self.CheckSave()
            self.panel.update()
            
        fdlg.Destroy()
        
        
    #----------------------------------------------------------------------
    def ShutDown(self, event):
        """
        First checks if there are unsaved changes, then allows shutdown
        """
        closeWindow = True
        
        if self.data.HasChanged():
            dlg = wx.MessageDialog(None,'Save changes to database?',
                                   'Save Changes?',
                                   wx.YES_NO|wx.CANCEL|wx.YES_DEFAULT|wx.ICON_QUESTION)
            ans = dlg.ShowModal()
            if ans == wx.ID_YES:
                self.data.SaveChanges()
                self.CheckSave()
                
            closeWindow = (ans == wx.ID_YES or ans == wx.ID_NO)
        
        if closeWindow:
            event.Skip()


        
###############################################################################
class MainPanel(wx.Panel):
    """
    The panel which contains the list of entries, category selector, and add
    entry button
    """
    def __init__(self, parent):
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)
        self.data = parent.data
        self.parent = parent
        
        
        self.icon = wx.StaticBitmap\
                    (
                        self, 
                        wx.ID_ANY, 
                        wx.Bitmap\
                        (
                            os.path.join('PasswordLocker','lock-small.png'), 
                            wx.BITMAP_TYPE_ANY
                        )
                    )
                    
        progLabel = wx.StaticText(self, wx.ID_ANY, 'Password Locker')
        progLabel.SetFont(wx.Font(24, wx.DEFAULT, wx.NORMAL, wx.BOLD))
        
        catLabel = wx.StaticText(self, wx.ID_ANY, 'Select Category')
        self.categorySelect = wx.ComboBox(self, wx.ID_ANY, style=wx.CB_READONLY, 
                                          choices=self.data.GetCategories())
        self.categorySelect.SetSelection(0)
        
        self.entryList = ObjectListCtrl(self, id=wx.ID_ANY, 
                         style=wx.LC_REPORT | wx.LC_HRULES | wx.SUNKEN_BORDER,
                         size=(900,440), 
                         cols=[('Location',200),
                               ('Username',250),
                               ('Password',150),
                               ('Category',100),
                               ('Comments',250)])
                         
        self.addEntry = wx.Button(self, wx.ID_ANY, 'Add Entry')
        
        #Layout items
        hBoxes = []
        hBoxes.append(wx.BoxSizer(wx.HORIZONTAL))
        hBoxes[-1].Add(self.icon, 0, wx.ALL, 5)
        hBoxes[-1].Add(progLabel, 1, 
                       wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT, 5)
        
        hBoxes.append(wx.BoxSizer(wx.HORIZONTAL))
        hBoxes[-1].Add(self.entryList, 1, wx.EXPAND|wx.ALL, 5)
        
        hBoxes.append(wx.BoxSizer(wx.HORIZONTAL))
        
        hBoxes[-1].Add(catLabel, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        hBoxes[-1].Add(self.categorySelect, 1, wx.EXPAND|wx.ALL, 5)
        hBoxes[-1].Add(self.addEntry, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)

        self.vBox =  wx.BoxSizer(wx.VERTICAL)
        for hBox in hBoxes:
            self.vBox.Add(hBox, 0, wx.EXPAND|wx.ALL, 5)

        self.SetSizer(self.vBox)
        self.vBox.Fit(self)
        
        # Bind events
        self.Bind(wx.EVT_BUTTON, self._add_entry, self.addEntry)
        self.Bind(wx.EVT_COMBOBOX, self._change_category, self.categorySelect)
        self.entryList.Bind(wx.EVT_LEFT_DCLICK, self._edit_entry)
        self.entryList.Bind(wx.EVT_CONTEXT_MENU, self._call_entry_menu)
        self.Bind(wx.EVT_LIST_KEY_DOWN, self._check_keypress, self.entryList)
        
        self.update()
        
    #-------------------------------------------------------------------------- 
    def _check_keypress(self, event):
        """ Check for enter or delete, otherwise ignore """
        if event.GetKeyCode() == wx.WXK_DELETE:
            self._delete_entry(event)
        elif event.GetKeyCode() == wx.WXK_RETURN:
            self._edit_entry(event)
        else:
            event.Skip()
        
    #-------------------------------------------------------------------------- 
    def _change_category(self, event):
        """ Update panel display if the selected category is changed """
        self.update()
        
    #-------------------------------------------------------------------------- 
    def _call_entry_menu(self, event):
        """ 
        Open right-click context menu if an item is right clicked on, but
        ignore right-clicks in the white space where no items are
        """
        try:
            entry = self.entryList.GetCurrentObject()
            self.PopupMenu(EntryMenu(self, entry))
        except (KeyError, IndexError): # ignore errors when no items selected
            pass
        
    #-------------------------------------------------------------------------- 
    def _edit_entry(self, event):
        """ Open a popup display to edit an entry """
        
        entry = self.entryList.GetCurrentObject()
        
        dlg = EditEntryDialog(self, 'Update', entry)
        
        if dlg.ShowModal() == wx.ID_OK:
            newEntry = dlg.GetNewItem()
            if newEntry != entry:
                self.data.UpdateEntry(entry.tag, newEntry)
                self.update()
                self.parent.CheckSave()
            
        dlg.Destroy()
        
    #-------------------------------------------------------------------------- 
    def _delete_entry(self, event):
        """ Confirm, then delete an entry """
        
        dlg = wx.MessageDialog(None, 
                               'Are you sure you want to delete this entry?',
                               'Confirm Delete',
                               wx.YES_NO|wx.NO_DEFAULT|wx.ICON_QUESTION)
                                   
        if dlg.ShowModal() == wx.ID_YES:
            entry = self.entryList.GetCurrentObject()
            self.data.entries.remove(entry)
            self.update()
            self.parent.CheckSave()
                
        dlg.Destroy()
    

    #-------------------------------------------------------------------------- 
    def _add_entry(self, event):
        """ Add a new entry, but do not allow exact duplicates """
        
        dlg = EditEntryDialog(self, 'Add')
        
        if dlg.ShowModal() == wx.ID_OK:
            newEntry = dlg.GetNewItem()
            
            if newEntry not in self.data.entries:
                self.data.entries.append(newEntry)
                self.update()
                self.parent.CheckSave()
                
            else:
                edlg = wx.MessageDialog\
                       (
                           None, 
                           'New entry is an exact duplicate of one '+
                           'already in the database',
                           'Entry Error', 
                           wx.OK|wx.ICON_ERROR
                       )
                       
                edlg.ShowModal()
                edlg.Destroy()
                
        dlg.Destroy()
         
    #-------------------------------------------------------------------------- 
    def update(self):
        """ Update the entry list display and category list in the panel """
        
        cat = self.categorySelect.GetValue()  # currently selected category
        cats = self.data.GetCategories()      # all categories (including new)
        idx = cats.index(cat)                 # index of current in new list
        
        self.categorySelect.Clear()
        self.categorySelect.AppendItems(cats)
        self.categorySelect.SetSelection(idx)
        
        self.entryList.update_objects(self.data.GetEntries(cat))
        
