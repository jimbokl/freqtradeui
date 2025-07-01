"""
Strategy exporter - converts node graph to Freqtrade IStrategy Python code
"""

import json
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, Template
from typing import Dict, List, Any, Optional
from collections import defaultdict, deque

from nodes.base_nodes import NODE_CLASSES


class StrategyExporter:
    """Exports node graphs to Freqtrade IStrategy Python code"""
    
    def __init__(self):
        self.template_dir = Path(__file__).parent / 'templates'
        self.env = Environment(loader=FileSystemLoader(str(self.template_dir)))
    
    def export_graph(self, graph) -> str:
        """Export node graph to Python strategy code"""
        
        # Get all nodes and connections
        nodes = graph.all_nodes()
        if not nodes:
            raise ValueError("Graph is empty - add some nodes first")
        
        # Analyze graph structure
        graph_data = self._analyze_graph(nodes)
        
        # Validate graph
        self._validate_graph(graph_data)
        
        # Generate code sections
        code_sections = self._generate_code_sections(graph_data)
        
        # Extract timeframe from market data nodes
        timeframe = '1h'  # default
        if graph_data['market_data_nodes']:
            first_market_node = graph_data['market_data_nodes'][0]
            timeframe = first_market_node['parameters'].get('timeframe', '1h')
        
        # Load and render template
        template = self._get_strategy_template()
        
        strategy_code = template.render(
            strategy_name="GeneratedStrategy",
            timeframe=timeframe,
            indicators=code_sections['indicators'],
            entry_signals=code_sections['entry_signals'],
            exit_signals=code_sections['exit_signals'],
            hyperopt_params=code_sections['hyperopt_params'],
            plots=code_sections['plots'],
            imports=code_sections['imports']
        )
        
        return strategy_code
    
    def _analyze_graph(self, nodes) -> Dict[str, Any]:
        """Analyze graph structure and connections"""
        
        graph_data = {
            'nodes': {},
            'connections': defaultdict(list),
            'execution_order': [],
            'market_data_nodes': [],
            'indicator_nodes': [],
            'math_nodes': [],
            'logic_nodes': [],
            'enter_nodes': [],
            'exit_nodes': [],
            'hyperopt_nodes': [],
            'plot_nodes': []
        }
        
        # Process all nodes
        for node in nodes:
            node_type = node.type_
            node_id = node.id
            node_name = node.name()
            
            # Get node parameters
            if hasattr(node, 'get_parameters'):
                parameters = node.get_parameters()
            else:
                parameters = {}
            
            node_data = {
                'id': node_id,
                'type': node_type,
                'name': node_name,
                'parameters': parameters,
                'inputs': {},
                'outputs': {}
            }
            
            # Process input ports
            for input_port in node.input_ports():
                port_name = input_port.name()
                connected_outputs = []
                
                for connection in input_port.connected_ports():
                    connected_outputs.append({
                        'node_id': connection.node().id,
                        'port_name': connection.name()
                    })
                
                node_data['inputs'][port_name] = connected_outputs
            
            # Process output ports
            for output_port in node.output_ports():
                port_name = output_port.name()
                connected_inputs = []
                
                for connection in output_port.connected_ports():
                    connected_inputs.append({
                        'node_id': connection.node().id,
                        'port_name': connection.name()
                    })
                
                node_data['outputs'][port_name] = connected_inputs
            
            graph_data['nodes'][node_id] = node_data
            
            # Categorize nodes by type
            if 'MarketData' in node_type:
                graph_data['market_data_nodes'].append(node_data)
            elif 'Indicator' in node_type:
                graph_data['indicator_nodes'].append(node_data)
            elif 'Math' in node_type:
                graph_data['math_nodes'].append(node_data)
            elif 'Logic' in node_type:
                graph_data['logic_nodes'].append(node_data)
            elif 'Enter' in node_type:
                graph_data['enter_nodes'].append(node_data)
            elif 'Exit' in node_type:
                graph_data['exit_nodes'].append(node_data)
            elif 'Hyperopt' in node_type:
                graph_data['hyperopt_nodes'].append(node_data)
            elif 'Plot' in node_type:
                graph_data['plot_nodes'].append(node_data)
        
        # Perform topological sort for execution order
        graph_data['execution_order'] = self._topological_sort(graph_data['nodes'])
        
        return graph_data
    
    def _topological_sort(self, nodes: Dict) -> List[str]:
        """Perform topological sort to determine execution order"""
        
        # Build adjacency list
        graph = defaultdict(list)
        in_degree = defaultdict(int)
        
        # Initialize in-degree
        for node_id in nodes:
            in_degree[node_id] = 0
        
        # Build graph and calculate in-degrees
        for node_id, node_data in nodes.items():
            for input_name, connections in node_data['inputs'].items():
                for connection in connections:
                    source_node = connection['node_id']
                    graph[source_node].append(node_id)
                    in_degree[node_id] += 1
        
        # Kahn's algorithm
        queue = deque([node_id for node_id in nodes if in_degree[node_id] == 0])
        result = []
        
        while queue:
            current = queue.popleft()
            result.append(current)
            
            for neighbor in graph[current]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        
        # Check for cycles
        if len(result) != len(nodes):
            raise ValueError("Graph contains cycles - please check your connections")
        
        return result
    
    def _validate_graph(self, graph_data: Dict[str, Any]):
        """Validate graph structure"""
        
        # Check for at least one market data node
        if not graph_data['market_data_nodes']:
            raise ValueError("Strategy must have at least one Market Data node")
        
        # Check for at least one entry signal
        if not graph_data['enter_nodes']:
            raise ValueError("Strategy must have at least one Entry Signal node")
        
        # Check for at least one exit signal
        if not graph_data['exit_nodes']:
            raise ValueError("Strategy must have at least one Exit Signal node")
        
        # Validate connections (более мягкая валидация)
        for node_id, node_data in graph_data['nodes'].items():
            # Проверяем только критически важные подключения
            # Индикаторы могут работать с dataframe напрямую
            if 'Enter' in node_data['type'] or 'Exit' in node_data['type']:
                # Entry/Exit узлы должны иметь сигнал, но мы можем создать его автоматически
                signal_inputs = node_data['inputs'].get('signal', [])
                if not signal_inputs:
                    print(f"Warning: {node_data['name']} has no signal input - will generate default condition")
        
        print(f"Graph validation completed - {len(graph_data['nodes'])} nodes validated")
    
    def _get_required_inputs(self, node_type: str) -> List[str]:
        """Get required inputs for a node type"""
        
        required_inputs = {
            'IndicatorNode': ['candles'],
            'MathNode': ['A'],  # B is optional (can use constant)
            'LogicNode': ['condition1'],  # condition2 is optional
            'EnterSignalNode': ['signal'],
            'ExitSignalNode': ['signal'],
            'PlotNode': ['data']
        }
        
        return required_inputs.get(node_type, [])
    
    def _generate_code_sections(self, graph_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate code sections for different parts of the strategy"""
        
        sections = {
            'imports': self._generate_imports(graph_data),
            'hyperopt_params': self._generate_hyperopt_params(graph_data),
            'indicators': self._generate_indicators(graph_data),
            'entry_signals': self._generate_entry_signals(graph_data),
            'exit_signals': self._generate_exit_signals(graph_data),
            'plots': self._generate_plots(graph_data)
        }
        
        return sections
    
    def _generate_imports(self, graph_data: Dict[str, Any]) -> List[str]:
        """Generate required imports based on nodes used"""
        
        imports = [
            "import pandas as pd",
            "import numpy as np",
            "from freqtrade.strategy import IStrategy, merge_informative_pair",
            "from pandas import DataFrame",
            "import talib.abstract as ta",
            "import freqtrade.vendor.qtpylib.indicators as qtpylib"
        ]
        
        # Add hyperopt imports if needed
        if graph_data['hyperopt_nodes']:
            imports.extend([
                "from freqtrade.optimize.space import Categorical, Dimension, Integer, SKDecimal",
                "from functools import reduce"
            ])
        
        return imports
    
    def _generate_hyperopt_params(self, graph_data: Dict[str, Any]) -> List[str]:
        """Generate hyperopt parameter definitions"""
        
        params = []
        
        for node in graph_data['hyperopt_nodes']:
            param_name = node['parameters'].get('param_name', 'param')
            param_type = node['parameters'].get('param_type', 'Integer')
            min_val = node['parameters'].get('min_value', 0)
            max_val = node['parameters'].get('max_value', 100)
            choices = node['parameters'].get('choices', [])
            
            if param_type == 'Integer':
                params.append(f"    {param_name} = Integer({min_val}, {max_val}, default={(min_val + max_val) // 2}, space='buy')")
            elif param_type == 'Real':
                params.append(f"    {param_name} = SKDecimal({min_val}, {max_val}, default={(min_val + max_val) / 2}, space='buy')")
            elif param_type == 'Categorical' and choices:
                params.append(f"    {param_name} = Categorical({choices}, default='{choices[0]}', space='buy')")
        
        return params
    
    def _generate_indicators(self, graph_data: Dict[str, Any]) -> List[str]:
        """Generate indicator calculations"""
        
        indicators = []
        
        # Process nodes in execution order
        for node_id in graph_data['execution_order']:
            node = graph_data['nodes'][node_id]
            
            if 'Indicator' in node['type']:
                indicator_code = self._generate_indicator_code(node, graph_data)
                if indicator_code:
                    indicators.append(indicator_code)
            elif 'Math' in node['type']:
                math_code = self._generate_math_code(node, graph_data)
                if math_code:
                    indicators.append(math_code)
            elif 'Logic' in node['type']:
                logic_code = self._generate_logic_code(node, graph_data)
                if logic_code:
                    indicators.append(logic_code)
        
        return indicators
    
    def _generate_indicator_code(self, node: Dict, graph_data: Dict) -> str:
        """Generate code for indicator node"""
        
        indicator_type = node['parameters'].get('indicator_type', 'EMA')
        period = node['parameters'].get('period', 14)
        source = node['parameters'].get('source', 'close')
        
        var_name = f"indicator_{node['id'].replace('-', '_')}"
        
        if indicator_type == 'EMA':
            return f"        dataframe['{var_name}'] = ta.EMA(dataframe['{source}'], timeperiod={period})"
        elif indicator_type == 'SMA':
            return f"        dataframe['{var_name}'] = ta.SMA(dataframe['{source}'], timeperiod={period})"
        elif indicator_type == 'RSI':
            return f"        dataframe['{var_name}'] = ta.RSI(dataframe['{source}'], timeperiod={period})"
        elif indicator_type == 'MACD':
            return f"        macd = ta.MACD(dataframe['{source}'])\n        dataframe['{var_name}'] = macd['macd']"
        elif indicator_type == 'Bollinger Bands':
            return f"        bollinger = qtpylib.bollinger_bands(dataframe['{source}'], window={period})\n        dataframe['{var_name}_upper'] = bollinger['upper']\n        dataframe['{var_name}_middle'] = bollinger['mid']\n        dataframe['{var_name}_lower'] = bollinger['lower']"
        else:
            return f"        # TODO: Implement {indicator_type} indicator"
    
    def _generate_math_code(self, node: Dict, graph_data: Dict) -> str:
        """Generate code for math node"""
        
        operation = node['parameters'].get('operation', 'add')
        constant = node['parameters'].get('constant', 0.0)
        
        var_name = f"math_{node['id'].replace('-', '_')}"
        
        # Get input variable names
        input_a = self._get_input_variable(node, 'A', graph_data)
        input_b = self._get_input_variable(node, 'B', graph_data)
        
        if not input_b:
            input_b = str(constant)
        
        operations_map = {
            'add': '+',
            'subtract': '-',
            'multiply': '*',
            'divide': '/',
            'power': '**'
        }
        
        op_symbol = operations_map.get(operation, '+')
        
        if operation in ['max', 'min']:
            return f"        dataframe['{var_name}'] = np.{operation}(dataframe['{input_a}'], dataframe['{input_b}'])"
        else:
            return f"        dataframe['{var_name}'] = dataframe['{input_a}'] {op_symbol} dataframe['{input_b}']"
    
    def _generate_logic_code(self, node: Dict, graph_data: Dict) -> str:
        """Generate code for logic node"""
        
        operation = node['parameters'].get('operation', 'AND')
        var_name = f"logic_{node['id'].replace('-', '_')}"
        
        # Get input variable names
        cond1 = self._get_input_variable(node, 'condition1', graph_data)
        cond2 = self._get_input_variable(node, 'condition2', graph_data)
        
        if operation == 'AND' and cond1 and cond2:
            return f"        dataframe['{var_name}'] = (dataframe['{cond1}']) & (dataframe['{cond2}'])"
        elif operation == 'OR' and cond1 and cond2:
            return f"        dataframe['{var_name}'] = (dataframe['{cond1}']) | (dataframe['{cond2}'])"
        elif operation == 'NOT' and cond1:
            return f"        dataframe['{var_name}'] = ~(dataframe['{cond1}'])"
        else:
            return f"        # TODO: Implement {operation} logic operation"
    
    def _generate_entry_signals(self, graph_data: Dict[str, Any]) -> List[str]:
        """Generate entry signal code"""
        
        signals = []
        
        for node in graph_data['enter_nodes']:
            side = node['parameters'].get('side', 'long')
            signal_var = self._get_input_variable(node, 'signal', graph_data)
            
            if signal_var:
                # Generate proper boolean condition
                if side in ['long', 'both']:
                    signals.append(f"        dataframe.loc[(dataframe['{signal_var}'] > 0), 'enter_long'] = 1")
                if side in ['short', 'both']:
                    signals.append(f"        dataframe.loc[(dataframe['{signal_var}'] < 0), 'enter_short'] = 1")
            else:
                # Fallback: create simple entry condition
                if side in ['long', 'both']:
                    signals.append("        # TODO: Define entry condition for long trades")
                if side in ['short', 'both']:
                    signals.append("        # TODO: Define entry condition for short trades")
        
        return signals
    
    def _generate_exit_signals(self, graph_data: Dict[str, Any]) -> List[str]:
        """Generate exit signal code"""
        
        signals = []
        
        for node in graph_data['exit_nodes']:
            side = node['parameters'].get('side', 'long')
            signal_var = self._get_input_variable(node, 'signal', graph_data)
            
            if signal_var:
                # Generate proper boolean condition
                if side in ['long', 'both']:
                    signals.append(f"        dataframe.loc[(dataframe['{signal_var}'] < 0), 'exit_long'] = 1")
                if side in ['short', 'both']:
                    signals.append(f"        dataframe.loc[(dataframe['{signal_var}'] > 0), 'exit_short'] = 1")
            else:
                # Fallback: create simple exit condition
                if side in ['long', 'both']:
                    signals.append("        # TODO: Define exit condition for long trades")
                if side in ['short', 'both']:
                    signals.append("        # TODO: Define exit condition for short trades")
        
        return signals
    
    def _generate_plots(self, graph_data: Dict[str, Any]) -> List[str]:
        """Generate plot configurations"""
        
        plots = []
        
        for node in graph_data['plot_nodes']:
            label = node['parameters'].get('label', 'Plot')
            color = node['parameters'].get('color', 'blue')
            plot_type = node['parameters'].get('plot_type', 'line')
            subplot = node['parameters'].get('subplot', False)
            
            data_var = self._get_input_variable(node, 'data', graph_data)
            
            if data_var:
                plot_config = f"            '{label}': {{'color': '{color}', 'type': '{plot_type}'}}"
                if subplot:
                    plot_config += f", 'subplot': True"
                plots.append(plot_config)
        
        return plots
    
    def _get_input_variable(self, node: Dict, input_name: str, graph_data: Dict) -> Optional[str]:
        """Get the variable name for a node's input"""
        
        if input_name not in node['inputs'] or not node['inputs'][input_name]:
            return None
        
        # Get the first connected input (assuming single connections for now)
        connection = node['inputs'][input_name][0]
        source_node_id = connection['node_id']
        source_node = graph_data['nodes'][source_node_id]
        
        # Generate variable name based on source node type
        if 'Indicator' in source_node['type']:
            return f"indicator_{source_node_id.replace('-', '_')}"
        elif 'Math' in source_node['type']:
            return f"math_{source_node_id.replace('-', '_')}"
        elif 'Logic' in source_node['type']:
            return f"logic_{source_node_id.replace('-', '_')}"
        elif 'MarketData' in source_node['type']:
            source = source_node['parameters'].get('source', 'close')
            return source
        else:
            return f"var_{source_node_id.replace('-', '_')}"
    
    def _get_strategy_template(self) -> Template:
        """Get the Jinja2 template for strategy generation"""
        
        # Template content (inline for now, will move to file later)
        template_content = '''
# Generated strategy from RDP visual builder
# PRAGMA pylint: disable=missing-docstring, invalid-name, pointless-string-statement

{% for import_line in imports %}
{{ import_line }}
{% endfor %}

class {{ strategy_name }}(IStrategy):
    """
    Generated strategy class
    """
    
    # Strategy interface version
    INTERFACE_VERSION = 3
    
    # Minimal ROI designed for the strategy
    minimal_roi = {
        "60": 0.01,
        "30": 0.02,
        "0": 0.04
    }
    
    # Optimal stoploss
    stoploss = -0.10
    
    # Optimal timeframe for the strategy
    timeframe = '{{ timeframe }}'
    
    # Can this strategy go short?
    can_short: bool = False
    
    # These values can be overridden in the config
    use_exit_signal = True
    exit_profit_only = False
    ignore_roi_if_entry_signal = False
    
    # Number of candles the strategy requires before producing valid signals
    startup_candle_count: int = 30
    
{% if hyperopt_params %}
    # Hyperopt parameters
{% for param in hyperopt_params %}
{{ param }}
{% endfor %}
{% endif %}
    
    def __init__(self, config: dict = None):
        """Инициализация стратегии с конфигурацией"""
        if config is None:
            config = {}
        super().__init__(config)

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Adds several different TA indicators to the given DataFrame
        """
{% for indicator in indicators %}
{{ indicator }}
{% endfor %}
        
        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Based on TA indicators, populates the entry signal for the given dataframe
        """
        # Initialize entry columns
        dataframe['enter_long'] = 0
        dataframe['enter_short'] = 0
        
{% for signal in entry_signals %}
{{ signal }}
{% endfor %}
        
        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Based on TA indicators, populates the exit signal for the given dataframe
        """
        # Initialize exit columns
        dataframe['exit_long'] = 0
        dataframe['exit_short'] = 0
        
{% for signal in exit_signals %}
{{ signal }}
{% endfor %}
        
        return dataframe

{% if plots %}
    def plot_config(self):
        """
        Plot configuration for freqtrade-plot
        """
        return {
            'main_plot': {
{% for plot in plots %}
{{ plot }}{% if not loop.last %},{% endif %}
{% endfor %}
            },
            'subplots': {}
        }
{% endif %}
'''
        
        return Template(template_content)
