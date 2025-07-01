"""
Results panel for displaying backtest results, equity curves, and logs
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTabWidget, QTextEdit,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QHBoxLayout, QLabel, QPushButton, QSplitter
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import pandas as pd


class EquityChartWidget(QWidget):
    """Widget for displaying equity curve chart"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the chart UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        
        # Create matplotlib figure and canvas
        self.figure = Figure(figsize=(12, 6), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)
        
        # Control buttons
        controls_layout = QHBoxLayout()
        
        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self.refresh_chart)
        controls_layout.addWidget(self.refresh_btn)
        
        controls_layout.addStretch()
        
        # Stats labels
        self.total_return_label = QLabel("Total Return: --")
        self.sharpe_label = QLabel("Sharpe: --")
        self.max_dd_label = QLabel("Max DD: --")
        
        controls_layout.addWidget(self.total_return_label)
        controls_layout.addWidget(self.sharpe_label)
        controls_layout.addWidget(self.max_dd_label)
        
        layout.addLayout(controls_layout)
        
        # Initial empty chart
        self.plot_empty_chart()
    
    def plot_empty_chart(self):
        """Plot empty chart with placeholder"""
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.text(0.5, 0.5, 'No backtest data available\nRun a backtest to see results', 
                horizontalalignment='center', verticalalignment='center',
                transform=ax.transAxes, fontsize=12, color='gray')
        ax.set_title('Equity Curve')
        ax.set_xlabel('Date')
        ax.set_ylabel('Portfolio Value')
        self.canvas.draw()
    
    def plot_equity_curve(self, equity_data):
        """Plot equity curve from backtest results"""
        if equity_data is None or equity_data.empty:
            self.plot_empty_chart()
            return
        
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        # Plot equity curve
        equity_data.plot(x='date', y='equity', ax=ax, label='Portfolio Value')
        
        # Add drawdown as filled area
        if 'drawdown' in equity_data.columns:
            ax2 = ax.twinx()
            ax2.fill_between(equity_data['date'], equity_data['drawdown'], 0, 
                           alpha=0.3, color='red', label='Drawdown')
            ax2.set_ylabel('Drawdown %')
            ax2.legend(loc='upper right')
        
        ax.set_title('Equity Curve')
        ax.set_xlabel('Date')
        ax.set_ylabel('Portfolio Value')
        ax.legend(loc='upper left')
        ax.grid(True, alpha=0.3)
        
        # Rotate x-axis labels for better readability
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
        
        self.figure.tight_layout()
        self.canvas.draw()
    
    def update_stats(self, stats):
        """Update performance statistics labels"""
        if stats:
            self.total_return_label.setText(f"Total Return: {stats.get('total_return', '--')}")
            self.sharpe_label.setText(f"Sharpe: {stats.get('sharpe', '--')}")
            self.max_dd_label.setText(f"Max DD: {stats.get('max_drawdown', '--')}")
        else:
            self.total_return_label.setText("Total Return: --")
            self.sharpe_label.setText("Sharpe: --")
            self.max_dd_label.setText("Max DD: --")
    
    def refresh_chart(self):
        """Refresh the chart (placeholder for now)"""
        # TODO: Implement chart refresh logic
        pass


class TradesTableWidget(QWidget):
    """Widget for displaying trades table"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the trades table UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        
        # Controls
        controls_layout = QHBoxLayout()
        
        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self.refresh_table)
        controls_layout.addWidget(self.refresh_btn)
        
        controls_layout.addStretch()
        
        # Summary stats
        self.total_trades_label = QLabel("Total Trades: --")
        self.profitable_label = QLabel("Profitable: --")
        self.avg_profit_label = QLabel("Avg Profit: --")
        
        controls_layout.addWidget(self.total_trades_label)
        controls_layout.addWidget(self.profitable_label)
        controls_layout.addWidget(self.avg_profit_label)
        
        layout.addLayout(controls_layout)
        
        # Trades table
        self.table = QTableWidget()
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        
        # Set up columns
        columns = [
            "Entry Date", "Exit Date", "Pair", "Side", "Amount",
            "Entry Price", "Exit Price", "Profit", "Profit %", "Duration"
        ]
        self.table.setColumnCount(len(columns))
        self.table.setHorizontalHeaderLabels(columns)
        
        # Resize columns to content
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        
        layout.addWidget(self.table)
        
        # Show empty message initially
        self.show_empty_message()
    
    def show_empty_message(self):
        """Show message when no trades available"""
        self.table.setRowCount(1)
        self.table.setColumnCount(1)
        self.table.setHorizontalHeaderLabels([""])
        
        item = QTableWidgetItem("No trades data available. Run a backtest to see trade results.")
        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        item.setFlags(Qt.ItemFlag.ItemIsEnabled)  # Make it non-editable
        self.table.setItem(0, 0, item)
        
        # Hide header and stretch to fill
        self.table.horizontalHeader().setVisible(False)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
    
    def populate_trades(self, trades_data):
        """Populate table with trades data"""
        if trades_data is None or trades_data.empty:
            self.show_empty_message()
            return
        
        # Restore proper table structure
        columns = [
            "Entry Date", "Exit Date", "Pair", "Side", "Amount",
            "Entry Price", "Exit Price", "Profit", "Profit %", "Duration"
        ]
        self.table.setColumnCount(len(columns))
        self.table.setHorizontalHeaderLabels(columns)
        self.table.horizontalHeader().setVisible(True)
        
        # Set row count
        self.table.setRowCount(len(trades_data))
        
        # Populate data
        for row, trade in trades_data.iterrows():
            self.table.setItem(row, 0, QTableWidgetItem(str(trade.get('entry_date', ''))))
            self.table.setItem(row, 1, QTableWidgetItem(str(trade.get('exit_date', ''))))
            self.table.setItem(row, 2, QTableWidgetItem(str(trade.get('pair', ''))))
            self.table.setItem(row, 3, QTableWidgetItem(str(trade.get('side', ''))))
            self.table.setItem(row, 4, QTableWidgetItem(str(trade.get('amount', ''))))
            self.table.setItem(row, 5, QTableWidgetItem(str(trade.get('entry_price', ''))))
            self.table.setItem(row, 6, QTableWidgetItem(str(trade.get('exit_price', ''))))
            self.table.setItem(row, 7, QTableWidgetItem(str(trade.get('profit', ''))))
            self.table.setItem(row, 8, QTableWidgetItem(str(trade.get('profit_pct', ''))))
            self.table.setItem(row, 9, QTableWidgetItem(str(trade.get('duration', ''))))
        
        # Resize columns
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
    
    def update_stats(self, stats):
        """Update trade statistics"""
        if stats:
            self.total_trades_label.setText(f"Total Trades: {stats.get('total_trades', '--')}")
            self.profitable_label.setText(f"Profitable: {stats.get('profitable_trades', '--')}")
            self.avg_profit_label.setText(f"Avg Profit: {stats.get('avg_profit', '--')}")
        else:
            self.total_trades_label.setText("Total Trades: --")
            self.profitable_label.setText("Profitable: --")
            self.avg_profit_label.setText("Avg Profit: --")
    
    def refresh_table(self):
        """Refresh the table (placeholder for now)"""
        # TODO: Implement table refresh logic
        pass


class LogsWidget(QWidget):
    """Widget for displaying execution logs"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the logs UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        
        # Controls
        controls_layout = QHBoxLayout()
        
        self.clear_btn = QPushButton("Clear")
        self.clear_btn.clicked.connect(self.clear_logs)
        controls_layout.addWidget(self.clear_btn)
        
        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self.refresh_logs)
        controls_layout.addWidget(self.refresh_btn)
        
        controls_layout.addStretch()
        
        layout.addLayout(controls_layout)
        
        # Logs text area
        self.logs_text = QTextEdit()
        self.logs_text.setReadOnly(True)
        self.logs_text.setFont(QFont("Monaco", 10))  # Monospace font
        self.logs_text.setStyleSheet("""
            QTextEdit {
                background-color: #2b2b2b;
                color: #ffffff;
                border: 1px solid #555;
            }
        """)
        
        layout.addWidget(self.logs_text)
        
        # Initial message
        self.append_log("Ready to run backtest. Select strategy and click 'Backtest' to begin.", "INFO")
    
    def append_log(self, message, level="INFO"):
        """Append a log message"""
        # Color code by level
        colors = {
            "INFO": "#ffffff",
            "WARNING": "#ffaa00", 
            "ERROR": "#ff4444",
            "SUCCESS": "#44ff44",
            "DEBUG": "#888888"
        }
        
        color = colors.get(level, "#ffffff")
        
        # Format message with timestamp
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        formatted_message = f'<span style="color: #888">[{timestamp}]</span> <span style="color: {color}; font-weight: bold">{level}:</span> <span style="color: {color}">{message}</span>'
        
        self.logs_text.append(formatted_message)
        
        # Auto-scroll to bottom
        scrollbar = self.logs_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def clear_logs(self):
        """Clear all logs"""
        self.logs_text.clear()
        self.append_log("Logs cleared.", "INFO")
    
    def refresh_logs(self):
        """Refresh logs (placeholder for now)"""
        # TODO: Implement log refresh from file
        self.append_log("Logs refreshed.", "INFO")


class ResultsPanel(QWidget):
    """Bottom panel with tabs for results, trades, and logs"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the results panel UI"""
        self.setMinimumHeight(200)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        
        # Tab widget
        self.tab_widget = QTabWidget()
        
        # Equity curve tab
        self.equity_widget = EquityChartWidget()
        self.tab_widget.addTab(self.equity_widget, "Equity Curve")
        
        # Trades tab
        self.trades_widget = TradesTableWidget()
        self.tab_widget.addTab(self.trades_widget, "Trades")
        
        # Logs tab
        self.logs_widget = LogsWidget()
        self.tab_widget.addTab(self.logs_widget, "Logs")
        
        layout.addWidget(self.tab_widget)
    
    def update_results(self, results_data):
        """Update all result widgets with new data"""
        if results_data:
            # Update equity curve
            equity_data = results_data.get('equity')
            stats = results_data.get('stats')
            
            self.equity_widget.plot_equity_curve(equity_data)
            self.equity_widget.update_stats(stats)
            
            # Update trades table
            trades_data = results_data.get('trades')
            trade_stats = results_data.get('trade_stats')
            
            self.trades_widget.populate_trades(trades_data)
            self.trades_widget.update_stats(trade_stats)
    
    def display_backtest_results(self, results):
        """Display backtest results - alias for update_results"""
        print(f"📊 Отображаю результаты бэктеста в GUI")
        print(f"📊 Ключи результатов: {list(results.keys()) if results else 'None'}")
        
        if results and results.get('success', False):
            self.log_message("Бэктест успешно завершен!", "SUCCESS")
            
            # Обновляем результаты
            self.update_results(results)
            
            # Переключаемся на вкладку с equity curve
            self.tab_widget.setCurrentIndex(0)
            
            # Логируем статистику
            stats = results.get('stats', {})
            if stats:
                self.log_message(f"Общая доходность: {stats.get('total_return', 'N/A')}", "INFO")
                self.log_message(f"Количество сделок: {stats.get('total_trades', 'N/A')}", "INFO")
                self.log_message(f"Прибыльных сделок: {stats.get('profitable_trades', 'N/A')}", "INFO")
        else:
            error_msg = results.get('error', 'Неизвестная ошибка') if results else 'Нет результатов'
            self.log_message(f"Ошибка бэктеста: {error_msg}", "ERROR")

    def log_message(self, message, level="INFO"):
        """Add a log message"""
        self.logs_widget.append_log(message, level)
