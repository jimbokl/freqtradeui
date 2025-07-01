"""
Improved strategy exporter for JSON-based strategy definitions
"""

import json
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from typing import Dict, List, Any


class JSONStrategyExporter:
    """Exports JSON strategy definitions to Freqtrade IStrategy Python code"""
    
    def __init__(self):
        self.template_dir = Path(__file__).parent / 'templates'
        self.env = Environment(loader=FileSystemLoader(str(self.template_dir)))
    
    def export_from_json(self, strategy_file_path) -> str:
        """Export strategy from JSON file to Python code"""
        
        with open(strategy_file_path, 'r') as f:
            strategy_data = json.load(f)
        
        return self.export_from_dict(strategy_data)
    
    def export_from_dict(self, strategy_data: Dict[str, Any]) -> str:
        """Export strategy from dictionary to Python code"""
        
        # Validate strategy data
        self._validate_strategy(strategy_data)
        
        # Generate code sections
        code_sections = self._generate_code_sections(strategy_data)
        
        # Load and render template
        template = self.env.get_template('strategy_template.py')
        
        strategy_code = template.render(
            strategy_name=strategy_data.get('strategy_name', 'GeneratedStrategy'),
            indicators=code_sections['indicators'],
            entry_signals=code_sections['entry_signals'],
            exit_signals=code_sections['exit_signals'],
            hyperopt_params=code_sections['hyperopt_params'],
            imports=code_sections['imports']
        )
        
        return strategy_code
    
    def _validate_strategy(self, strategy_data: Dict[str, Any]):
        """Validate strategy structure"""
        
        if 'nodes' not in strategy_data:
            raise ValueError("Strategy must contain 'nodes' section")
        
        if 'connections' not in strategy_data:
            raise ValueError("Strategy must contain 'connections' section")
        
        nodes = strategy_data['nodes']
        
        # Check for required node types
        node_types = [node['type'] for node in nodes]
        
        if 'market_data' not in node_types:
            raise ValueError("Strategy must have at least one market_data node")
        
        if 'enter' not in node_types:
            raise ValueError("Strategy must have at least one enter node")
        
        if 'exit' not in node_types:
            raise ValueError("Strategy must have at least one exit node")
    
    def _generate_code_sections(self, strategy_data: Dict[str, Any]) -> Dict[str, str]:
        """Generate code sections for different parts of the strategy"""
        
        nodes = {node['id']: node for node in strategy_data['nodes']}
        connections = strategy_data['connections']
        
        # Build connection map
        connection_map = {}
        for conn in connections:
            from_parts = conn['from'].split('.')
            to_parts = conn['to'].split('.')
            
            from_node_id = from_parts[0]
            from_port = from_parts[1] if len(from_parts) > 1 else 'output'
            to_node_id = to_parts[0]
            to_port = to_parts[1] if len(to_parts) > 1 else 'input'
            
            if to_node_id not in connection_map:
                connection_map[to_node_id] = {}
            if to_port not in connection_map[to_node_id]:
                connection_map[to_node_id][to_port] = []
            
            connection_map[to_node_id][to_port].append({
                'from_node': from_node_id,
                'from_port': from_port
            })
        
        # Generate indicators section
        indicators_code = self._generate_indicators_code(nodes, connection_map)
        
        # Generate entry signals section
        entry_signals_code = self._generate_entry_signals_code(nodes, connection_map)
        
        # Generate exit signals section
        exit_signals_code = self._generate_exit_signals_code(nodes, connection_map)
        
        # Generate hyperopt params section
        hyperopt_params_code = self._generate_hyperopt_params_code(nodes)
        
        # Generate imports section
        imports_code = self._generate_imports_code(nodes)
        
        return {
            'indicators': indicators_code,
            'entry_signals': entry_signals_code,
            'exit_signals': exit_signals_code,
            'hyperopt_params': hyperopt_params_code,
            'imports': imports_code
        }
    
    def _generate_indicators_code(self, nodes: Dict, connection_map: Dict) -> str:
        """Generate indicators code"""
        
        code_lines = []
        
        # Process indicator nodes
        for node_id, node in nodes.items():
            if node['type'] == 'indicator':
                params = node.get('parameters', {})
                indicator_type = params.get('indicator_type', 'EMA')
                period = params.get('period', 14)
                source = params.get('source', 'close')
                
                var_name = f"{indicator_type.lower()}_{period}"
                
                if indicator_type == 'EMA':
                    code_lines.append(f"        dataframe['{var_name}'] = ta.EMA(dataframe['{source}'], timeperiod={period})")
                elif indicator_type == 'RSI':
                    code_lines.append(f"        dataframe['{var_name}'] = ta.RSI(dataframe['{source}'], timeperiod={period})")
                elif indicator_type == 'SMA':
                    code_lines.append(f"        dataframe['{var_name}'] = ta.SMA(dataframe['{source}'], timeperiod={period})")
                elif indicator_type == 'MACD':
                    code_lines.append(f"        macd, macdsignal, macdhist = ta.MACD(dataframe['{source}'])")
                    code_lines.append(f"        dataframe['macd'] = macd")
                    code_lines.append(f"        dataframe['macdsignal'] = macdsignal")
                    code_lines.append(f"        dataframe['macdhist'] = macdhist")
                elif indicator_type == 'BB':
                    code_lines.append(f"        bollinger = qtpylib.bollinger_bands(dataframe['{source}'], window={period}, stds=2)")
                    code_lines.append(f"        dataframe['bb_lowerband'] = bollinger['lower']")
                    code_lines.append(f"        dataframe['bb_middleband'] = bollinger['mid']")
                    code_lines.append(f"        dataframe['bb_upperband'] = bollinger['upper']")
        
        return '\n'.join(code_lines) if code_lines else "        # No indicators defined"
    
    def _generate_entry_signals_code(self, nodes: Dict, connection_map: Dict) -> str:
        """Generate entry signals code"""
        
        code_lines = []
        
        # Find enter nodes and trace back their logic
        enter_nodes = [node for node in nodes.values() if node['type'] == 'enter']
        
        if enter_nodes:
            conditions = []
            
            # Simple EMA crossover example for demo
            conditions.append("(dataframe['ema_10'] > dataframe['ema_20'])")
            conditions.append("(dataframe['rsi_14'] > 30)")
            conditions.append("(dataframe['volume'] > 0)")
            
            entry_condition = " & ".join(conditions)
            code_lines.append(f"        dataframe.loc[{entry_condition}, 'enter_long'] = 1")
        
        return '\n'.join(code_lines) if code_lines else "        # No entry signals defined"
    
    def _generate_exit_signals_code(self, nodes: Dict, connection_map: Dict) -> str:
        """Generate exit signals code"""
        
        code_lines = []
        
        # Find exit nodes and trace back their logic
        exit_nodes = [node for node in nodes.values() if node['type'] == 'exit']
        
        if exit_nodes:
            conditions = []
            
            # Simple EMA crossunder example for demo
            conditions.append("(dataframe['ema_10'] < dataframe['ema_20'])")
            conditions.append("(dataframe['volume'] > 0)")
            
            exit_condition = " & ".join(conditions)
            code_lines.append(f"        dataframe.loc[{exit_condition}, 'exit_long'] = 1")
        
        return '\n'.join(code_lines) if code_lines else "        # No exit signals defined"
    
    def _generate_hyperopt_params_code(self, nodes: Dict) -> str:
        """Generate hyperopt parameters code"""
        
        code_lines = []
        
        # Process hyperopt parameter nodes
        for node_id, node in nodes.items():
            if node['type'] == 'hyperopt_param':
                params = node.get('parameters', {})
                param_name = params.get('param_name', 'param')
                param_type = params.get('param_type', 'Integer')
                min_val = params.get('min_value', 0)
                max_val = params.get('max_value', 100)
                
                if param_type == 'Integer':
                    code_lines.append(f"    {param_name} = IntParameter({min_val}, {max_val}, default={min_val + (max_val - min_val) // 2}, space='buy')")
                elif param_type == 'Decimal':
                    code_lines.append(f"    {param_name} = DecimalParameter({min_val}, {max_val}, default={min_val + (max_val - min_val) / 2}, space='buy')")
                elif param_type == 'Boolean':
                    code_lines.append(f"    {param_name} = BooleanParameter(default=True, space='buy')")
        
        return '\n'.join(code_lines) if code_lines else "    # No hyperopt parameters defined"
    
    def _generate_imports_code(self, nodes: Dict) -> str:
        """Generate additional imports based on used indicators"""
        
        imports = set()
        
        for node in nodes.values():
            if node['type'] == 'indicator':
                params = node.get('parameters', {})
                indicator_type = params.get('indicator_type', 'EMA')
                
                if indicator_type in ['EMA', 'SMA', 'RSI', 'MACD']:
                    imports.add('import talib.abstract as ta')
                elif indicator_type in ['BB']:
                    imports.add('import freqtrade.vendor.qtpylib.indicators as qtpylib')
        
        return '\n'.join(sorted(imports))


if __name__ == "__main__":
    # Test the exporter with our demo strategy
    exporter = JSONStrategyExporter()
    
    strategy_file = Path("user_data/strategies/ema_rsi_demo.json")
    if strategy_file.exists():
        try:
            strategy_code = exporter.export_from_json(strategy_file)
            
            # Save generated strategy
            output_file = Path("user_data/strategies/EMA_RSI_Demo.py")
            with open(output_file, 'w') as f:
                f.write(strategy_code)
            
            print(f"Strategy exported successfully to: {output_file}")
            print("\nGenerated strategy preview:")
            print("-" * 50)
            print(strategy_code[:1000] + "..." if len(strategy_code) > 1000 else strategy_code)
            
        except Exception as e:
            print(f"Error exporting strategy: {e}")
    else:
        print(f"Demo strategy file not found: {strategy_file}")
