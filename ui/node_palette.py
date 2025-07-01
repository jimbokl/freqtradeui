"""
Node palette widget for displaying available nodes
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QScrollArea, 
    QPushButton, QLabel, QHBoxLayout, QFrame
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont


class NodeButton(QPushButton):
    """Custom button for node palette"""
    
    def __init__(self, node_type, display_name, description=""):
        super().__init__(display_name)
        self.node_type = node_type
        self.description = description
        
        # Style the button
        self.setFixedHeight(40)
        self.setToolTip(description)
        self.setStyleSheet("""
            QPushButton {
                text-align: left;
                padding: 8px;
                border: 1px solid #ccc;
                border-radius: 4px;
                background-color: #f0f0f0;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
                border-color: #999;
            }
            QPushButton:pressed {
                background-color: #d0d0d0;
            }
        """)


class NodePalette(QWidget):
    """Left panel containing available nodes for drag-and-drop"""
    
    # Signal emitted when user wants to create a node
    node_requested = Signal(str)  # node_type
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.populate_nodes()
    
    def setup_ui(self):
        """Setup the UI layout"""
        self.setFixedWidth(200)
        self.setMinimumHeight(400)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)
        
        # Title
        title = QLabel("Node Palette")
        title.setFont(QFont("", 12, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(separator)
        
        # Scroll area for buttons
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # Container for node buttons
        self.buttons_container = QWidget()
        self.buttons_layout = QVBoxLayout(self.buttons_container)
        self.buttons_layout.setContentsMargins(4, 4, 4, 4)
        self.buttons_layout.setSpacing(4)
        
        scroll_area.setWidget(self.buttons_container)
        layout.addWidget(scroll_area)
        
        # Stretch at the bottom
        layout.addStretch()
    
    def populate_nodes(self):
        """Populate the palette with available node types"""
        
        # Define the 8 basic node types as per specification
        node_definitions = [
            {
                'type': 'market_data',
                'name': 'Market Data',
                'description': 'Provides market candle data\nInputs: none\nOutputs: candles dataframe'
            },
            {
                'type': 'indicator',
                'name': 'Indicator',
                'description': 'Technical indicators (EMA, RSI, Bollinger Bands)\nInputs: candles\nOutputs: indicator series'
            },
            {
                'type': 'math',
                'name': 'Math',
                'description': 'Mathematical operations\nInputs: A, B\nOutputs: result series'
            },
            {
                'type': 'logic',
                'name': 'Logic',
                'description': 'Logical operations (AND, OR, NOT)\nInputs: conditions\nOutputs: boolean mask'
            },
            {
                'type': 'enter',
                'name': 'Enter Signal',
                'description': 'Entry signal for trades\nInputs: signal\nOutputs: entry flags'
            },
            {
                'type': 'exit',
                'name': 'Exit Signal',
                'description': 'Exit signal for trades\nInputs: signal\nOutputs: exit flags'
            },
            {
                'type': 'hyperopt_param',
                'name': 'Hyperopt Param',
                'description': 'Hyperoptimization parameter\nInputs: none\nOutputs: parameter value'
            },
            {
                'type': 'plot',
                'name': 'Plot',
                'description': 'Plot data on chart\nInputs: series\nOutputs: none'
            }
        ]
        
        # Create buttons for each node type
        for node_def in node_definitions:
            button = NodeButton(
                node_def['type'],
                node_def['name'],
                node_def['description']
            )
            button.clicked.connect(lambda checked, t=node_def['type']: self.request_node_creation(t))
            self.buttons_layout.addWidget(button)
        
        # Add stretch to push buttons to top
        self.buttons_layout.addStretch()
    
    def request_node_creation(self, node_type):
        """Request creation of a new node"""
        self.node_requested.emit(node_type)
