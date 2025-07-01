"""
Property panel for editing node properties
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QScrollArea, QLabel, 
    QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox,
    QCheckBox, QGroupBox, QFormLayout, QFrame
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont


class PropertyPanel(QWidget):
    """Right panel for editing selected node properties"""
    
    def __init__(self):
        super().__init__()
        self.current_node = None
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the UI layout"""
        self.setFixedWidth(250)
        self.setMinimumHeight(400)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)
        
        # Title
        title = QLabel("Properties")
        title.setFont(QFont("", 12, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(separator)
        
        # Scroll area for properties
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # Container for property widgets
        self.properties_container = QWidget()
        self.properties_layout = QVBoxLayout(self.properties_container)
        self.properties_layout.setContentsMargins(4, 4, 4, 4)
        self.properties_layout.setSpacing(8)
        
        # Default message when no node selected
        self.no_selection_label = QLabel("Select a node to edit its properties")
        self.no_selection_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.no_selection_label.setWordWrap(True)
        self.no_selection_label.setStyleSheet("color: #666; font-style: italic;")
        self.properties_layout.addWidget(self.no_selection_label)
        
        scroll_area.setWidget(self.properties_container)
        layout.addWidget(scroll_area)
        
        # Stretch at the bottom
        layout.addStretch()
    
    def set_node(self, node):
        """Set the currently selected node and show its properties"""
        self.current_node = node
        self.update_properties()
    
    def update_properties(self):
        """Update the properties panel based on current node"""
        # Clear existing widgets
        self.clear_properties()
        
        if not self.current_node:
            # Show default message
            self.no_selection_label = QLabel("Select a node to edit its properties")
            self.no_selection_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.no_selection_label.setWordWrap(True)
            self.no_selection_label.setStyleSheet("color: #666; font-style: italic;")
            self.properties_layout.addWidget(self.no_selection_label)
            return
        
        # Node info group
        info_group = QGroupBox("Node Info")
        info_layout = QFormLayout(info_group)
        
        # Node name (editable)
        name_edit = QLineEdit(self.current_node.name())
        name_edit.textChanged.connect(lambda text: self.current_node.set_name(text))
        info_layout.addRow("Name:", name_edit)
        
        # Node type (read-only)
        type_label = QLabel(self.current_node.type_)
        type_label.setStyleSheet("color: #666;")
        info_layout.addRow("Type:", type_label)
        
        self.properties_layout.addWidget(info_group)
        
        # Node-specific properties based on type
        self.add_node_specific_properties()
        
        # Add stretch at the end
        self.properties_layout.addStretch()
    
    def add_node_specific_properties(self):
        """Add properties specific to the node type"""
        if not self.current_node:
            return
        
        node_type = self.current_node.type_
        
        # Добавляем специфичные свойства для каждого типа узла
        if "MarketData" in node_type or node_type == "MarketDataNode":
            self.add_market_data_properties()
        elif "Indicator" in node_type or node_type == "IndicatorNode":
            self.add_indicator_properties()
        elif "Math" in node_type or node_type == "MathNode":
            self.add_math_properties()
        elif "Logic" in node_type or node_type == "LogicNode":
            self.add_logic_properties()
        elif "Enter" in node_type or node_type == "EnterNode":
            self.add_enter_properties()
        elif "Exit" in node_type or node_type == "ExitNode":
            self.add_exit_properties()
        elif "Hyperopt" in node_type or node_type == "HyperoptParamNode":
            self.add_hyperopt_properties()
        elif "Plot" in node_type or node_type == "PlotNode":
            self.add_plot_properties()
        else:
            # Для неизвестных типов узлов, показываем все доступные параметры
            self.add_generic_properties()
    
    def add_dynamic_parameters(self, skip_keys=None):
        """Динамически добавить все параметры узла, кроме уже отображённых вручную"""
        if not self.current_node:
            return
        
        # Получаем параметры из узла
        params = {}
        
        # Пробуем принудительно инициализировать параметры
        if hasattr(self.current_node, 'ensure_parameters_initialized'):
            params = self.current_node.ensure_parameters_initialized()
        elif hasattr(self.current_node, 'get_parameters'):
            params = self.current_node.get_parameters()
        
        # Если параметров всё ещё нет, пытаемся получить их напрямую
        if not params and hasattr(self.current_node, '_parameters'):
            params = self.current_node._parameters
        
        skip_keys = set(skip_keys or [])
        
        if not params:
            # Если параметров всё ещё нет, добавляем информационное сообщение
            info_group = QGroupBox("Информация")
            info_layout = QFormLayout(info_group)
            info_label = QLabel("Параметры не найдены для этого узла.\nВозможно, узел не инициализирован правильно.")
            info_label.setWordWrap(True)
            info_layout.addRow(info_label)
            self.properties_layout.addWidget(info_group)
            return
        
        # Создаем группу для всех параметров
        group = QGroupBox(f"Все параметры ({len(params)} шт.)")
        layout = QFormLayout(group)
        
        # Добавляем счетчик отображенных параметров
        displayed_count = 0
        
        for key, value in params.items():
            if key in skip_keys:
                continue
                
            displayed_count += 1
            
            # Определяем тип виджета по типу значения
            if isinstance(value, bool):
                widget = QCheckBox()
                widget.setChecked(value)
                widget.stateChanged.connect(lambda state, k=key: self.update_parameter(k, bool(state)))
            elif isinstance(value, int):
                widget = QSpinBox()
                widget.setRange(-999999, 999999)
                widget.setValue(value)
                widget.valueChanged.connect(lambda v, k=key: self.update_parameter(k, v))
            elif isinstance(value, float):
                widget = QDoubleSpinBox()
                widget.setRange(-999999.0, 999999.0)
                widget.setDecimals(4)
                widget.setValue(value)
                widget.valueChanged.connect(lambda v, k=key: self.update_parameter(k, v))
            elif isinstance(value, list):
                widget = QLineEdit(','.join(map(str, value)))
                widget.textChanged.connect(lambda text, k=key: self.update_parameter(k, [x.strip() for x in text.split(',') if x.strip()]))
            else:
                widget = QLineEdit(str(value))
                widget.textChanged.connect(lambda text, k=key: self.update_parameter(k, text))
            
            # Добавляем подсказку с типом значения
            label_text = f"{key} ({type(value).__name__})"
            layout.addRow(label_text, widget)
        
        # Обновляем заголовок группы с количеством отображенных параметров
        group.setTitle(f"Параметры узла ({displayed_count} отображено)")
        self.properties_layout.addWidget(group)
    
    def update_parameter(self, key, value):
        """Обновить параметр узла"""
        if not self.current_node:
            return
        
        if hasattr(self.current_node, 'set_parameter'):
            self.current_node.set_parameter(key, value)
        elif hasattr(self.current_node, '_parameters'):
            self.current_node._parameters[key] = value
    
    def add_market_data_properties(self):
        """Add properties for MarketData node"""
        group = QGroupBox("Market Data Settings")
        layout = QFormLayout(group)
        
        # Pair selection
        pair_combo = QComboBox()
        pair_combo.addItems(["BTC/USDT", "ETH/USDT", "ADA/USDT", "DOT/USDT"])
        pair_combo.setEditable(True)
        current_pair = self.current_node.get_parameter('pair', 'BTC/USDT')
        pair_combo.setCurrentText(current_pair)
        pair_combo.currentTextChanged.connect(lambda text: self.current_node.set_parameter('pair', text))
        layout.addRow("Pair:", pair_combo)
        
        # Timeframe
        timeframe_combo = QComboBox()
        timeframe_combo.addItems(["1m", "5m", "15m", "30m", "1h", "4h", "1d"])
        current_timeframe = self.current_node.get_parameter('timeframe', '1h')
        timeframe_combo.setCurrentText(current_timeframe)
        timeframe_combo.currentTextChanged.connect(lambda text: self.current_node.set_parameter('timeframe', text))
        layout.addRow("Timeframe:", timeframe_combo)
        
        # Lookback period
        lookback_spin = QSpinBox()
        lookback_spin.setRange(1, 10000)
        lookback_spin.setValue(self.current_node.get_parameter('lookback', 500))
        lookback_spin.valueChanged.connect(lambda value: self.current_node.set_parameter('lookback', value))
        layout.addRow("Lookback:", lookback_spin)
        
        self.properties_layout.addWidget(group)
        # Динамические параметры
        self.add_dynamic_parameters(skip_keys=['pair', 'timeframe', 'lookback'])
    
    def add_indicator_properties(self):
        """Add properties for Indicator node"""
        group = QGroupBox("Indicator Settings")
        layout = QFormLayout(group)
        
        # Indicator type
        indicator_combo = QComboBox()
        indicator_combo.addItems([
            "EMA", "SMA", "RSI", "MACD", "Bollinger Bands", 
            "Stochastic", "Williams %R", "ATR"
        ])
        current_indicator = self.current_node.get_parameter('indicator_type', 'EMA')
        indicator_combo.setCurrentText(current_indicator)
        indicator_combo.currentTextChanged.connect(lambda text: self.current_node.set_parameter('indicator_type', text))
        layout.addRow("Type:", indicator_combo)
        
        # Window/Period
        period_spin = QSpinBox()
        period_spin.setRange(1, 200)
        period_spin.setValue(self.current_node.get_parameter('period', 14))
        period_spin.valueChanged.connect(lambda value: self.current_node.set_parameter('period', value))
        layout.addRow("Period:", period_spin)
        
        # Source
        source_combo = QComboBox()
        source_combo.addItems(["close", "open", "high", "low", "hl2", "hlc3", "ohlc4"])
        current_source = self.current_node.get_parameter('source', 'close')
        source_combo.setCurrentText(current_source)
        source_combo.currentTextChanged.connect(lambda text: self.current_node.set_parameter('source', text))
        layout.addRow("Source:", source_combo)
        
        self.properties_layout.addWidget(group)
        # Динамические параметры
        self.add_dynamic_parameters(skip_keys=['indicator_type', 'period', 'source'])
    
    def add_math_properties(self):
        """Add properties for Math node"""
        group = QGroupBox("Math Operation")
        layout = QFormLayout(group)
        
        # Operation type
        operation_combo = QComboBox()
        operation_combo.addItems([
            "add", "subtract", "multiply", "divide", "power", "max", "min"
        ])
        current_operation = self.current_node.get_parameter('operation', 'add')
        operation_combo.setCurrentText(current_operation)
        operation_combo.currentTextChanged.connect(lambda text: self.current_node.set_parameter('operation', text))
        layout.addRow("Operation:", operation_combo)
        
        # Constant value (optional)
        constant_spin = QDoubleSpinBox()
        constant_spin.setRange(-999999, 999999)
        constant_spin.setDecimals(4)
        constant_spin.setValue(self.current_node.get_parameter('constant', 0.0))
        constant_spin.valueChanged.connect(lambda value: self.current_node.set_parameter('constant', value))
        layout.addRow("Constant:", constant_spin)
        
        self.properties_layout.addWidget(group)
        # Динамические параметры
        self.add_dynamic_parameters(skip_keys=['operation', 'constant'])
    
    def add_logic_properties(self):
        """Add properties for Logic node"""
        group = QGroupBox("Logic Operation")
        layout = QFormLayout(group)
        
        # Logic type
        logic_combo = QComboBox()
        logic_combo.addItems(["AND", "OR", "NOT", "XOR"])
        current_logic = self.current_node.get_parameter('operation', 'AND')
        logic_combo.setCurrentText(current_logic)
        logic_combo.currentTextChanged.connect(lambda text: self.current_node.set_parameter('operation', text))
        layout.addRow("Operation:", logic_combo)
        
        self.properties_layout.addWidget(group)
        # Динамические параметры
        self.add_dynamic_parameters(skip_keys=['operation'])
    
    def add_enter_properties(self):
        """Add properties for Enter node"""
        group = QGroupBox("Entry Settings")
        layout = QFormLayout(group)
        
        # Trade side
        side_combo = QComboBox()
        side_combo.addItems(["Long", "Short", "Both"])
        layout.addRow("Side:", side_combo)
        
        # Position size
        size_spin = QDoubleSpinBox()
        size_spin.setRange(0.01, 100.0)
        size_spin.setDecimals(2)
        size_spin.setValue(1.0)
        size_spin.setSuffix(" %")
        layout.addRow("Position Size:", size_spin)
        
        self.properties_layout.addWidget(group)
        # Динамические параметры
        self.add_dynamic_parameters(skip_keys=['side', 'position_size'])
    
    def add_exit_properties(self):
        """Add properties for Exit node"""
        group = QGroupBox("Exit Settings")
        layout = QFormLayout(group)
        
        # Trade side
        side_combo = QComboBox()
        side_combo.addItems(["Long", "Short", "Both"])
        layout.addRow("Side:", side_combo)
        
        # Stop loss
        stop_loss_check = QCheckBox("Enable Stop Loss")
        layout.addRow(stop_loss_check)
        
        stop_loss_spin = QDoubleSpinBox()
        stop_loss_spin.setRange(0.1, 50.0)
        stop_loss_spin.setDecimals(1)
        stop_loss_spin.setValue(5.0)
        stop_loss_spin.setSuffix(" %")
        layout.addRow("Stop Loss:", stop_loss_spin)
        
        # Take profit
        take_profit_check = QCheckBox("Enable Take Profit")
        layout.addRow(take_profit_check)
        
        take_profit_spin = QDoubleSpinBox()
        take_profit_spin.setRange(0.1, 100.0)
        take_profit_spin.setDecimals(1)
        take_profit_spin.setValue(10.0)
        take_profit_spin.setSuffix(" %")
        layout.addRow("Take Profit:", take_profit_spin)
        
        self.properties_layout.addWidget(group)
        # Динамические параметры
        self.add_dynamic_parameters(skip_keys=['side', 'enable_stop_loss', 'stop_loss_pct', 'enable_take_profit', 'take_profit_pct'])
    
    def add_hyperopt_properties(self):
        """Add properties for HyperoptParam node"""
        group = QGroupBox("Hyperopt Parameter")
        layout = QFormLayout(group)
        
        # Parameter name
        name_edit = QLineEdit("param_name")
        layout.addRow("Name:", name_edit)
        
        # Parameter type
        type_combo = QComboBox()
        type_combo.addItems(["Integer", "Real", "Categorical"])
        layout.addRow("Type:", type_combo)
        
        # Range (for Integer/Real)
        min_spin = QDoubleSpinBox()
        min_spin.setRange(-999999, 999999)
        min_spin.setValue(0.0)
        layout.addRow("Min Value:", min_spin)
        
        max_spin = QDoubleSpinBox()
        max_spin.setRange(-999999, 999999)
        max_spin.setValue(100.0)
        layout.addRow("Max Value:", max_spin)
        
        # Choices (for Categorical)
        choices_edit = QLineEdit("choice1,choice2,choice3")
        layout.addRow("Choices:", choices_edit)
        
        self.properties_layout.addWidget(group)
        # Динамические параметры
        self.add_dynamic_parameters(skip_keys=['param_name', 'param_type', 'min_value', 'max_value', 'choices'])
    
    def add_plot_properties(self):
        """Add properties for Plot node"""
        group = QGroupBox("Plot Settings")
        layout = QFormLayout(group)
        
        # Plot label
        label_edit = QLineEdit("Plot Label")
        layout.addRow("Label:", label_edit)
        
        # Color
        color_combo = QComboBox()
        color_combo.addItems([
            "Blue", "Red", "Green", "Orange", "Purple", 
            "Cyan", "Magenta", "Yellow", "Black"
        ])
        layout.addRow("Color:", color_combo)
        
        # Plot type
        plot_type_combo = QComboBox()
        plot_type_combo.addItems(["Line", "Scatter", "Bar"])
        layout.addRow("Type:", plot_type_combo)
        
        # Subplot
        subplot_check = QCheckBox("Separate Subplot")
        layout.addRow(subplot_check)
        
        self.properties_layout.addWidget(group)
        # Динамические параметры
        self.add_dynamic_parameters(skip_keys=['label', 'color', 'plot_type', 'subplot'])
    
    def add_generic_properties(self):
        """Add properties for unknown node types"""
        group = QGroupBox("Общие параметры")
        layout = QFormLayout(group)
        
        # Показываем тип узла
        type_label = QLabel(self.current_node.type_)
        type_label.setStyleSheet("color: #666; font-style: italic;")
        layout.addRow("Тип узла:", type_label)
        
        # Показываем идентификатор если есть
        if hasattr(self.current_node, '__identifier__'):
            identifier_label = QLabel(self.current_node.__identifier__)
            identifier_label.setStyleSheet("color: #666; font-style: italic;")
            layout.addRow("Идентификатор:", identifier_label)
        
        self.properties_layout.addWidget(group)
        # Динамические параметры (все доступные)
        self.add_dynamic_parameters(skip_keys=[])
    
    def clear_properties(self):
        """Clear all property widgets"""
        while self.properties_layout.count():
            child = self.properties_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
