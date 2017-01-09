import os
from bitsbox import create_app

app = create_app(os.environ['BITSBOX_CONFIG'])
