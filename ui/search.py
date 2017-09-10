from maya import cmds

# import pyside, do qt version check for maya 2017 >
qtVersion = cmds.about(qtVersion=True)
if qtVersion.startswith("4"):
    from PySide.QtGui import *
    from PySide.QtCore import *
    import shiboken
else:
    from PySide2.QtGui import *
    from PySide2.QtCore import *
    from PySide2.QtWidgets import *
    import shiboken2 as shiboken
      
from . import manager, results, utils
from .. import commands

# ---------------------------------------------------------------------------

BAR_CLOSE_ICON = QPixmap( ":/closeBar.png" )
BAR_OPEN_ICON  = QPixmap( ":/openBar.png" )

# ---------------------------------------------------------------------------
    
class SearchWidget(QWidget):
    """
    Search Widget 
    
    The search widget will give access to all of the functionality in the 
    command search package.
    
    * Search input field.
    * Pin set manager.
    * Search results.
    
    :param QWidget parent:
    """
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        
        # get commands
        if not commands.get():
            commands.store(utils.mayaMenu())
            
        # variable
        self.setObjectName("CMDSearch")
        
        # create layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(1)
            
        # create bar
        self.bar = QPushButton(self)
        self.bar.setFlat(True)
        self.bar.setFixedWidth(8)
        self.bar.setFixedHeight(25)   
        self.bar.setIcon(BAR_CLOSE_ICON)
        self.bar.setIconSize(QSize(8,25))
        
        # create container
        self.container = QWidget(self)
        self.container.setFixedWidth(250)
        
        # add widgets
        layout.addWidget(self.bar)
        layout.addWidget(self.container)
        
        # create layout
        layout = QHBoxLayout(self.container)
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(1)
        
        button = QPushButton(self)
        button.setFlat(True)
        button.setFixedWidth(25)
        button.setFixedHeight(25)   
        button.setIcon(utils.findSearchIcon())
        button.setIconSize(QSize(25,25))   
        
        self.search = SearchEdit(self, self.container)
        
        # add widgets
        layout.addWidget(button)
        layout.addWidget(self.search)
          
        # add signals
        self.search.textChanged.connect(self.typing)
        self.search.returnPressed.connect(self.enter)
        self.bar.released.connect(self.switch)
        
        button.setMenu(manager.ManagerMenu(self))
        
        # window
        self.window = results.ResultsWindow(self)
        self.window.aboutToClose.connect(self.closeWindowEvent)
        
        # menu
        self.menu = results.ResultsMenu(self)
        self.menu.aboutToClose.connect(self.closeMenuEvent)
        
        self.results = self.menu
        
    # ------------------------------------------------------------------------
        
    def typing(self):
        """
        Typing callback, since there are many commands to filter through, 
        when typing it will only start processing when there are at least
        4 characters typed.
        """
        self.process(4)
 
    def enter(self):  
        """
        Enter callback, will call the process function regardless of how many
        characters the input field holds, used when you want to search for 
        something with less than 4 char
        """
        self.process(0)
        
    # ------------------------------------------------------------------------
    
    def process(self, num):
        """
        Process the search command, the number determines how many characters
        the search string should at least be for it to continue.
        
        :param int num: Search character number at least before process
        """
        # filter search
        search = str(self.search.text())
        if len(search) < num:      
            search = None
          
        # filter commands
        matches = commands.filter(search)

        # add commands
        widget = self.results.widget
        widget.populate(matches)
        
        # display
        num = len(matches)
        self.results.show(num)

        # set focus
        self.search.setFocus()
        
    # ------------------------------------------------------------------------
    
    def closeWindowEvent(self):
        self.results.hide()
        self.results = self.menu
        
    def closeMenuEvent(self):
        self.results.hide()
        self.results = self.window
        
        self.typing()

    # ------------------------------------------------------------------------
        
    def switch(self):
        """
        Switch visibility of the widget, it is build in the same style as all
        if the maya status line ui elements.
        """
        if self.container.isVisible():
            self.container.setVisible(False)
            self.bar.setIcon(BAR_CLOSE_ICON)
        else:
            self.container.setVisible(True)
            self.bar.setIcon(BAR_OPEN_ICON)
            
# ----------------------------------------------------------------------------

class SearchEdit(QLineEdit):
    """
    Subclass of a line edit to force it to show the parents results window
    on release of the left buttons.
    """
    def __init__(self, parent, widgetParent):
        QLineEdit.__init__(self, widgetParent)
        self.parent = parent
        
    # -----------------------------------------------------------------------

    def mouseReleaseEvent(self, e): 
        if e.button() == Qt.LeftButton:                
            if not self.parent.results.isVisible():
                self.parent.typing()
                
        QLineEdit.mouseReleaseEvent(self, e)