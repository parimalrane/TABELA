import sys
import traceback
try:
    from runners.main import main
    main()
except Exception as e:
    with open("crash.txt", "w") as f:
        traceback.print_exc(file=f)
