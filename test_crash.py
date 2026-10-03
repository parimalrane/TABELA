import sys
from runners.main import main
try:
    main()
except Exception as e:
    import traceback
    with open('error_log.txt', 'w') as f:
        traceback.print_exc(file=f)
