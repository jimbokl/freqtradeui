"""
Main window for RDP application
Contains the visual strategy builder interface
"""

from pathlib import Path
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QSplitter, QMenuBar, QToolBar, QStatusBar,
    QFileDialog, QMessageBox, QPushButton,
    QTabWidget, QTextEdit, QLabel
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QKeySequence, QIcon, QAction

from NodeGraphQt import NodeGraph
from .node_palette import NodePalette
from .property_panel import PropertyPanel
from .results_panel import ResultsPanel
from exporter import StrategyExporter
from runner import FreqtradeRunner, BacktestThread, HyperoptThread
from nodes.base_nodes import NODE_CLASSES


# BacktestThread imported from runner.py

class MainWindow(QMainWindow):
    """Main application window with visual strategy builder"""
    
    def __init__(self):
        super().__init__()
        self.current_file = None
        self.graph = None
        self.exporter = StrategyExporter()
        self.runner = FreqtradeRunner()
        
        self.setup_ui()
        self.setup_menu_bar()
        self.setup_toolbar()
        self.setup_status_bar()
        self.connect_signals()
        
        # Load default strategy for immediate testing
        self.load_default_strategy()
    
    def setup_ui(self):
        """Setup the main UI layout"""
        self.setWindowTitle("RDP for Freqtrade v0.2")
        self.setMinimumSize(1200, 800)
        self.resize(1400, 900)
        
        # Central widget with splitter layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main horizontal splitter
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        central_widget_layout = QVBoxLayout(central_widget)
        central_widget_layout.addWidget(main_splitter)
        
        # Left panel - Node palette
        self.node_palette = NodePalette()
        main_splitter.addWidget(self.node_palette)
        
        # Center - Canvas area with vertical splitter
        canvas_splitter = QSplitter(Qt.Orientation.Vertical)
        
        # Node graph canvas
        self.graph = NodeGraph()
        
        # Register node types
        for node_type, node_class in NODE_CLASSES.items():
            self.graph.register_node(node_class)
        
        # Set context menu (will create later)
        # self.graph.set_context_menu_from_file('ui/context_menu.json')
        canvas_splitter.addWidget(self.graph.widget)
        
        # Bottom panel - Results tabs
        self.results_panel = ResultsPanel()
        canvas_splitter.addWidget(self.results_panel)
        
        # Set splitter proportions
        canvas_splitter.setSizes([600, 200])
        main_splitter.addWidget(canvas_splitter)
        
        # Right panel - Properties
        self.property_panel = PropertyPanel()
        main_splitter.addWidget(self.property_panel)
        
        # Set main splitter proportions
        main_splitter.setSizes([200, 800, 200])
    
    def setup_menu_bar(self):
        """Setup application menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        
        # New strategy
        new_action = QAction("&New Strategy", self)
        new_action.setShortcut(QKeySequence.StandardKey.New)
        new_action.triggered.connect(self.new_strategy)
        file_menu.addAction(new_action)
        
        # Open strategy
        open_action = QAction("&Open Strategy", self)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.triggered.connect(self.open_strategy)
        file_menu.addAction(open_action)
        
        file_menu.addSeparator()
        
        # Load Examples submenu
        examples_menu = file_menu.addMenu("Load &Examples")
        
        ema_example_action = QAction("EMA Crossover Strategy", self)
        ema_example_action.triggered.connect(lambda: self.load_example_strategy("ema_crossover_example.json"))
        examples_menu.addAction(ema_example_action)
        
        rsi_example_action = QAction("RSI Strategy", self)
        rsi_example_action.triggered.connect(lambda: self.load_example_strategy("rsi_strategy_example.json"))
        examples_menu.addAction(rsi_example_action)
        
        # Save strategy
        save_action = QAction("&Save Strategy", self)
        save_action.setShortcut(QKeySequence.StandardKey.Save)
        save_action.triggered.connect(self.save_strategy)
        file_menu.addAction(save_action)
        
        # Save As
        save_as_action = QAction("Save &As...", self)
        save_as_action.setShortcut(QKeySequence.StandardKey.SaveAs)
        save_as_action.triggered.connect(self.save_strategy_as)
        file_menu.addAction(save_as_action)
        
        file_menu.addSeparator()
        
        # Export strategy
        export_action = QAction("&Export Strategy", self)
        export_action.setShortcut(QKeySequence("Ctrl+E"))
        export_action.triggered.connect(self.export_strategy)
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()
        
        # Exit
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit menu
        edit_menu = menubar.addMenu("&Edit")
        
        # Undo/Redo (handled by NodeGraphQt)
        undo_action = QAction("&Undo", self)
        undo_action.setShortcut(QKeySequence.StandardKey.Undo)
        undo_action.triggered.connect(self.undo_action)
        edit_menu.addAction(undo_action)
        
        redo_action = QAction("&Redo", self)
        redo_action.setShortcut(QKeySequence.StandardKey.Redo)
        redo_action.triggered.connect(self.redo_action)
        edit_menu.addAction(redo_action)
        
        # Help menu
        help_menu = menubar.addMenu("&Help")
        
        about_action = QAction("&About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def setup_toolbar(self):
        """Setup main toolbar with trading actions"""
        toolbar = self.addToolBar("Trading")
        toolbar.setMovable(False)
        
        # Backtest button
        self.backtest_btn = QPushButton("Backtest")
        self.backtest_btn.clicked.connect(self.run_backtest)
        toolbar.addWidget(self.backtest_btn)
        
        # Hyperopt button
        self.hyperopt_btn = QPushButton("Hyperopt")
        self.hyperopt_btn.clicked.connect(self.run_hyperopt)
        toolbar.addWidget(self.hyperopt_btn)
        
        # Live trading button
        self.live_btn = QPushButton("Live Trading")
        self.live_btn.clicked.connect(self.run_live)
        self.live_btn.setStyleSheet("QPushButton { color: red; font-weight: bold; }")
        toolbar.addWidget(self.live_btn)
        
        toolbar.addSeparator()
        
        # Status indicator
        self.status_label = QLabel("Ready")
        toolbar.addWidget(self.status_label)
    
    def setup_status_bar(self):
        """Setup status bar"""
        self.statusBar().showMessage("Ready")
    
    def connect_signals(self):
        """Connect various signals"""
        # Connect node selection to property panel
        self.graph.node_selected.connect(self.property_panel.set_node)
        
        # Connect palette to graph for node creation
        self.node_palette.node_requested.connect(self.create_node)
    
    def create_node(self, node_type):
        """Create a new node on the canvas"""
        try:
            if node_type in NODE_CLASSES:
                node_class = NODE_CLASSES[node_type]
                # NodeGraphQt automatically appends class name to identifier
                full_identifier = f"{node_class.__identifier__}.{node_class.__name__}"
                node = self.graph.create_node(full_identifier)
                
                # Position the node in the center of the visible area
                viewer = self.graph.viewer()
                center = viewer.mapToScene(viewer.rect().center())
                node.set_pos(center.x(), center.y())
                
                self.statusBar().showMessage(f"Created {node_class.NODE_NAME} node", 2000)
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create node: {str(e)}")
            print(f"Debug - Error creating node: {e}")
            print(f"Debug - Node type: {node_type}")
            if node_type in NODE_CLASSES:
                node_class = NODE_CLASSES[node_type]
                print(f"Debug - Node class: {node_class}")
                print(f"Debug - Identifier: {node_class.__identifier__}")
                print(f"Debug - Name: {node_class.NODE_NAME}")
                print(f"Debug - Class name: {node_class.__name__}")
                print(f"Debug - Full identifier: {node_class.__identifier__}.{node_class.__name__}")
    
    def new_strategy(self):
        """Create new strategy (clear canvas)"""
        if self.check_unsaved_changes():
            self.graph.clear_session()
            self.current_file = None
            self.setWindowTitle("RDP for Freqtrade v0.2 - New Strategy")
    
    def open_strategy(self):
        """Open strategy from JSON file"""
        if self.check_unsaved_changes():
            file_path, _ = QFileDialog.getOpenFileName(
                self, "Open Strategy", "", "JSON Files (*.json)"
            )
            if file_path:
                try:
                    self.graph.import_session(file_path)
                    self.current_file = file_path
                    self.setWindowTitle(f"RDP for Freqtrade v0.2 - {file_path}")
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to open strategy: {str(e)}")
    
    def save_strategy(self):
        """Save current strategy"""
        if self.current_file:
            try:
                self.graph.export_session(self.current_file)
                self.statusBar().showMessage(f"Strategy saved to {self.current_file}", 2000)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save strategy: {str(e)}")
        else:
            self.save_strategy_as()
    
    def save_strategy_as(self):
        """Save strategy with new name"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Strategy As", "", "JSON Files (*.json)"
        )
        if file_path:
            try:
                self.graph.export_session(file_path)
                self.current_file = file_path
                self.setWindowTitle(f"RDP for Freqtrade v0.2 - {file_path}")
                self.statusBar().showMessage(f"Strategy saved to {file_path}", 2000)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save strategy: {str(e)}")
    
    def export_strategy(self):
        """Export strategy to Python code"""
        try:
            strategy_code = self.exporter.export_graph(self.graph)
            
            # Save to file
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Export Strategy", "", "Python Files (*.py)"
            )
            if file_path:
                with open(file_path, 'w') as f:
                    f.write(strategy_code)
                self.statusBar().showMessage(f"Strategy exported to {file_path}", 2000)
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to export strategy: {str(e)}")
    
    def run_backtest(self):
        """Run backtest using Freqtrade CLI"""
        try:
            self.set_buttons_enabled(False)
            self.status_label.setText("Running backtest...")
            self.results_panel.log_message("Exporting strategy...", "INFO")
            
            # Export strategy first
            strategy_code = self.exporter.export_graph(self.graph)
            
            # Save exported strategy for debugging
            debug_file = Path(__file__).parent.parent / "user_data" / "strategies" / "debug_generated.py"
            debug_file.parent.mkdir(exist_ok=True)
            with open(debug_file, 'w') as f:
                f.write(strategy_code)
            
            self.results_panel.log_message(f"Strategy exported to {debug_file}", "SUCCESS")
            
            # Create and start backtest thread
            self.backtest_thread = BacktestThread(
                self.runner, 
                strategy_code, 
                "GeneratedStrategy"
            )
            
            # Connect signals
            self.backtest_thread.finished.connect(self.on_backtest_finished)
            self.backtest_thread.error.connect(self.on_backtest_error)
            self.backtest_thread.progress.connect(self.results_panel.log_message)
            
            # Start thread
            self.backtest_thread.start()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to run backtest: {str(e)}")
            self.set_buttons_enabled(True)
            self.status_label.setText("Ready")
    
    def on_backtest_finished(self, results):
        """Handle backtest completion"""
        self.set_buttons_enabled(True)
        self.status_label.setText("Ready")
        
        if results.get('success', False):
            self.results_panel.log_message("Backtest completed successfully!", "SUCCESS")
            self.results_panel.update_results(results)
        else:
            error_msg = results.get('error', 'Unknown error')
            self.results_panel.log_message(f"Backtest failed: {error_msg}", "ERROR")
    
    def on_backtest_error(self, error_msg):
        """Handle backtest error"""
        self.set_buttons_enabled(True)
        self.status_label.setText("Ready")
        self.results_panel.log_message(f"Backtest error: {error_msg}", "ERROR")
        QMessageBox.critical(self, "Backtest Error", f"Backtest failed:\n{error_msg}")
    
    def run_hyperopt(self):
        """Run hyperopt using Freqtrade CLI"""
        try:
            self.set_buttons_enabled(False)
            self.status_label.setText("Running hyperopt...")
            # TODO: Implement hyperopt execution
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to run hyperopt: {str(e)}")
            self.set_buttons_enabled(True)
            self.status_label.setText("Ready")
    
    def run_live(self):
        """Run live trading using Freqtrade CLI"""
        # Show confirmation dialog
        reply = QMessageBox.question(
            self, "Live Trading", 
            "Are you sure you want to start live trading?\nThis will use real money!",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.set_buttons_enabled(False)
                self.status_label.setText("Live trading active")
                # TODO: Implement live trading execution
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to start live trading: {str(e)}")
                self.set_buttons_enabled(True)
                self.status_label.setText("Ready")
    
    def set_buttons_enabled(self, enabled):
        """Enable/disable trading buttons"""
        self.backtest_btn.setEnabled(enabled)
        self.hyperopt_btn.setEnabled(enabled)
        self.live_btn.setEnabled(enabled)
    
    def check_unsaved_changes(self):
        """Check if there are unsaved changes and ask user"""
        # TODO: Implement change tracking
        return True
    
    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(
            self, "About RDP for Freqtrade",
            "RDP (Rapid Development Platform) for Freqtrade v0.2\n\n"
            "Visual strategy builder using drag-and-drop interface.\n"
            "Built with PySide6 and NodeGraphQt."
        )
    
    def closeEvent(self, event):
        """Handle window close event"""
        if self.check_unsaved_changes():
            event.accept()
        else:
            event.ignore()
    
    def undo_action(self):
        """Perform undo action"""
        try:
            if hasattr(self.graph, 'undo_stack'):
                self.graph.undo_stack().undo()
            elif hasattr(self.graph, 'undo'):
                self.graph.undo()
        except Exception as e:
            print(f"Undo failed: {e}")
    
    def redo_action(self):
        """Perform redo action"""
        try:
            if hasattr(self.graph, 'undo_stack'):
                self.graph.undo_stack().redo()
            elif hasattr(self.graph, 'redo'):
                self.graph.redo()
        except Exception as e:
            print(f"Redo failed: {e}")
    
    def load_default_strategy(self):
        """Load default EMA crossover strategy for immediate testing"""
        try:
            # Create a simple test strategy programmatically
            # Skip JSON loading for now as it causes import issues
            self.create_simple_test_strategy()
                
        except Exception as e:
            print(f"Failed to load default strategy: {e}")
            # Show welcome message if all else fails
            self.statusBar().showMessage("Welcome to RDP! Create nodes by clicking the palette on the left.", 3000)
    
    def create_simple_test_strategy(self):
        """Create a simple test strategy programmatically"""
        try:
            # Create market data node
            market_node = self.graph.create_node('frequi.nodes.MarketDataNode.MarketDataNode')
            market_node.set_pos(100, 100)
            market_node.set_parameter('pair', 'BTC/USDT')
            market_node.set_parameter('timeframe', '1h')
            
            # Create EMA fast indicator
            ema_fast = self.graph.create_node('frequi.nodes.IndicatorNode.IndicatorNode') 
            ema_fast.set_pos(300, 50)
            ema_fast.set_name('EMA Fast')
            ema_fast.set_parameter('indicator_type', 'EMA')
            ema_fast.set_parameter('period', 12)
            
            # Create EMA slow indicator
            ema_slow = self.graph.create_node('frequi.nodes.IndicatorNode.IndicatorNode')
            ema_slow.set_pos(300, 150)
            ema_slow.set_name('EMA Slow')
            ema_slow.set_parameter('indicator_type', 'EMA')
            ema_slow.set_parameter('period', 26)
            
            # Create crossover logic
            crossover = self.graph.create_node('frequi.nodes.MathNode.MathNode')
            crossover.set_pos(500, 100)
            crossover.set_name('Crossover')
            crossover.set_parameter('operation', 'subtract')
            
            # Create entry signal
            entry = self.graph.create_node('frequi.nodes.EnterNode.EnterNode')
            entry.set_pos(700, 50)
            entry.set_name('Long Entry')
            
            # Create exit signal
            exit_node = self.graph.create_node('frequi.nodes.ExitNode.ExitNode')
            exit_node.set_pos(700, 150)
            exit_node.set_name('Long Exit')
            
            # Connect nodes (EMA indicators to market data)
            try:
                market_candles = market_node.get_output('candles')
                ema_fast_candles = ema_fast.get_input('candles')
                ema_slow_candles = ema_slow.get_input('candles')
                
                if market_candles and ema_fast_candles:
                    market_candles.connect_to(ema_fast_candles)
                if market_candles and ema_slow_candles:
                    market_candles.connect_to(ema_slow_candles)
                    
                # Connect EMA outputs to crossover inputs
                ema_fast_output = ema_fast.get_output('values')
                ema_slow_output = ema_slow.get_output('values')
                crossover_a = crossover.get_input('A')
                crossover_b = crossover.get_input('B')
                
                if ema_fast_output and crossover_a:
                    ema_fast_output.connect_to(crossover_a)
                if ema_slow_output and crossover_b:
                    ema_slow_output.connect_to(crossover_b)
                    
                # Connect crossover to entry/exit signals
                crossover_output = crossover.get_output('result')
                entry_input = entry.get_input('signal')
                exit_input = exit_node.get_input('signal')
                
                if crossover_output and entry_input:
                    crossover_output.connect_to(entry_input)
                if crossover_output and exit_input:
                    crossover_output.connect_to(exit_input)
                    
            except Exception as e:
                print(f"Warning: Could not connect nodes automatically: {e}")
            
            # Show success message
            self.statusBar().showMessage("Created simple EMA crossover strategy - ready to backtest!", 5000)
            
        except Exception as e:
            print(f"Failed to create simple test strategy: {e}")
            self.statusBar().showMessage("Welcome to RDP! Create nodes by clicking the palette on the left.", 3000)
    
    def load_example_strategy(self, filename):
        """Load an example strategy by filename"""
        try:
            from pathlib import Path
            
            example_file = Path(__file__).parent.parent / "user_data" / "strategies" / filename
            
            if example_file.exists():
                if self.check_unsaved_changes():
                    self.graph.clear_session()
                    self.graph.import_session(str(example_file))
                    self.current_file = str(example_file)
                    strategy_name = filename.replace('_', ' ').replace('.json', '').title()
                    self.setWindowTitle(f"RDP for Freqtrade v0.2 - {strategy_name}")
                    self.statusBar().showMessage(f"Loaded {strategy_name} - ready to backtest!", 3000)
            else:
                QMessageBox.warning(self, "Example Not Found", f"Example strategy '{filename}' not found.")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load example strategy: {str(e)}")
    
    def load_demo_strategy(self):
        """Load and display demo strategy in the graph"""
        try:
            demo_file = Path("user_data/strategies/ema_rsi_demo.json")
            if not demo_file.exists():
                # Create demo strategy if it doesn't exist
                from demo_strategy_builder import save_demo_strategy
                save_demo_strategy()
            
            self.load_strategy_from_file(demo_file)
            self.statusBar().showMessage("Demo strategy loaded successfully", 3000)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load demo strategy: {str(e)}")
    
    def load_strategy_from_file(self, file_path):
        """Load strategy from JSON file and create nodes in graph"""
        import json
        
        with open(file_path, 'r') as f:
            strategy_data = json.load(f)
        
        # Clear existing graph
        self.graph.clear_session()
        
        # Create nodes
        node_objects = {}
        for node_data in strategy_data.get('nodes', []):
            node_type = node_data['type']
            node_id = node_data['id']
            position = node_data.get('position', [0, 0])
            parameters = node_data.get('parameters', {})
            
            if node_type in NODE_CLASSES:
                node_class = NODE_CLASSES[node_type]
                # Create node using the registered class
                node = self.graph.create_node(node_class.__identifier__, node_class.NODE_NAME)
                
                # Set position
                node.set_pos(position[0], position[1])
                
                # Set parameters
                if hasattr(node, 'set_parameters'):
                    node.set_parameters(parameters)
                
                node_objects[node_id] = node
        
        # Create connections (simplified for now)
        for connection in strategy_data.get('connections', []):
            # For now, just log the connections - full implementation would require
            # parsing the connection format and creating actual node connections
            print(f"Connection: {connection['from']} -> {connection['to']}")
        
        self.current_file = file_path