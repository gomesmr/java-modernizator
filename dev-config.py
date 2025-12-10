# dev-config.py
"""
Development configuration for quick testing
"""

# Execution IDs for testing
EXECUTION_IDS = {
    'latest': '01KC3WJQRRMWVNDMH9W0S89JWW',
    'previous': '01KC3V5RVXGKA473N9QYQDD5SK',
    # Adicione mais IDs conforme necessário
}

# Development settings
DEV_SETTINGS = {
    'skip_to_step_4': True,
    'use_execution_id': EXECUTION_IDS['latest'],
    'save_pretty_json': True,
    'verbose_output': True
}

def get_dev_execution_id(key='latest'):
    """Get execution ID for development"""
    return EXECUTION_IDS.get(key, EXECUTION_IDS['latest'])