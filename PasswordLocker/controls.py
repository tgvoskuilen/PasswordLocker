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
import math
import wx.lib.agw.pygauge as PG

###############################################################################
class StrengthGauge(PG.PyGauge):
    """
    A custom progress bar for showing password strength. It scales 
    logarithmically with mean password cracking time and changes the bar
    color for more secure passwords.
    
    The scale goes up to cracking times of about 3 million years (2^30 days)
    """
    def __init__(self, parent, size, style):
        PG.PyGauge.__init__(self, parent, wx.ID_ANY, size=size, style=style )
        self.SetRange(32.)
        self.SetValue(0.5)
        self.SetBarColor(wx.RED)
        
    #-------------------------------------------------------------------------- 
    def UpdateStrength(self, nDays):
        """
        Update the progress bar based on days to crack password. Scale is
        logarithmic and colors change at 30 days and 10 years cracking time.
        """
        oldVal = self.GetValue()
        
        if nDays > 0.:
            newVal = max([0, min([30., math.log(nDays,2)])]) + 2.
        else:
            newVal = 0.5
            
        if nDays < 30:
            self.SetBarColor(wx.RED)
        elif nDays < 3650:
            self.SetBarColor(wx.Colour(255,153,51))
        else:
            self.SetBarColor(wx.GREEN)
        
        if abs(newVal - oldVal) > 1e-3:
            self.Update(newVal - oldVal, 50)
    

###############################################################################
class ObjectListCtrl(wx.ListCtrl):
    """
    A wx.ListCtrl object that can have objects associated with it
    more easily than a standard ListCtrl.
    """
    def __init__(self, *args, **kwargs):
        cols = kwargs.get('cols')
        del kwargs['cols']
        wx.ListCtrl.__init__(self, *args, **kwargs)
        self._map = {}

        for i, col in enumerate(cols):
            self.InsertColumn(i, col[0], width=col[1])
            
        self.Arrange()
        

    #-------------------------------------------------------------------------- 
    def update_objects(self, objects):
        """
        In this case, 'objects' is a list of objects. Each object must
        have a unique attribute 'tag', must provide a list of strings for all
        columns with the col_strings() function, and must provide a sorting
        name with the sorting_name() function
        
        If a single entry is changed, this just looks up that entry and 
        re-writes its columns. If entries are deleted, it rebuilds the list.
        """
        
        # Deal with deleted objects still in the ListCtrl
        objkeys = [obj.tag for obj in objects]
                
        if sorted(objkeys) != sorted(self._map.keys()):
            self.DeleteAllItems()
            self._map.clear()
        
        # Sort objects alphabetically by sorting_name()
        sortedObjects = sorted(objects, key=lambda k: k.sorting_name())
        
        for obj in sortedObjects:
            # Check if obj is already in the list
            if obj.tag in self._map:
                # Find obj's row in the table
                self._map[obj.tag] = obj
                keys = [self.GetItemData(x) for x in range(self.GetItemCount())]
                row = keys.index(obj.tag)

            else:
                # Add obj at the end of the list and get its row
                self._map[obj.tag] = obj
                row = self.InsertStringItem(self.GetItemCount(), str(obj.tag))
                self.SetItemData(row, obj.tag)

            # Update values in specified row, all columns
            for i,s in enumerate(obj.col_strings()):
                self.SetStringItem(row, i, s)
                
    #-------------------------------------------------------------------------- 
    def GetCurrentObject(self):
        tag = self.GetItemData(self.GetFirstSelected())
        return self._map[tag]
        

        
###############################################################################
class EntryMenu(wx.Menu):
    """ 
    Right click context menu for entries in the list panel with Edit and Delete
    options
    """
    def __init__(self, parent, entry):
        wx.Menu.__init__(self)
  
        mi = wx.MenuItem(self, wx.NewId(), 'Edit')
        self.AppendItem(mi)
        self.Bind(wx.EVT_MENU, lambda event: parent._edit_entry(entry), mi)
        
        mi = wx.MenuItem(self, wx.NewId(), 'Delete')
        self.AppendItem(mi)
        self.Bind(wx.EVT_MENU, lambda event: parent._delete_entry(entry), mi)
        

            
